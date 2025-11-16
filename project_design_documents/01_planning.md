# Phase 1: Planning - AX650 LLM Chat Completion Service

**Project**: Persistent LLM Chat Completion API for M5Stack AX650/LLM8850 PCIe Accelerator  
**Target Platform**: Raspberry Pi 5 + AX650 PCIe card  
**Date**: November 16, 2025  
**Status**: Phase 1 - Planning Mode

---

## Executive Summary

This planning document outlines the development of a production-ready, OpenAI-compatible chat completion API service running on the M5Stack AX650/LLM8850 PCIe accelerator. The service will provide persistent model hosting with fast inference (<3s for 100 tokens) suitable for interactive art installations and other real-time applications.

**Core Principle**: Build a minimal but robust MVP using proven Python tools (PyAXEngine, FastAPI) before adding complexity.

---

## 1. Project Scope & Objectives

### 1.1 Primary Goal
Deliver a **reliable, persistent LLM chat-completion HTTP service** that:
- Keeps models loaded in device memory (no cold starts)
- Provides OpenAI-compatible API endpoints
- Supports stateless request handling (client manages conversation state)
- Runs unattended for 24+ hours
- Responds in <3 seconds for typical interactive use cases

### 1.2 Success Criteria

**Must Achieve**:
1. ✅ **Drop-in Replacement**: Existing projects (coyote_interactive) work with <10 lines of code change
2. ✅ **Performance**: 95% of requests complete in <3s (100-token responses)
3. ✅ **Reliability**: Service runs 24+ hours without manual intervention
4. ✅ **Compatibility**: Works with standard `openai` Python client library
5. ✅ **Context Support**: Handles 2048+ token conversations

**Verification Test**: Run coyote_interactive demo for 1 hour with AX650 service, verify all button interactions work with natural response times.

### 1.3 Explicit Non-Goals (MVP Phase)

- ❌ Multi-model dynamic loading/swapping (single model only initially)
- ❌ Server-side conversation session management (stateless only)
- ❌ Advanced KV cache persistence across requests
- ❌ High-concurrency optimization (>5 simultaneous requests)
- ❌ Streaming responses (blocking responses acceptable for MVP)
- ❌ Model fine-tuning or optimization
- ❌ Authentication/authorization (local network only)

---

## 2. Technical Architecture

### 2.1 Technology Stack

**Core Components**:
```
┌─────────────────────────────────────────┐
│  FastAPI HTTP Server                    │
│  - OpenAI-compatible endpoints          │
│  - Request validation & queuing         │
│  - Health monitoring                    │
├─────────────────────────────────────────┤
│  Inference Engine (PyAXEngine)          │
│  - axengine.InferenceSession            │
│  - Model loaded at startup              │
│  - Persistent buffer allocation         │
├─────────────────────────────────────────┤
│  Tokenizer (Transformers/Local)         │
│  - Qwen tokenizer                       │
│  - Encode/decode utilities              │
├─────────────────────────────────────────┤
│  Device Monitor (axcl-smi wrapper)      │
│  - Temperature tracking                 │
│  - Memory monitoring (CMM/System)       │
│  - NPU utilization                      │
├─────────────────────────────────────────┤
│  AX650 Hardware (via AXCL drivers)      │
│  - NPU compute                          │
│  - CMM memory (~7GB)                    │
│  - PCIe interface                       │
└─────────────────────────────────────────┘
```

**Python Dependencies**:
- `fastapi` - HTTP API framework
- `uvicorn` - ASGI server
- `pydantic` - Request/response validation
- `transformers` - Tokenizer support
- `PyAXEngine` - AX650 inference wrapper (wheel provided)
- `pyaxcl` - Low-level AXCL bindings (optional, for advanced monitoring)
- `openai` - For testing client compatibility

### 2.2 API Design

**Endpoint**: `POST /v1/chat/completions`

**Request Format** (OpenAI-compatible):
```json
{
  "model": "qwen3-4b-ax650",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
  ],
  "temperature": 0.9,
  "max_tokens": 125,
  "top_p": 0.95,
  "stop": null
}
```

**Response Format**:
```json
{
  "id": "chatcmpl-{uuid}",
  "object": "chat.completion",
  "created": 1732000000,
  "model": "qwen3-4b-ax650",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! How can I help you today?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 25,
    "completion_tokens": 12,
    "total_tokens": 37
  }
}
```

**Additional Endpoints**:
- `GET /health` - Service health check
- `GET /v1/models` - List available models
- `GET /metrics` - Prometheus-style metrics (optional)

### 2.3 Request Processing Flow

```
1. HTTP Request Received
   ↓
2. Validate Request Schema (Pydantic)
   ↓
3. Extract & Concatenate Messages → Prompt String
   ↓
4. Tokenize Prompt (transformers)
   ↓
5. Acquire NPU Lock (threading.Lock for MVP)
   ↓
6. Prepare Input Tensor (reuse pre-allocated buffer)
   ↓
7. Run Inference (session.run())
   ↓
8. Extract Output Tokens
   ↓
9. Release NPU Lock
   ↓
10. Detokenize → Response Text
    ↓
11. Format OpenAI Response
    ↓
12. Return JSON Response
```

**Concurrency Strategy (MVP)**:
- Single NPU worker with lock-based serialization
- Requests queued via FastAPI's default request handling
- No explicit queue management initially
- Future: Worker pool with configurable size

### 2.4 Memory Management

**CMM (Contiguous Memory Manager) Budget**:
- Total: ~7040 MiB
- Qwen3-4B INT8 model: ~4000 MiB (weights + runtime overhead)
- Input/output buffers: ~200 MiB
- KV cache reserve: ~500 MiB (future)
- Safety margin: ~2340 MiB free

**Buffer Allocation Strategy**:
```python
# At startup (pseudo-code)
session = axengine.InferenceSession(model_path, device_id=0)

# Get I/O shapes
input_shape = session.get_inputs()[0].shape  # e.g., (1, 2048)
output_shape = session.get_outputs()[0].shape

# Allocate buffers once, reuse across requests
input_buffer = np.zeros(input_shape, dtype=np.int64)
output_buffer = np.zeros(output_shape, dtype=np.float32)
```

**Memory Monitoring**:
- Poll `axcl-smi info --cmm` every 10 seconds
- Log warning if free CMM < 1GB
- Reject requests if free CMM < 500MB

---

## 3. Device Health Monitoring

### 3.1 Monitoring Strategy

**Metrics to Track**:
1. **Temperature** (critical)
   - Poll: Every 5 seconds
   - Thresholds:
     - Normal: <70°C
     - Warning: 70-75°C (log warning)
     - Caution: 75-80°C (log error, reduce load)
     - Critical: >80°C (pause requests, initiate cooldown)
     - Emergency: >85°C (attempt device reset)

2. **Memory (CMM)**
   - Poll: Every 10 seconds
   - Thresholds:
     - Healthy: >2GB free
     - Warning: 1-2GB free
     - Critical: <1GB free (reject new requests)

3. **NPU Utilization**
   - Poll: Every 10 seconds
   - Expected: 0-100% (spikes during inference)
   - Use for metrics/logging only (not throttling)

**Implementation**:
```python
# Background thread
async def device_monitor():
    while True:
        try:
            temp = get_device_temperature()
            cmm_free = get_cmm_free_memory()
            npu_util = get_npu_utilization()
            
            # Check thresholds and take action
            if temp > 80:
                logger.error(f"High temp: {temp}°C - pausing requests")
                pause_request_processing()
            
            if cmm_free < 1024:  # <1GB
                logger.warning(f"Low CMM: {cmm_free}MB")
        
        except Exception as e:
            logger.error(f"Monitor error: {e}")
        
        await asyncio.sleep(5)
```

### 3.2 Error Recovery

**Device Unresponsive**:
- Detect: Inference timeout (>30s with no response)
- Action 1: Log error, return 503 to client
- Action 2: If 3 consecutive timeouts, attempt device reset
- Action 3: Reload model after reset

**Memory Exhaustion**:
- Detect: CMM allocation failure
- Action: Return 503 error, log incident
- Future: Implement LRU cache eviction

**Thermal Throttling**:
- Detect: Temperature >80°C
- Action: Pause new requests, log warning
- Resume: When temperature <70°C

---

## 4. Implementation Phases

### Phase 0: Environment Setup & Validation (1-2 days)

**Objectives**:
- Verify hardware is accessible and functional
- Install all required dependencies
- Run reference examples to confirm drivers work

**Tasks**:
1. [ ] Install PyAXEngine wheel
   ```bash
   pip install reference_projects_and_documentation/PyAXEngine/axengine-0.1.3-py3-none-any.whl
   ```

2. [ ] Install pyaxcl (optional but recommended)
   ```bash
   cd reference_projects_and_documentation/pyaxcl
   pip install .
   ```

3. [ ] Install Python dependencies
   ```bash
   pip install fastapi uvicorn pydantic transformers safetensors openai
   ```

4. [ ] Verify device access
   ```bash
   axcl-smi
   axcl-smi info --cmm -d 0
   axcl-smi info --temp -d 0
   ```

5. [ ] Run PyAXEngine example
   ```bash
   # Test with Stable Diffusion example if available
   cd reference_projects_and_documentation/sd1.5-lcm.axera/python
   python run.py  # Verify inference works
   ```

6. [ ] Locate Qwen3-4B model files
   ```bash
   ls reference_projects_and_documentation/Qwen3-4B/
   # Confirm .axmodel file exists
   ```

7. [ ] Test tokenizer loading
   ```python
   from transformers import AutoTokenizer
   tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen-7B")
   # Or use local tokenizer from reference project
   ```

**Deliverable**: Documented verification that all components work independently.

---

### Phase 1: Minimal FastAPI Service (3-5 days)

**Objectives**:
- Create basic HTTP service skeleton
- Load model at startup and keep resident
- Implement single-request inference pipeline
- Verify OpenAI client compatibility

**Tasks**:

**1.1 Project Structure** (0.5 days)
```
qwen3-4b-chat-completion-service/
├── main.py                 # FastAPI app entry point
├── config.py               # Configuration (model paths, device ID, etc.)
├── models.py               # Pydantic request/response models
├── inference.py            # Inference engine wrapper
├── tokenizer_utils.py      # Tokenization helpers
├── device_monitor.py       # Health monitoring (stub initially)
├── requirements.txt        # Python dependencies
└── README.md              # Setup and usage instructions
```

**1.2 Configuration Module** (0.5 days)
```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Device
    DEVICE_ID: int = 0
    
    # Model
    MODEL_PATH: str = "../reference_projects_and_documentation/Qwen3-4B/qwen3-4b.axmodel"
    TOKENIZER_PATH: str = "../reference_projects_and_documentation/Qwen3-4B/"
    MODEL_NAME: str = "qwen3-4b-ax650"
    
    # Inference
    MAX_CONTEXT_LENGTH: int = 2048
    DEFAULT_MAX_TOKENS: int = 100
    DEFAULT_TEMPERATURE: float = 0.9
    DEFAULT_TOP_P: float = 0.95
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Monitoring
    MONITOR_INTERVAL_SEC: int = 10
    TEMP_WARNING_C: int = 70
    TEMP_CRITICAL_C: int = 80
    MIN_FREE_CMM_MB: int = 1024

settings = Settings()
```

**1.3 Request/Response Models** (0.5 days)
```python
# models.py
from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = 0.9
    max_tokens: Optional[int] = 100
    top_p: Optional[float] = 0.95
    stop: Optional[List[str]] = None

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[dict]
    usage: dict
```

**1.4 Inference Engine** (1.5 days)
```python
# inference.py
import axengine
import numpy as np
from threading import Lock

class InferenceEngine:
    def __init__(self, model_path: str, device_id: int = 0):
        self.session = axengine.InferenceSession(model_path, device_id)
        self.lock = Lock()  # Single NPU serialization
        
        # Get I/O metadata
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name
        
    def generate(self, input_ids: np.ndarray, max_tokens: int) -> np.ndarray:
        """Run inference with NPU lock."""
        with self.lock:
            # Prepare input
            inputs = {self.input_name: input_ids}
            
            # Run inference
            outputs = self.session.run(None, inputs)
            
            # Extract output tokens
            output_ids = outputs[0]
            
        return output_ids
```

**1.5 FastAPI Application** (1.5 days)
```python
# main.py
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import uvicorn
import uuid
import time

from models import ChatCompletionRequest, ChatCompletionResponse
from inference import InferenceEngine
from tokenizer_utils import load_tokenizer, messages_to_prompt
from config import settings

# Global state
engine = None
tokenizer = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle."""
    global engine, tokenizer
    
    # Startup
    print("Loading model...")
    engine = InferenceEngine(settings.MODEL_PATH, settings.DEVICE_ID)
    
    print("Loading tokenizer...")
    tokenizer = load_tokenizer(settings.TOKENIZER_PATH)
    
    print("Service ready!")
    
    yield
    
    # Shutdown
    print("Shutting down...")
    del engine
    del tokenizer

app = FastAPI(title="AX650 Chat Completion API", lifespan=lifespan)

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """OpenAI-compatible chat completion endpoint."""
    
    # Convert messages to prompt
    prompt = messages_to_prompt(request.messages, tokenizer)
    
    # Tokenize
    input_ids = tokenizer.encode(prompt, return_tensors="np")
    
    # Check context length
    if input_ids.shape[1] > settings.MAX_CONTEXT_LENGTH:
        raise HTTPException(400, "Prompt exceeds max context length")
    
    # Generate
    try:
        output_ids = engine.generate(input_ids, request.max_tokens)
        output_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    except Exception as e:
        raise HTTPException(500, f"Inference failed: {e}")
    
    # Format response
    return ChatCompletionResponse(
        id=f"chatcmpl-{uuid.uuid4().hex[:8]}",
        created=int(time.time()),
        model=request.model,
        choices=[{
            "index": 0,
            "message": {"role": "assistant", "content": output_text},
            "finish_reason": "stop"
        }],
        usage={
            "prompt_tokens": input_ids.shape[1],
            "completion_tokens": len(output_ids[0]),
            "total_tokens": input_ids.shape[1] + len(output_ids[0])
        }
    )

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "model": settings.MODEL_NAME}

if __name__ == "__main__":
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
```

**1.6 Testing** (0.5 days)

Test with OpenAI client:
```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="not-needed"
)

response = client.chat.completions.create(
    model="qwen3-4b-ax650",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is 2+2?"}
    ],
    max_tokens=50
)

print(response.choices[0].message.content)
```

**Deliverable**: Working HTTP service that responds to chat completion requests.

---

### Phase 2: Device Monitoring & Hardening (2-3 days)

**Objectives**:
- Implement background device health monitoring
- Add proper error handling and recovery
- Create metrics endpoint
- Test long-running stability

**Tasks**:

**2.1 Device Monitor Implementation** (1 day)
```python
# device_monitor.py
import subprocess
import asyncio
import logging
from dataclasses import dataclass

@dataclass
class DeviceStatus:
    temperature_c: float
    cmm_free_mb: int
    cmm_total_mb: int
    npu_util_pct: int
    system_mem_free_mb: int

class DeviceMonitor:
    def __init__(self, device_id: int = 0):
        self.device_id = device_id
        self.status = None
        self.paused = False
        
    def get_temperature(self) -> float:
        """Parse axcl-smi temp output."""
        result = subprocess.run(
            ["axcl-smi", "info", "--temp", "-d", str(self.device_id)],
            capture_output=True, text=True
        )
        # Parse: "temperature: 49263" (millidegrees)
        temp_str = result.stdout.strip().split(":")[1].strip()
        return float(temp_str) / 1000.0
    
    def get_cmm_info(self) -> tuple[int, int]:
        """Parse CMM total/free in MB."""
        result = subprocess.run(
            ["axcl-smi", "info", "--cmm", "-d", str(self.device_id)],
            capture_output=True, text=True
        )
        # Parse: "CMM Total: 7208960 KiB, CMM Used: 18876 KiB"
        # ... parsing logic
        return total_mb, free_mb
    
    async def monitor_loop(self):
        """Background monitoring task."""
        while True:
            try:
                self.status = DeviceStatus(
                    temperature_c=self.get_temperature(),
                    # ... other metrics
                )
                
                # Check thresholds
                if self.status.temperature_c > 80:
                    logging.error(f"Critical temp: {self.status.temperature_c}°C")
                    self.paused = True
                elif self.status.temperature_c < 70 and self.paused:
                    logging.info("Temperature normalized, resuming")
                    self.paused = False
                    
            except Exception as e:
                logging.error(f"Monitor error: {e}")
            
            await asyncio.sleep(10)
```

**2.2 Integrate Monitor into FastAPI** (0.5 days)
- Start monitor task in lifespan
- Add `/metrics` endpoint exposing current status
- Check `monitor.paused` before inference, return 503 if paused

**2.3 Error Handling Improvements** (0.5 days)
- Catch inference timeouts
- Graceful degradation on memory errors
- Structured logging throughout

**2.4 Long-Running Stability Test** (1 day)
- Run service for 24 hours
- Send request every 60 seconds
- Monitor for memory leaks, crashes, or slowdowns
- Document any issues and fixes

**Deliverable**: Hardened service with monitoring and 24-hour uptime demonstration.

---

### Phase 3: Integration Testing with Coyote Interactive (1-2 days)

**Objectives**:
- Verify drop-in replacement compatibility
- Test real interactive art use case
- Document migration steps

**Tasks**:

**3.1 Coyote Interactive Migration** (0.5 days)
- Add AX650 backend to `llm_chat_completion.py`
- Update config to use `LLM = "ax650"`
- Test TV button and person button flows

**3.2 Performance Benchmarking** (0.5 days)
- Measure response times for typical requests
- Verify <3s target is met
- Test various conversation lengths (1-50 messages)

**3.3 Documentation** (0.5 days)
- Write setup guide for coyote_interactive integration
- Document configuration options
- Create troubleshooting guide

**Deliverable**: Working integration with documented migration path.

---

## 5. Risk Assessment & Mitigation

### 5.1 Technical Risks

**Risk 1: Model Not Compatible with PyAXEngine**
- **Likelihood**: Medium
- **Impact**: High
- **Mitigation**: Test with reference examples first (Phase 0)
- **Fallback**: Use pyaxcl low-level API or C++ wrapper

**Risk 2: Inference Speed Too Slow (<3s target)**
- **Likelihood**: Low-Medium
- **Impact**: High
- **Mitigation**: Profile inference pipeline, optimize tokenization
- **Fallback**: Use smaller model or reduce default max_tokens

**Risk 3: Memory Exhaustion (CMM)**
- **Likelihood**: Medium
- **Impact**: Medium
- **Mitigation**: Monitor CMM usage, reject requests if low
- **Fallback**: Reduce context length or use model quantization

**Risk 4: Device Instability/Crashes**
- **Likelihood**: Low-Medium
- **Impact**: High
- **Mitigation**: Implement health monitoring and auto-restart
- **Fallback**: Add watchdog process to restart service

**Risk 5: Tokenizer Incompatibility**
- **Likelihood**: Low
- **Impact**: Medium
- **Mitigation**: Test with reference tokenizer from Qwen3-4B folder
- **Fallback**: Use Hugging Face transformers tokenizer

### 5.2 Operational Risks

**Risk 6: Service Not Starting After Reboot**
- **Likelihood**: Medium
- **Impact**: High
- **Mitigation**: Create systemd service file with auto-restart
- **Fallback**: Manual startup script with detailed error logging

**Risk 7: Network Connectivity Issues**
- **Likelihood**: Low
- **Impact**: Low (local network only)
- **Mitigation**: Test on local network, document port requirements
- **Fallback**: Direct USB/serial connection for debugging

---

## 6. Testing Strategy

### 6.1 Unit Tests
- Tokenizer utilities (encode/decode)
- Request validation (Pydantic models)
- Device monitor parsing functions

### 6.2 Integration Tests
- End-to-end request flow
- OpenAI client compatibility
- Health endpoint responses
- Metrics endpoint data

### 6.3 Performance Tests
- Single request latency (<3s target)
- Sustained load (10 requests/minute for 1 hour)
- Context length scaling (512, 1024, 2048 tokens)
- Memory stability (no leaks over 24 hours)

### 6.4 Acceptance Tests
- Coyote Interactive full demo (1 hour runtime)
- Button interaction response times
- Conversation state persistence across requests
- Error recovery (simulated device issues)

---

## 7. Documentation Plan

### 7.1 User Documentation
- **README.md**: Quick start, installation, basic usage
- **API_REFERENCE.md**: Endpoint documentation, request/response examples
- **CONFIGURATION.md**: All configuration options explained
- **TROUBLESHOOTING.md**: Common issues and solutions

### 7.2 Developer Documentation
- **ARCHITECTURE.md**: System design, component interactions
- **DEVELOPMENT.md**: Local setup, testing, contributing
- **DEPLOYMENT.md**: Production deployment, systemd setup, monitoring

### 7.3 Integration Guides
- **COYOTE_MIGRATION.md**: Step-by-step migration for coyote_interactive
- **OPENAI_CLIENT.md**: Using standard OpenAI Python client
- **MONITORING.md**: Health checks, metrics, alerting

---

## 8. Timeline & Milestones

### Overall Timeline: 7-12 days

**Week 1**:
- Days 1-2: Phase 0 (Environment Setup)
- Days 3-5: Phase 1 (Minimal Service)
- Days 6-7: Phase 2 (Monitoring & Hardening)

**Week 2** (if needed):
- Days 8-9: Phase 3 (Integration Testing)
- Day 10: Documentation & polish
- Days 11-12: Buffer for unexpected issues

### Key Milestones

**M1**: Environment validated, all dependencies working (Day 2)
**M2**: First successful inference via HTTP (Day 5)
**M3**: 24-hour stability test passed (Day 7)
**M4**: Coyote Interactive integration working (Day 9)
**M5**: Production-ready release (Day 12)

---

## 9. Success Metrics (Revisited)

### Quantitative Metrics
- [ ] **Latency**: P95 response time <3s for 100-token completions
- [ ] **Uptime**: 24-hour continuous operation without crashes
- [ ] **Compatibility**: 100% of OpenAI client basic features work
- [ ] **Context**: Successfully process 2048-token conversations
- [ ] **Error Rate**: <1% request failures under normal operation

### Qualitative Metrics
- [ ] **Integration Ease**: <10 lines of code change for existing projects
- [ ] **Documentation**: Complete setup possible from README alone
- [ ] **Monitoring**: Clear visibility into device health and performance
- [ ] **Recovery**: Automatic recovery from common failure modes

---

## 10. Next Steps (After Planning Approval)

Once this plan is approved, proceed to:

1. **Phase 2: Spec Mode**
   - Create detailed technical specifications
   - Define exact API contracts
   - Specify file structures and interfaces
   - Document data flows and state machines

2. **Phase 3: Implementation Mode**
   - Implement according to spec
   - Follow phase-by-phase approach
   - Track progress against milestones

3. **Phase 4: Critic Mode**
   - Review implementation for flaws
   - Test edge cases
   - Identify improvements

4. **Phase 5: Revise Mode**
   - Address identified issues
   - Refine and optimize
   - Finalize documentation

---

## Appendix A: Reference Materials

### Key Documents
- `PROJECT_VISION.md` - Overall project goals
- `initial_roadmap.md` - Initial technical roadmap
- `ax650_hardware_interaction_strategies.md` - Hardware API analysis
- `chat_completion_support_for_example_project.md` - Coyote requirements

### Reference Projects
- `reference_projects_and_documentation/Qwen3-4B/` - Model binaries
- `reference_projects_and_documentation/PyAXEngine/` - Inference library
- `reference_projects_and_documentation/pyaxcl/` - Low-level bindings
- `coyote_interactive/` - Example integration project

### External Resources
- M5Stack AX650 documentation
- AXCL SDK documentation
- OpenAI API specification
- FastAPI documentation

---

## Appendix B: Open Questions

**Q1**: Does the Qwen3-4B folder include a compatible tokenizer config?
- **Action**: Verify in Phase 0

**Q2**: What is the actual inference latency of Qwen3-4B on AX650?
- **Action**: Benchmark in Phase 1

**Q3**: Does PyAXEngine support all necessary inference parameters (temperature, top_p)?
- **Action**: Test in Phase 0, may need to use lower-level API

**Q4**: Is there a reference implementation for LLM inference with PyAXEngine?
- **Action**: Search reference_projects for examples

**Q5**: What is the exact format of the .axmodel file I/O?
- **Action**: Inspect with PyAXEngine metadata functions

---

**End of Planning Document**

**Status**: Ready for Review  
**Next Phase**: Spec Mode (pending approval)
