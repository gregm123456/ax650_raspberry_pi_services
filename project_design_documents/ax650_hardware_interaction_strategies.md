# AX650/LLM8850 Hardware Interaction Strategies for API Services

**Project Context**: Building persistent API services for LLM chat completion and Stable Diffusion image generation on M5Stack AX650/LLM8850 PCIe accelerator running on Raspberry Pi 5.

**Date**: November 16, 2025  
**Status**: Analysis & Strategy Document

---

## Executive Summary

This document analyzes the AXCL (Axera Compute Library) SDK to determine optimal hardware interaction strategies for implementing persistent API services on the M5Stack AX650/LLM8850 PCIe accelerator. The analysis is based on official SDK examples, API documentation, and system management tools.

**Key Findings**:
1. **Two-tier API Architecture**: AXCL provides both Runtime API (for NPU/compute) and Native API (for media codecs)
2. **Python Bindings Available**: `pyaxcl` package provides Python wrappers for both Runtime and Native APIs
3. **System Management Tools**: `axcl-smi` provides comprehensive device monitoring and health checking
4. **Memory Management**: Explicit device memory allocation with cached/non-cached options
5. **Model Persistence**: Runtime Engine supports keeping models loaded in memory

---

## 1. Hardware Architecture Understanding

### 1.1 Device Type & Constraints

**Critical Reality Check**:
- **NOT a development board** — it's an M.2 PCIe accelerator card
- Requires **AXCL runtime**, not standard SDK used for on-board deployments
- Binary variants exist: `main_ax650` (on-device) vs `main_axcl_aarch64` (M.2 card on ARM host)
- Must use AXCL-specific binaries and libraries

### 1.2 Memory Architecture

The AX650 has two distinct memory pools:

**System Memory (DRAM)**:
- ~945 MiB total on typical device
- Used for general system operations, buffers, and temporary storage
- Queryable via: `axcl_sample_runtime -d 0` → shows `total mem size` and `free mem size`

**CMM (Contiguous Memory Manager) - Media Memory**:
- ~7040 MiB total on typical device
- Used for model weights, inference I/O buffers, video frames
- **Critical for model persistence** — models loaded here stay resident
- Queryable via: `axcl-smi info --cmm -d 0`

**Practical Implications**:
- LLM models (e.g., Qwen3-4B INT8) require ~4GB+ CMM for weights + KV cache
- Stable Diffusion models require ~2-3GB CMM for UNet, VAE, text encoder
- Running both simultaneously may require model swapping based on available CMM

### 1.3 Device Identification

Devices are identified by **device index** (0, 1, 2...), not PCIe bus ID directly.

```bash
# Query all connected devices
axcl_sample_runtime -d -1  # -1 = traverse all devices

# Query specific device
axcl_sample_runtime -d 0   # Device index 0
```

**Bus ID Format**: `0001:01:00.0` (example from docs)

---

## 2. AXCL SDK Architecture Analysis

### 2.1 API Layers

```
┌─────────────────────────────────────────┐
│  Application (Python/C++)               │
├─────────────────────────────────────────┤
│  libaxcl_ppl.so (Pipeline abstraction)  │  ← High-level, e.g., transcode
├─────────────────────────────────────────┤
│  libaxcl_lite.so (Helper utilities)     │  ← Optional convenience layer
├─────────────────────────────────────────┤
│  AXCL Runtime API                       │  ← NPU inference, memory
│  - axclrt* (device, context, memory)    │
│  - axclrtEngine* (model loading, exec)  │
├─────────────────────────────────────────┤
│  AXCL Native API                        │  ← Video/Image processing
│  - AXCL_SYS (system, memory pools)      │
│  - AXCL_VDEC/VENC (video codecs)        │
│  - AXCL_IVPS (image processing)         │
│  - AXCL_IVE (computer vision)           │
└─────────────────────────────────────────┘
```

### 2.2 Runtime API — For NPU & Model Execution

**Initialization Flow** (from `axcl_sample_runtime`):
```c
1. axclInit(config)                    // System init with optional JSON config
2. axclrtSetDevice(deviceId)           // Activate device, creates default context
3. axclrtCreateContext(&context, id)   // (Optional) Create explicit contexts for threads
4. /* Do work */
5. axclrtDestroyContext(context)       // Clean up explicit contexts
6. axclrtResetDevice(deviceId)         // Deactivate device, release resources
7. axclFinalize()                      // System cleanup
```

**Key Functions for Our Use Case**:

| Function | Purpose | Notes |
|----------|---------|-------|
| `axclrtMalloc()` | Allocate device memory (non-cached) | For model I/O buffers |
| `axclrtMallocCached()` | Allocate device memory (cached) | Requires flush/invalidate |
| `axclrtFree()` | Free device memory | Must match allocation type |
| `axclrtMemcpy()` | Copy memory (Host↔Device, Device↔Device) | Multiple direction modes |
| `axclrtEngineLoadFromFile()` | Load model from `.axmodel` file | Returns `modelId` |
| `axclrtEngineCreateIO()` | Create I/O structure for inference | Wraps input/output buffers |
| `axclrtEngineExecute()` | Synchronous inference | Blocks until complete |
| `axclrtEngineExecuteAsync()` | Asynchronous inference | Requires stream management |

**Model Lifecycle**:
```c
// Load model once at service startup
uint64_t modelId;
axclrtEngineLoadFromFile("model.axmodel", &modelId);

// Get I/O metadata
axclrtEngineIOInfo ioInfo;
axclrtEngineGetIOInfo(modelId, &ioInfo);
uint32_t inputCount = axclrtEngineGetNumInputs(ioInfo);
uint32_t outputCount = axclrtEngineGetNumOutputs(ioInfo);

// Create I/O structure
axclrtEngineIO io;
axclrtEngineCreateIO(ioInfo, &io);

// Allocate buffers ONCE, reuse across requests
void* inputBuffer;
axclrtMalloc(&inputBuffer, inputSize, policy);
axclrtEngineSetInputBufferByIndex(io, 0, inputBuffer, inputSize);

// Run inference (many times)
axclrtEngineExecute(modelId, contextId, 0, io);

// Cleanup when service stops
axclrtFree(inputBuffer);
axclrtEngineDestroyIO(io);
axclrtEngineUnload(modelId);
```

**Critical for Goal 3 (Model Persistence)**:
- Models stay loaded in CMM memory until `axclrtEngineUnload()` is called
- Buffers allocated with `axclrtMalloc()` persist until `axclrtFree()` is called
- No automatic unloading — **perfect for our use case!**

### 2.3 Native API — For Video/Image Processing

**Not directly needed for LLM**, but **critical for Stable Diffusion** if we need to:
- Decode input images (AXCL_VDEC)
- Resize/crop images (AXCL_IVPS)
- Encode output images to JPEG (AXCL_JENC)

**Key Difference from Runtime API**:
- Function names: `AXCL_*` instead of `axclrt*`
- Example: `AXCL_SYS_Init()`, `AXCL_IVPS_CreateGrp()`
- Requires explicit pool management for video frames

**For Stable Diffusion**:
- Input: Text prompt (no Native API needed, pure NPU)
- Output: Raw tensor → need to convert to PNG/JPEG
  - Option A: Use AXCL_JENC (Native API)
  - Option B: Copy to host, use PIL/OpenCV (simpler for Python)

---

## 3. Device Monitoring & Health Management

### 3.1 AXCL-SMI Tool — System Management Interface

**Primary tool for Goal 4 (Device Monitoring)**

**Basic Device Query**:
```bash
axcl-smi              # Show all devices with summary
axcl-smi -d 0         # Show device 0 only
```

**Output Example**:
```
+------------------------------------------------------------------------------------------------+
| AXCL-SMI  V3.6.4_20250805020145                                  Driver  V3.6.4_20250805020145 |
+-----------------------------------------+--------------+---------------------------------------+
| Card  Name                     Firmware                                                          | Bus-Id       | Memory-Usage           |
| Fan   Temp                Pwr:Usage/Cap                                                          | CPU      NPU | CMM-Usage              |
|=========================================+==============+=======================================|
| 0  AX650N                     V3.6.4                                                             | 0001:01:00.0 | 149 MiB /      945 MiB |
| --   41C                      -- / --                                                            | 1%        0% | 18 MiB /     7040 MiB  |
+-----------------------------------------+--------------+---------------------------------------+
```

**Parsed Metrics**:
- **Temperature**: `41C` (41°C) — **critical safety threshold: likely 80-85°C**
- **CPU Utilization**: `1%` (average)
- **NPU Utilization**: `0%` (average)
- **System Memory**: `149 MiB / 945 MiB` used
- **CMM Memory**: `18 MiB / 7040 MiB` used

**Detailed Queries**:
```bash
# Temperature only
axcl-smi info --temp -d 0
# Output: temperature: 49263  (49.263°C in millidegrees)

# Memory usage
axcl-smi info --mem -d 0
# Output: total mem size: 968356 KB, free mem size: 815084 KB

# CMM usage
axcl-smi info --cmm -d 0
# Output: CMM Total: 7208960 KiB, CMM Used: 18876 KiB

# CPU utilization
axcl-smi info --cpu -d 0

# NPU utilization  
axcl-smi info --npu -d 0
```

**Process Monitoring**:
```bash
# List processes using device
axcl-smi       # Bottom section shows PID, process name, NPU memory usage
```

### 3.2 Programmatic Device Health Checks

**From C++ (axcl_sample_runtime.cpp pattern)**:
```cpp
axclrtDeviceProperties properties;
axclrtGetDeviceProperties(deviceId, &properties);

// Check fields:
properties.temperature    // In millidegrees Celsius
properties.totalMemSize   // Total system memory in KB
properties.freeMemSize    // Free system memory in KB
properties.totalCmmSize   // Total CMM in KB
properties.freeCmmSize    // Free CMM in KB
properties.cpuLoading     // CPU usage percentage
properties.npuLoading     // NPU usage percentage
```

**Python Equivalent** (via pyaxcl):
```python
from axcl.rt import axcl_rt

# Initialize
axcl_rt.axclInit(config_path)
axcl_rt.axclrtSetDevice(0)

# Query device properties
props = axcl_rt.axclrtDeviceProperties()
axcl_rt.axclrtGetDeviceProperties(0, props)

temp_celsius = props.temperature / 1000.0
cpu_pct = props.cpuLoading
npu_pct = props.npuLoading
free_cmm_mb = props.freeCmmSize / 1024
```

### 3.3 Device Reset & Recovery

**Software Reset**:
```bash
# Reboot device (firmware reload)
axcl-smi reboot -d 0
```

**From Code**:
```cpp
// Force device panic and reboot (emergency recovery)
// This is shown in axcl_sample_runtime --reboot example
// Internal implementation likely sends panic trigger to device
```

**For Production Services**:
- Monitor temperature every 5-10 seconds
- If temp > 75°C: Log warning, reduce load
- If temp > 80°C: Gracefully shutdown inference, wait for cooldown
- If device becomes unresponsive (inference timeout): Call `axcl-smi reboot`
- After reboot: Reinitialize, reload models

---

## 4. Python Integration Strategies

### 4.1 PyAXCL Package Analysis

**Location**: `reference_projects_and_documentation/pyaxcl/`

**Structure**:
```
pyaxcl/
├── setup.py                    # Install with: pip install .
├── axcl/
│   ├── __init__.py
│   ├── axcl_base.py
│   ├── rt/                     # Runtime API wrappers
│   │   ├── axcl_rt.py          # Core runtime functions
│   │   ├── axcl_rt_device.py   # Device management
│   │   ├── axcl_rt_memory.py   # Memory allocation
│   │   ├── axcl_rt_engine.py   # Model execution
│   ├── npu/                    # NPU-specific
│   ├── ivps/                   # Image processing
│   ├── vdec/                   # Video decoder
│   ├── venc/                   # Video encoder
```

**Sample Code** (from `sample/runtime/sample_runtime.py`):
```python
from axcl.rt import axcl_rt

# Init
ret = axcl_rt.axclInit(None)
ret = axcl_rt.axclrtSetDevice(device_id)

# Allocate memory
dev_ptr = axcl_rt.axclrtMalloc(size, axcl_rt.AXCL_MEM_MALLOC_NORMAL_ONLY)

# Copy data
ret = axcl_rt.axclrtMemcpy(
    dev_ptr, 
    host_data,
    size,
    axcl_rt.AXCL_MEMCPY_HOST_TO_DEVICE
)

# Free memory
axcl_rt.axclrtFree(dev_ptr)

# Cleanup
axcl_rt.axclrtResetDevice(device_id)
axcl_rt.axclFinalize()
```

### 4.2 PyAXEngine Package (Alternative)

**Location**: `reference_projects_and_documentation/PyAXEngine/axengine-0.1.3-py3-none-any.whl`

**From Stable Diffusion examples** (`sd1.5-lcm.axera/python/`):
```python
import axengine

# Load model
session = axengine.InferenceSession(
    model_path="model.axmodel",
    device_id=0
)

# Get I/O info
input_name = session.get_inputs()[0].name
output_name = session.get_outputs()[0].name

# Run inference
outputs = session.run(
    None,  # output names (None = all)
    {input_name: input_array}
)
```

**Comparison**:

| Feature | pyaxcl | PyAXEngine |
|---------|--------|------------|
| API Style | Low-level, explicit | High-level, Pythonic |
| Memory Control | Manual (axclrtMalloc/Free) | Automatic |
| Flexibility | Full access to all APIs | NPU inference only |
| Learning Curve | Steeper (C-like) | Gentler (like ONNX Runtime) |

**Recommendation for Project**:
- **LLM Service**: Use **PyAXEngine** for simpler code, unless need precise control
- **Stable Diffusion Service**: Use **PyAXEngine** (proven in examples)
- **Device Monitoring**: Use **subprocess** to call `axcl-smi` commands

### 4.3 Running Shell Commands from Python

**For Device Monitoring**:
```python
import subprocess
import json
import re

def get_device_temperature(device_id=0):
    """Get temperature in Celsius"""
    cmd = f"axcl-smi info --temp -d {device_id}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    # Parse output: "temperature     : 49263"
    match = re.search(r'temperature\s*:\s*(\d+)', result.stdout)
    if match:
        temp_millidegrees = int(match.group(1))
        return temp_millidegrees / 1000.0
    return None

def get_cmm_usage(device_id=0):
    """Get CMM memory usage in MB"""
    cmd = f"axcl-smi info --cmm -d {device_id}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    # Parse: "CMM Used : 18876 KiB"
    match = re.search(r'CMM Used\s*:\s*(\d+)\s*KiB', result.stdout)
    if match:
        return int(match.group(1)) / 1024  # Convert to MB
    return None

def check_device_health(device_id=0, temp_threshold=75.0):
    """Monitor device health"""
    temp = get_device_temperature(device_id)
    cmm_mb = get_cmm_usage(device_id)
    
    health = {
        'temperature_c': temp,
        'cmm_used_mb': cmm_mb,
        'status': 'ok'
    }
    
    if temp and temp > temp_threshold:
        health['status'] = 'warning'
        health['reason'] = f'Temperature {temp}°C exceeds threshold'
    
    return health
```

**For Emergency Device Reset**:
```python
def reset_device(device_id=0):
    """Reset device (use with caution!)"""
    cmd = f"echo y | axcl-smi reboot -d {device_id}"
    subprocess.run(cmd, shell=True, check=True)
```

---

## 5. Implementation Patterns for Our Services

### 5.1 LLM Chat Completion Service Architecture

**Service Lifecycle**:
```
┌─────────────────────────────────────────────────┐
│ FastAPI Server Startup                          │
├─────────────────────────────────────────────────┤
│ 1. axcl_rt.axclInit()                           │
│ 2. axcl_rt.axclrtSetDevice(0)                   │
│ 3. Load Qwen3-4B model → modelId               │
│ 4. Allocate I/O buffers (persist in CMM)       │
│ 5. Load tokenizer (transformers library)       │
├─────────────────────────────────────────────────┤
│ Request Handler (per chat completion request)  │
├─────────────────────────────────────────────────┤
│ 1. Tokenize input text → token IDs             │
│ 2. Copy token IDs to input buffer              │
│ 3. Run inference (prefill + decode loop)       │
│ 4. Decode output tokens → text                 │
│ 5. Stream or return complete response          │
├─────────────────────────────────────────────────┤
│ Background Thread: Device Health Monitor       │
├─────────────────────────────────────────────────┤
│ - Every 10s: Check temperature, memory          │
│ - If unhealthy: Log warning, pause requests     │
│ - If critical: Attempt device reset             │
├─────────────────────────────────────────────────┤
│ Server Shutdown                                 │
├─────────────────────────────────────────────────┤
│ 1. Free buffers                                 │
│ 2. Unload model                                 │
│ 3. axclrtResetDevice(0)                         │
│ 4. axclFinalize()                               │
└─────────────────────────────────────────────────┘
```

**Code Skeleton**:
```python
from fastapi import FastAPI
from contextlib import asynccontextmanager
import axengine
from transformers import AutoTokenizer
import threading
import time

# Global state
model_session = None
tokenizer = None
device_monitor_thread = None
shutdown_flag = False

def monitor_device_health():
    """Background thread to monitor device"""
    global shutdown_flag
    while not shutdown_flag:
        health = check_device_health(device_id=0)
        if health['status'] != 'ok':
            logging.warning(f"Device health issue: {health}")
            # Could pause request handling here
        time.sleep(10)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global model_session, tokenizer, device_monitor_thread, shutdown_flag
    
    # Startup
    logging.info("Loading model...")
    model_session = axengine.InferenceSession(
        "reference_projects_and_documentation/Qwen3-4B/qwen3-4b-ax650/",
        device_id=0
    )
    
    tokenizer = AutoTokenizer.from_pretrained(
        "reference_projects_and_documentation/Qwen3-4B/qwen3_tokenizer/"
    )
    
    # Start health monitor
    device_monitor_thread = threading.Thread(target=monitor_device_health, daemon=True)
    device_monitor_thread.start()
    
    logging.info("Model loaded, ready for requests")
    
    yield  # Server runs here
    
    # Shutdown
    shutdown_flag = True
    device_monitor_thread.join(timeout=5)
    model_session = None
    logging.info("Cleanup complete")

app = FastAPI(lifespan=lifespan)

@app.post("/v1/chat/completions")
async def chat_completion(request: ChatCompletionRequest):
    # Tokenize
    tokens = tokenizer.encode(request.messages[-1].content)
    
    # Run inference (simplified)
    # Real implementation needs prefill + decode loop with KV cache
    outputs = model_session.run(None, {"input_ids": tokens})
    
    # Decode
    response_text = tokenizer.decode(outputs[0])
    
    return ChatCompletionResponse(
        choices=[Choice(message=Message(content=response_text))]
    )
```

### 5.2 Stable Diffusion Service Architecture

**Service Lifecycle**:
```
┌─────────────────────────────────────────────────┐
│ FastAPI Server Startup                          │
├─────────────────────────────────────────────────┤
│ 1. axcl_rt.axclInit()                           │
│ 2. axcl_rt.axclrtSetDevice(0)                   │
│ 3. Load text_encoder.axmodel → session1        │
│ 4. Load unet.axmodel → session2                │
│ 5. Load vae_decoder.axmodel → session3         │
│ 6. Load tokenizer (CLIPTokenizer)              │
├─────────────────────────────────────────────────┤
│ Request Handler (per image generation)         │
├─────────────────────────────────────────────────┤
│ 1. Tokenize prompt → clip tokens               │
│ 2. Run text_encoder → text embeddings          │
│ 3. Generate random latents                     │
│ 4. For each denoising step:                    │
│    - Run unet(latents, timestep, embeddings)   │
│    - Update latents                            │
│ 5. Run vae_decoder(final_latents) → image      │
│ 6. Convert to PNG/JPEG, return                 │
└─────────────────────────────────────────────────┘
```

**Code Skeleton**:
```python
import axengine
from transformers import CLIPTokenizer
import numpy as np
from PIL import Image

# Global state
text_encoder_session = None
unet_session = None
vae_session = None
tokenizer = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global text_encoder_session, unet_session, vae_session, tokenizer
    
    # Startup
    logging.info("Loading Stable Diffusion models...")
    
    text_encoder_session = axengine.InferenceSession(
        "models/text_encoder.axmodel", device_id=0
    )
    unet_session = axengine.InferenceSession(
        "models/unet.axmodel", device_id=0
    )
    vae_session = axengine.InferenceSession(
        "models/vae_decoder.axmodel", device_id=0
    )
    
    tokenizer = CLIPTokenizer.from_pretrained("models/tokenizer/")
    
    logging.info("All models loaded")
    yield
    
    # Shutdown
    text_encoder_session = None
    unet_session = None
    vae_session = None

app = FastAPI(lifespan=lifespan)

@app.post("/sdapi/v1/txt2img")
async def text_to_image(request: Txt2ImgRequest):
    # Encode prompt
    tokens = tokenizer(request.prompt, return_tensors="np")
    text_embeddings = text_encoder_session.run(None, tokens.input_ids)[0]
    
    # Initialize latents
    latents = np.random.randn(1, 4, 64, 64).astype(np.float32)
    
    # Denoising loop
    for t in range(request.steps):
        timestep = get_timestep(t, request.steps)
        noise_pred = unet_session.run(None, {
            "latents": latents,
            "timestep": timestep,
            "text_embeddings": text_embeddings
        })[0]
        latents = update_latents(latents, noise_pred, timestep)
    
    # Decode
    image_array = vae_session.run(None, {"latents": latents})[0]
    
    # Convert to PIL Image
    image = array_to_pil(image_array)
    
    # Return as base64 or save to file
    return {"image": image_to_base64(image)}
```

---

## 6. Best Practices & Recommendations

### 6.1 Memory Management

**DO**:
- ✅ Allocate model buffers once at startup, reuse across requests
- ✅ Use `axclrtMalloc()` for non-cached buffers (faster)
- ✅ Monitor CMM usage — if running low, consider model swapping
- ✅ Keep per-request data (like input tokens) small, allocate/free quickly

**DON'T**:
- ❌ Allocate/free large buffers per request (performance killer)
- ❌ Use cached memory (`axclrtMallocCached`) unless explicitly needed
- ❌ Mix `axclrtMalloc()` with wrong `axclrtFree()` variant

### 6.2 Device Initialization

**DO**:
- ✅ Call `axclInit()` exactly once per process
- ✅ Handle cleanup in signal handlers (SIGINT, SIGTERM)
- ✅ Always call `axclrtResetDevice()` before process exit
- ✅ Use context managers (`@asynccontextmanager`) for FastAPI lifespan

**DON'T**:
- ❌ Call `axclInit()` multiple times
- ❌ Exit without calling `axclFinalize()` (can cause driver issues)
- ❌ Rely on Python `__del__` for cleanup (unreliable)

### 6.3 Error Handling

**DO**:
- ✅ Check return codes: `ret == AXCL_SUCC (0)` means success
- ✅ Log device properties on startup for debugging
- ✅ Implement request timeouts (e.g., 30s for inference)
- ✅ Gracefully degrade if device is unhealthy

**DON'T**:
- ❌ Ignore AXCL error codes (can mask critical failures)
- ❌ Let inference run indefinitely without timeout
- ❌ Crash the service on device errors (try recovery first)

### 6.4 Multi-Client Handling

**Critical Issue from Submodule Overview**:
> The C++ server maintains ONE SINGLE GLOBAL CONVERSATION STATE. It does NOT support multiple independent client conversations.

**Solutions**:

**Option A: Session Management in Python Wrapper**
- Wrap C++ binary with Python FastAPI
- Maintain session state in Python (conversation history per client)
- Call `/api/reset` between different clients
- Use locks to serialize requests

**Option B: Pure Python Implementation**
- Use PyAXEngine for model execution
- Implement KV cache management in Python
- Full control over per-client state
- May sacrifice some performance vs C++ implementation

**Recommendation**: **Option B** (Pure Python) for better multi-client support

### 6.5 Device Monitoring Integration

**Monitoring Cadence**:
```python
# Background thread
while True:
    health = {
        'temp': get_device_temperature(0),
        'cmm_mb': get_cmm_usage(0),
        'timestamp': time.time()
    }
    
    # Store in time-series (e.g., Prometheus, or simple deque)
    metrics_buffer.append(health)
    
    # Check thresholds
    if health['temp'] > 75:
        logging.warning("High temperature warning")
        # Could throttle requests here
    
    if health['temp'] > 80:
        logging.error("Critical temperature, pausing service")
        pause_request_handling()
        
    time.sleep(10)  # Check every 10 seconds
```

**Expose Metrics Endpoint**:
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy" if device_healthy else "degraded",
        "temperature_c": latest_temp,
        "cmm_used_mb": latest_cmm,
        "model_loaded": model_session is not None
    }
```

---

## 7. Recommended Implementation Path

Based on this analysis, here's the recommended path forward for the project:

### Phase 1: Infrastructure Setup
1. Install pyaxcl: `pip install reference_projects_and_documentation/pyaxcl/`
2. Install PyAXEngine: `pip install reference_projects_and_documentation/PyAXEngine/axengine-0.1.3-py3-none-any.whl`
3. Verify device access: `axcl-smi -d 0`
4. Test basic inference with example scripts

### Phase 2: LLM Chat Completion Service
1. **Use PyAXEngine** for model loading and inference
2. **Use transformers** for tokenization (no separate tokenizer service needed)
3. Implement FastAPI with lifespan management
4. Add session management for multi-client support
5. Implement device health monitoring thread
6. Add OpenAI-compatible API endpoints

**Estimated Effort**: 2-3 weeks for MVP

### Phase 3: Stable Diffusion Service
1. Load SD 1.5 LCM models from `sd1.5-lcm.axera/`
2. Use PyAXEngine for text_encoder, unet, vae_decoder
3. Implement denoising loop in Python
4. Add Automatic1111-compatible API endpoints
5. Reuse device monitoring from Phase 2

**Estimated Effort**: 1-2 weeks (building on Phase 2 infrastructure)

### Phase 4: Production Hardening
1. Add systemd service files for auto-start
2. Implement request queuing for fairness
3. Add Prometheus metrics export
4. Create healthcheck scripts for monitoring
5. Document deployment on Raspberry Pi 5

**Estimated Effort**: 1 week

---

## 8. Reference Commands Cheat Sheet

```bash
# Device Info
axcl-smi -d 0                        # Show device 0 summary
axcl-smi info --temp -d 0            # Temperature
axcl-smi info --cmm -d 0             # CMM memory usage
axcl-smi info --cpu -d 0             # CPU utilization
axcl-smi info --npu -d 0             # NPU utilization

# Process Info
axcl-smi proc --vdec -d 0            # Video decoder status
axcl-smi proc --venc -d 0            # Video encoder status
axcl-smi proc --pool -d 0            # Memory pool status
axcl-smi proc --cmm -d 0             # Detailed CMM info

# Device Management
axcl-smi reboot -d 0                 # Reboot device
axcl-smi set -f 1700000 -d 0         # Set CPU freq to 1.7GHz
axcl-smi log -d 0 -o ./logs/         # Download device logs

# Shell Commands on Device
axcl-smi sh "cat /proc/ax_proc/mem_cmm_info" -d 0
axcl-smi sh "cat /proc/ax_proc/link_table" -d 0
```

---

## 9. Open Questions & Next Steps

### Questions to Investigate
1. **KV Cache Management**: How to implement efficient KV cache for LLM in Python?
   - Check if Qwen3-4B examples include KV cache handling
   - May need to study `ax-llm/src/runner/LLM.hpp` for patterns

2. **Concurrent Inference**: Can we run text_encoder while unet is running?
   - Test if NPU can handle parallel models
   - May need separate contexts per model

3. **Memory Limits**: Exact CMM requirements for both services running simultaneously
   - Load both sets of models and measure actual CMM usage
   - Determine if model swapping is needed

### Immediate Next Steps
1. ✅ Document hardware interaction strategies (this document)
2. ⬜ Set up development environment on Raspberry Pi 5
3. ⬜ Test basic inference with PyAXEngine
4. ⬜ Create minimal FastAPI skeleton
5. ⬜ Implement device health monitoring
6. ⬜ Build LLM service MVP
7. ⬜ Build SD service MVP

---

## 10. Conclusion

The AXCL SDK provides a comprehensive, production-ready framework for building persistent AI services on the AX650/LLM8850 accelerator. Key advantages:

✅ **Model Persistence**: Models stay loaded in CMM until explicitly unloaded  
✅ **Python Support**: PyAXEngine provides clean, high-level API  
✅ **Device Monitoring**: axcl-smi and Runtime API enable comprehensive health checks  
✅ **Memory Control**: Explicit allocation allows efficient buffer reuse  
✅ **Multi-Model Support**: Can load multiple models simultaneously (if CMM permits)

The primary challenge is adapting demo code (designed for one-shot CLI usage) into persistent service architecture, but the SDK primitives fully support our use case.

**Confidence Level**: High — the SDK examples and API documentation provide clear paths to implement both LLM and Stable Diffusion services meeting all project goals.
