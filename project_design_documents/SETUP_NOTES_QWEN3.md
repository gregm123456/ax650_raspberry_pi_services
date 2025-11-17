# Qwen3-4B AX650 Setup Notes

**Date**: November 16, 2025  
**Status**: Runtime Setup - In Progress

---

## Executive Summary

This document captures critical setup steps and fixes discovered while bringing up the Qwen3-4B model on the AX650/LLM8850 PCIe accelerator. These notes supplement the main project specifications and provide practical solutions to common issues.

---

## Critical Environment Setup

### 1. AXCL Environment Must Be Sourced

**Issue**: AXCL tools and libraries are not on PATH/LD_LIBRARY_PATH by default.

**Solution**: Always source `/etc/profile` before running any AXCL commands or binaries:

```bash
source /etc/profile
```

**What this provides**:
- AXCL CLI tools (`axcl-smi`, etc.) on PATH
- AXCL runtime libraries (`/usr/lib/axcl`) on LD_LIBRARY_PATH
- Required environment variables for hardware access

**When to use**:
- Before running any `axcl-smi` commands
- Before starting any runtime binaries (`main_axcl_aarch64`, `main_api_axcl_aarch64`)
- In shell scripts that interact with the hardware

### 2. Python Virtual Environment

**Issue**: Python dependencies (transformers, jinja2, protobuf, etc.) must be available.

**Solution**: Always activate the project venv before running Python scripts:

```bash
source /home/robot/ax650_raspberry_pi_services/.venv/bin/activate
```

**When to use**:
- Before starting the tokenizer service (`qwen3_tokenizer_uid.py`)
- Before running any FastAPI service commands
- Before any Python script that imports project dependencies

### 3. Combined Environment Setup Pattern

For scripts that need both AXCL hardware access AND Python dependencies:

```bash
# Source AXCL environment first
source /etc/profile

# Then activate Python venv
source /home/robot/ax650_raspberry_pi_services/.venv/bin/activate

# Now run your commands
```

---

## Model Artifacts & Git LFS Issues

### Problem: LFS Pointer Files Instead of Real Binaries

**Issue**: Many files in the `reference_projects_and_documentation/Qwen3-4B/` directory are Git LFS pointer files (132-byte ASCII text) rather than actual binaries or model files.

**Affected files discovered**:
- `main_ax650` (985 KB actual binary)
- `main_axcl_aarch64` (1.7 MB actual binary)
- `main_api_ax650` (needs download)
- `main_api_axcl_aarch64` (1.8 MB actual binary)
- `qwen3_tokenizer/tokenizer.json` and related files

**Why this happens**: The GitHub repo has LFS pointers committed, but the actual large files are stored on HuggingFace's servers, not the user's GitHub LFS server.

### Solution: Download from HuggingFace

Use `huggingface_hub` to download real files:

```python
from huggingface_hub import hf_hub_download
import shutil

# Download specific binary
path = hf_hub_download(
    repo_id='AXERA-TECH/Qwen3-4B',
    filename='main_api_axcl_aarch64',  # or other file
    local_dir_use_symlinks=False
)

# Copy from HF cache to working directory
shutil.copy(path, 'reference_projects_and_documentation/Qwen3-4B/main_api_axcl_aarch64')
```

For directories of files (like tokenizer):

```python
from huggingface_hub import snapshot_download

snapshot_download(
    repo_id='AXERA-TECH/Qwen3-4B',
    allow_patterns='qwen3_tokenizer/*',
    local_dir='reference_projects_and_documentation/Qwen3-4B',
    local_dir_use_symlinks=False
)
```

**Verification**: Check file sizes after download:

```bash
# LFS pointer = 132 bytes (wrong)
# Real binary = hundreds of KB to MB (correct)
ls -lh reference_projects_and_documentation/Qwen3-4B/main_api_axcl_aarch64
```

---

## Runtime Binary Selection

### Critical Distinction: AX SDK vs AXCL

The M5Stack AX650/LLM8850 PCIe card uses **AXCL** runtime, not the older AX SDK.

**Binary naming pattern**:
- `main_ax650` = Old AX SDK binary (incompatible with PCIe card)
- `main_axcl_aarch64` = AXCL-compatible binary for ARM64 host
- `main_axcl_x86` = AXCL-compatible binary for x86_64 host

### Interactive CLI vs HTTP API Server

**Two types of binaries available**:

1. **Interactive CLI** (`main_axcl_aarch64`):
   - Runs in interactive mode with `prompt >>` loop
   - Good for testing model manually
   - NOT suitable for API service integration

2. **HTTP API Server** (`main_api_axcl_aarch64`):
   - Exposes REST API endpoints (`/api/reset`, `/api/chat`, `/api/health`)
   - Runs as a background service
   - **THIS IS THE CORRECT CHOICE** for FastAPI integration per specs

**Command-line arguments**:

The HTTP API binary uses long-form options (not `-m` style):

```bash
./main_api_axcl_aarch64 \
  --system_prompt "You are Qwen, created by Alibaba Cloud. You are a helpful assistant." \
  --template_filename_axmodel "qwen3-4b-ax650/qwen3_p128_l%d_together.axmodel" \
  --axmodel_num 36 \
  --url_tokenizer_model "http://127.0.0.1:12345" \
  --filename_post_axmodel qwen3-4b-ax650/qwen3_post.axmodel \
  --filename_tokens_embed qwen3-4b-ax650/model.embed_tokens.weight.bfloat16.bin \
  --tokens_embed_num 151936 \
  --tokens_embed_size 2560 \
  --use_mmap_load_embed 1 \
  --live_print 1 \
  --devices 0
```

**Default port**: 8000 (HTTP API listens on this port)

---

## Tokenizer Service Setup

### Required Python Dependencies

The tokenizer service (`qwen3_tokenizer_uid.py`) requires:

```bash
pip install transformers protobuf jinja2
```

**Why each is needed**:
- `transformers`: HuggingFace tokenizer library
- `protobuf`: Required by transformers for tokenizer model serialization
- `jinja2`: Required by transformers for chat template rendering

**Error symptoms if missing**:
- `protobuf` missing: `ImportError: protobuf not found`
- `jinja2` missing: `ImportError: apply_chat_template requires jinja2 to be installed`

### Tokenizer Model Files

The tokenizer requires actual model files (not LFS pointers) in `qwen3_tokenizer/`:

**Required files**:
- `tokenizer.json` (main tokenizer config)
- `merges.txt` (BPE merges)
- `vocab.json` (vocabulary)
- `special_tokens_map.json`
- `tokenizer_config.json`

**Download if missing**:

```bash
cd /home/robot/ax650_raspberry_pi_services
source .venv/bin/activate
python3 -c "
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id='AXERA-TECH/Qwen3-4B',
    allow_patterns='qwen3_tokenizer/*',
    local_dir='reference_projects_and_documentation/Qwen3-4B',
    local_dir_use_symlinks=False
)
"
```

### Starting the Tokenizer

**Correct startup sequence**:

```bash
cd /home/robot/ax650_raspberry_pi_services/reference_projects_and_documentation/Qwen3-4B
source /home/robot/ax650_raspberry_pi_services/.venv/bin/activate
nohup python3 qwen3_tokenizer_uid.py --host 127.0.0.1 --port 12345 > qwen3_tokenizer.log 2>&1 &
```

**Verification**:

```bash
# Check if listening
curl -sS http://127.0.0.1:12345/get_uid
# Should return: {"uid": "<uuid>"}

# Check logs
tail -n 50 qwen3_tokenizer.log
```

---

## Shared Library Dependencies

### AXCL System Libraries

**Location**: `/usr/lib/axcl/`

**Key libraries**:
- `libaxcl_sys.so` - System management
- `libaxcl_rt.so` - Runtime engine
- `libaxcl_pkg.so` - Package management
- `libaxcl_engine.so` - NPU engine (if present)

**Environment variable**:

```bash
export LD_LIBRARY_PATH=/usr/lib/axcl
```

**Note**: Sourcing `/etc/profile` typically sets this automatically.

### DO NOT Use SmolVLM Paths

**Common mistake**: Including SmolVLM library paths when running Qwen3-4B.

**Wrong**:
```bash
export LD_LIBRARY_PATH=/path/to/SmolVLM-256M-Instruct.axera/python/npu_python_llm/engine_so:/usr/lib/axcl
```

**Correct**:
```bash
export LD_LIBRARY_PATH=/usr/lib/axcl
```

**Why**: Qwen3-4B binaries are built against the system AXCL libraries. SmolVLM's engine libraries are for a different model and can cause conflicts or symbol mismatches.

---

## Dependency Installation Summary

### System Requirements

```bash
# AXCL runtime must be installed system-wide
# Verify with:
source /etc/profile
axcl-smi
```

### Python Dependencies (in project venv)

```bash
cd /home/robot/ax650_raspberry_pi_services
python3 -m venv .venv
source .venv/bin/activate

# Core dependencies
pip install fastapi uvicorn pydantic

# LLM-specific
pip install transformers huggingface_hub

# Required by transformers
pip install protobuf jinja2

# Testing
pip install httpx pytest

# Development
pip install openai  # For testing OpenAI-compatible client
```

**Installed versions (verified working)**:
- `transformers==4.57.1`
- `huggingface_hub<1.0,>=0.34.0`
- `protobuf==6.33.1`
- `jinja2==3.1.6`
- `MarkupSafe==3.0.3`

---

## Device Verification Commands

### Check Device Status

```bash
source /etc/profile
axcl-smi
```

**Expected output**:
```
+------------------------------------------------------------------------------------------------+
| AXCL-SMI  V3.6.4                                             Driver  V3.6.4                    |
+-----------------------------------------+--------------+---------------------------------------+
| Card  Name                     Firmware | Bus-Id       | Memory-Usage                          |
| Fan   Temp                Pwr:Usage/Cap | CPU      NPU | CMM-Usage                             |
|=========================================+==============+=======================================|
| 0  AX650N                     V3.6.4    | 0001:01:00.0 | 149 MiB /      945 MiB                |
| --   41C                      -- / --   | 1%        0% | 18 MiB /     7040 MiB                 |
+-----------------------------------------+--------------+---------------------------------------+
```

### Check CMM (Model Memory)

```bash
axcl-smi info --cmm -d 0
```

**Expected**: `CMM Total: 7208960 KiB, CMM Used: 18876 KiB` (or similar)

### Check Temperature

```bash
axcl-smi info --temp -d 0
```

**Expected**: `temperature: 41000` (41°C in millidegrees)

---

## Current Status & Next Steps

### Completed
- ✅ AXCL environment sourced and device verified
- ✅ Python venv created with all dependencies
- ✅ Model artifacts downloaded (~5.1 GB of .axmodel files)
- ✅ Tokenizer model files downloaded (real files, not LFS pointers)
- ✅ Tokenizer service running successfully on 127.0.0.1:12345
- ✅ HTTP API runtime binary (`main_api_axcl_aarch64`) downloaded and made executable

### In Progress
- ⏳ Start HTTP API runtime (`main_api_axcl_aarch64`) with correct arguments
  - Command prepared with proper long-form options
  - Needs to be started with AXCL env sourced
  - Should listen on port 8000 for `/api/health`, `/api/reset`, `/api/chat`

### Not Started
- ❌ Verify HTTP runtime health endpoint (`/api/health`)
- ❌ Start FastAPI service in non-mock mode
- ❌ Configure FastAPI service to communicate with runtime on port 8000
- ❌ Run end-to-end test: POST to `/v1/chat/completions`
- ❌ Verify full request flow: FastAPI → runtime → tokenizer → model → response

---

## Quick Reference: Startup Commands

### Full Service Startup Sequence

```bash
# 1. Navigate to Qwen3-4B directory
cd /home/robot/ax650_raspberry_pi_services/reference_projects_and_documentation/Qwen3-4B

# 2. Source AXCL environment
source /etc/profile

# 3. Activate Python venv
source /home/robot/ax650_raspberry_pi_services/.venv/bin/activate

# 4. Start tokenizer service
nohup python3 qwen3_tokenizer_uid.py --host 127.0.0.1 --port 12345 > qwen3_tokenizer.log 2>&1 &

# 5. Wait for tokenizer to be ready
sleep 2

# 6. Set library path (AXCL only, no SmolVLM)
export LD_LIBRARY_PATH=/usr/lib/axcl

# 7. Start HTTP API runtime
nohup ./main_api_axcl_aarch64 \
  --system_prompt "You are Qwen, created by Alibaba Cloud. You are a helpful assistant." \
  --template_filename_axmodel "qwen3-4b-ax650/qwen3_p128_l%d_together.axmodel" \
  --axmodel_num 36 \
  --url_tokenizer_model "http://127.0.0.1:12345" \
  --filename_post_axmodel qwen3-4b-ax650/qwen3_post.axmodel \
  --filename_tokens_embed qwen3-4b-ax650/model.embed_tokens.weight.bfloat16.bin \
  --tokens_embed_num 151936 \
  --tokens_embed_size 2560 \
  --use_mmap_load_embed 1 \
  --live_print 1 \
  --devices 0 \
  > qwen3_http_runtime.log 2>&1 &

# 8. Wait for runtime to initialize
sleep 5

# 9. Verify services
curl -sS http://127.0.0.1:12345/get_uid        # Tokenizer health
curl -sS http://127.0.0.1:8000/api/health      # Runtime health
```

### Log Monitoring

```bash
# Tokenizer logs
tail -f /home/robot/ax650_raspberry_pi_services/reference_projects_and_documentation/Qwen3-4B/qwen3_tokenizer.log

# Runtime logs
tail -f /home/robot/ax650_raspberry_pi_services/reference_projects_and_documentation/Qwen3-4B/qwen3_http_runtime.log
```

### Process Management

```bash
# Check if running
ps -ef | grep qwen3_tokenizer_uid.py
ps -ef | grep main_api_axcl_aarch64

# Stop services
pkill -f qwen3_tokenizer_uid.py
pkill -f main_api_axcl_aarch64
```

---

## Common Issues & Solutions

### Issue: "No such file or directory" when running binary

**Cause**: Either the binary is an LFS pointer (132 bytes), or working directory is wrong.

**Solution**: Download real binary from HuggingFace and verify size.

### Issue: "undefined short option: -m"

**Cause**: Using old-style short options with HTTP API binary.

**Solution**: Use long-form options (`--system_prompt`, not `-m`).

### Issue: Tokenizer crashes with "expected value at line 1 column 1"

**Cause**: Tokenizer model files are LFS pointers, not real JSON files.

**Solution**: Download tokenizer files from HuggingFace.

### Issue: "ImportError: jinja2" or "ImportError: protobuf"

**Cause**: Missing Python dependencies.

**Solution**: `pip install jinja2 protobuf` in the project venv.

### Issue: Runtime can't find AXCL libraries

**Cause**: `/etc/profile` not sourced or `LD_LIBRARY_PATH` not set.

**Solution**: `source /etc/profile` before running runtime binary.

---

## Architecture Notes for Next Session

### Current Understanding

Per the project specifications (`02_specifications.md`):

1. **Runtime Binary**: `main_api_axcl_aarch64` is the HTTP server that:
   - Loads the Qwen3-4B model once at startup
   - Exposes REST API on port 8000
   - Endpoints: `/api/reset`, `/api/chat`, `/api/generate`, `/api/health`
   - Maintains a single global KV cache

2. **Conversation Independence**: 
   - Each new conversation requires `POST /api/reset` to clear KV cache
   - Then `POST /api/chat` with messages array
   - Adds ~50-100ms prefill overhead per conversation
   - Trade-off acceptable vs generation time (6-12s for 512 tokens)

3. **FastAPI Service Role**:
   - Wraps the HTTP runtime in OpenAI-compatible API
   - Implements reset-then-chat pattern via `runtime_adapter.py`
   - Translates `/v1/chat/completions` → `/api/reset` + `/api/chat`
   - Should be configured to point to `http://127.0.0.1:8000` (runtime port)

### Configuration Needed

The `services/qwen3-4b-raspi/src/config.py` should have:

```python
RUNTIME_HOST = "127.0.0.1"
RUNTIME_PORT = 8000  # Where main_api_axcl_aarch64 listens
MODEL_BASE_PATH = "/home/robot/ax650_raspberry_pi_services/reference_projects_and_documentation/Qwen3-4B/qwen3-4b-ax650"
```

---

## Git Repository Management

### Downloaded Files Are Gitignored

The following patterns are added to `.gitignore` to prevent accidentally committing large model files:

```gitignore
# Downloaded model artifacts (several GB - keep out of git)
*.axmodel
*.bfloat16.bin
reference_projects_and_documentation/Qwen3-4B/qwen3-4b-ax650/
reference_projects_and_documentation/Qwen3-4B/qwen3_tokenizer/
reference_projects_and_documentation/Qwen3-4B/qwen2.5_tokenizer/

# Downloaded runtime binaries (download from HF as needed)
reference_projects_and_documentation/Qwen3-4B/main_axcl_aarch64
reference_projects_and_documentation/Qwen3-4B/main_api_axcl_aarch64

# Runtime logs and PID files
qwen3*.log
qwen3*.pid
reference_projects_and_documentation/Qwen3-4B/*.log
reference_projects_and_documentation/Qwen3-4B/*.pid
```

### Qwen3-4B Submodule Notes

The `reference_projects_and_documentation/Qwen3-4B/` directory is a git submodule that contains LFS pointer files. When you download the actual files from HuggingFace, git will show them as "Modified" in the submodule.

**Important**: DO NOT commit these changes to the Qwen3-4B submodule. They should remain local only.

```bash
# To see submodule changes:
cd reference_projects_and_documentation/Qwen3-4B
git status

# You will see many "M" (modified) files - this is expected
# DO NOT run: git add . or git commit in this directory

# To discard submodule changes (if needed):
cd /home/robot/ax650_raspberry_pi_services
git submodule update --init --recursive  # Resets to LFS pointers
```

### What Should Be Committed

Only commit to the main repository:
- Documentation updates (`project_design_documents/SETUP_NOTES_QWEN3.md`)
- Service code changes (`services/qwen3-4b-raspi/`)
- Scripts (`scripts/download_qwen3_models.sh`)
- Configuration updates (`.gitignore`)

Do NOT commit:
- Downloaded model files (multi-GB)
- Downloaded binaries (`main_*`)
- Runtime logs (`*.log`)
- PID files (`*.pid`)

---

## Critical Bug: Message Order Reversal in Runtime

**Date Discovered**: November 16, 2025

### Problem Description

The C++ runtime binary (`main_api_axcl_aarch64`) **reverses the message array internally** before processing conversations. This causes the model to respond based on the FIRST message sent to the API, rather than the LAST (most recent) message.

### Symptoms

- When sending a conversation like: `[system_msg, user_msg_1, assistant_msg_1, user_msg_2, assistant_msg_2, user_msg_3]`
- The runtime processes it as: `[user_msg_3, assistant_msg_2, user_msg_2, assistant_msg_1, user_msg_1, system_msg]`
- The model generates a response based on `user_msg_3` (which it sees first after reversal) instead of the intended most-recent message

### Evidence & Testing

**Test 1: Original Order Conversation**
- Sent 13-message conversation with first message about "protein/Six-Ounce Center/beating our heart"
- Last message about "vaccines/plants/hot deal/2495"
- **Result**: Model responded about "Six-Ounce Center" and "protein" (first message topics)

**Test 2: Reversed Order Conversation**  
- Sent the same conversation with messages manually reversed
- Now "vaccines" message was first, "protein" message was last
- **Result**: Model responded about "vaccines", "plants", "hot deal", "2495" (what was originally the last message)

**Test 3: Product List Request**
- Changed the last message to: "Please list the names of five of the products you have heard about"
- Expected: Model lists 5 products from throughout the conversation
- **Actual**: Model only talked about "Six-Ounce Center" (the first product), completely ignoring the question asking for a list

**Debug Evidence**:
```
DEBUG: Message[0] role=user, length=680, hash=1408712486810884044
DEBUG: Message[0] middle snippet: ...beating our heart...
DEBUG: Message[-1] role=user, length=67, hash=405190351691753379  
DEBUG: Message[-1] middle snippet: ...the products you have heard about...
```
Model response ignored the actual last message and responded to the first one.

### Root Cause

The runtime's internal conversation context builder or KV cache management reverses the message order. This is likely in the C++ code that processes the `/api/chat` endpoint's message array.

### Solution

**Implemented in**: `services/qwen3-4b-raspi/src/runtime_adapter.py`

The `reset_then_chat()` function now **reverses the message array before sending it to the runtime**:

```python
# CRITICAL FIX: The C++ runtime reverses the message array internally
reversed_messages = list(reversed(messages))
payload: Dict[str, Any] = {"messages": reversed_messages}
```

This way, when the runtime reverses it again, the messages end up in the correct chronological order.

### Verification

After implementing the fix, test with a multi-turn conversation and verify the model responds to the most recent message, not the first one.

**Test command**:
```bash
curl -X POST http://127.0.0.1:8080/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3-4b",
    "messages": [
      {"role": "user", "content": "FIRST: Tell me about apples"},
      {"role": "assistant", "content": "Apples are fruits..."},
      {"role": "user", "content": "LAST: Forget apples. Tell me about oranges instead."}
    ]
  }'
```

Expected: Model talks about oranges (most recent request)
Before fix: Model would talk about apples (first message)

---

**End of setup notes. Continue with runtime startup and FastAPI integration.**
