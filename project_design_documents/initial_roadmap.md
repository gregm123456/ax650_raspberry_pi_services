LLM Service Implementation Roadmap

Purpose
- Deliver a reliable, persistent LLM chat-completion service on M5Stack AX650/LLM8850 PCIe accelerator running on Raspberry Pi 5 that satisfies the project goals (persistent models, multi-client independence, Python-first when practical).

High-level Plan
1. Choose runtime approach: Pure-Python using `PyAXEngine` for MVP.  
2. Build a `FastAPI` service that loads axmodel(s) at startup and keeps them resident in CMM.  
3. Implement stateless request handling so each request is independent (no global conversation state).  
4. Add background device health monitor using `axcl-smi` (or `pyaxcl`).  
5. Optionally add session/KV cache later with careful memory budgeting.

Why this approach
- The pre-built C++ `ax-llm` binary is fast but enforces a single global conversation state and requires a separate tokenizer service; modifying it to safely support multi-client conversation isolation is a large engineering effort.  
- `PyAXEngine` has proven Python examples (Stable Diffusion) and allows loading and reusing models from Python, which meets Goals 2–5 quickly with less integration friction.

Recommended Architecture (MVP)
- FastAPI HTTP server exposing OpenAI-style / minimal chat-completions endpoint.  
- `axengine.InferenceSession` (PyAXEngine) to load the LLM axmodel once at startup and reuse it.  
- Use Hugging Face `transformers` or repo-provided Python tokenizer (no separate HTTP tokenizer service).  
- Single NPU worker queue initially (serialize device access).  
- Background health monitor calling `axcl-smi` every 5–10s; expose `/health` and `/metrics`.

Request Flow (stateless)
- POST prompt -> Tokenize -> Fill input tensor/buffer -> Acquire NPU worker lock -> session.run() -> Collect output tokens -> Detokenize -> Respond (streaming optional).

Persistence & Buffers
- Load models at startup into device CMM (models remain resident until explicitly unloaded).  
- Allocate and reuse input/output buffers once at startup to avoid per-request allocation overhead.

Memory & Concurrency Planning
- Typical CMM: ~7040 MiB (per analysis).  
- Example model budgets: Qwen3-4B ≈ 4 GiB (weights + KV reserve); plan per-model budgets before enabling concurrency.  
- MVP concurrency: single NPU worker (requests queued).  
- Future: allow limited concurrency (worker pool size determined empirically) and add per-session KV cache with capped concurrency and LRU eviction.

Operational Considerations
- Device health: poll `axcl-smi` every 5–10s. Thresholds: warn at 75°C, throttle at 80°C, critical actions / pause at 85°C.  
- CMM low memory: refuse model loads / reject heavy requests, evict session caches, or unload nonessential models.  
- Device unresponsive / timeout: attempt controlled reboot (`axcl-smi reboot`) and service reinitialization.  
- Expose Prometheus metrics: request rate, latency, NPU util, CMM free, temperature.

Implementation Roadmap & Estimates
- Phase 0 — Prep & smoke tests (1–2 days)
	- Install `pyaxcl` and `PyAXEngine` wheel. Run example scripts to confirm device and drivers.  
	- Confirm `axcl-smi` output and permissions.
- Phase 1 — MVP FastAPI service (3–7 days)
	- FastAPI app with lifespan startup that initializes `axengine.InferenceSession`, tokenizer, health monitor.  
	- Single `/v1/chat/completions` endpoint (stateless).  
	- Single NPU worker queue and persistent buffers.  
	- Health endpoints and basic metrics.
- Phase 2 — Hardening & performance tuning (1–2 weeks)
	- Add concurrency tuning, rate-limiting, session/KV manager if needed.  
	- Prometheus metrics, logging, systemd unit for auto-start.  
- Phase 3 — Advanced features (1–2 weeks)
	- KV cache session store in CMM with LRU eviction, more advanced scheduling.

Quickstart Commands (target device)
```bash
python3 -m pip install ./reference_projects_and_documentation/pyaxcl/
python3 -m pip install ./reference_projects_and_documentation/PyAXEngine/axengine-0.1.3-py3-none-any.whl
pip3 install fastapi uvicorn transformers safetensors openai

# Validate device
# Note: Must source /etc/profile before using AXCL commands
source /etc/profile
axcl-smi
axcl-smi info --cmm -d 0
```

MVP FastAPI lifecycle (pseudo-steps)
- On startup: load `axengine.InferenceSession(model_path, device_id=0)`; load tokenizer; allocate/reuse buffers; start health monitor.  
- Request: tokenize → fill input → acquire NPU lock → run `session.run()` → decode and return → release lock.  
- Shutdown: stop accepting requests → drain queue → close session → free buffers → optionally call `axclrtResetDevice()` via `pyaxcl`.

**API Format (OpenAI-compatible)**:
- Endpoint: `POST /v1/chat/completions`
- Request body: `{"model": "qwen3-4b-ax650", "messages": [{"role": "user", "content": "..."}], "temperature": 0.9, "max_tokens": 100}`
- Response: OpenAI chat completion format with `choices[0].message.content`

Smoke Test (curl)
```bash
curl -X POST "http://127.0.0.1:8000/v1/chat/completions" \
	-H "Content-Type: application/json" \
	-d '{"model":"qwen3-4b-ax650","messages":[{"role":"user","content":"Hello"}], "max_tokens":64}'
```

Smoke Test (OpenAI Python client - for coyote_interactive compatibility)
```python
from openai import OpenAI
client = OpenAI(base_url="http://localhost:8000/v1", api_key="not-needed")

completion = client.chat.completions.create(
    model="qwen3-4b-ax650",
    messages=[{"role": "user", "content": "Hello"}],
    max_tokens=64,
    temperature=0.9
)

print(completion.choices[0].message.content)
```

Failure modes & mitigation
- Out-of-memory (CMM): cap concurrent sessions, evict LRU, refuse new heavy requests.  
- Overheat: throttle or pause request acceptance, schedule cooldown, send alert.  
- Device unresponsive: reboot device, restart service, re-load models.

Immediate Next Tasks (pick one)
1. Scaffold an MVP FastAPI app with `lifespan` that loads an `axengine.InferenceSession`, a tokenizer, and a `/v1/chat/completions` endpoint (stateless).  
2. Produce a detailed KV-cache memory budgeting tool and per-model CMM planner.

Choose which immediate task to implement and I will scaffold files and run readonly checks before committing further edits.

---

## Interactive Art Installation Requirements (from coyote_interactive analysis)

### Performance Targets
- **Response latency**: < 3 seconds for 100-token responses (critical for interactive UX)
- **Cold start**: Model must stay loaded (no startup delay on requests)
- **Context window**: Support 2048+ tokens (long conversations with system message)

### API Compatibility
- **Primary**: OpenAI-compatible `/v1/chat/completions` endpoint
- **Client**: Must work with `openai` Python package (drop-in replacement for Azure/OpenAI)
- **Parameters**: Support `temperature`, `max_tokens`, `top_p`, `stop` per request
- **Stateless**: Client sends full conversation array each request (no server-side sessions)

### Typical Usage Pattern
```json
{
  "model": "qwen3-4b-ax650",
  "messages": [
    {"role": "system", "content": "You are Wile E. Coyote..."},
    {"role": "user", "content": "What did you hear on TV?"},
    {"role": "assistant", "content": "I heard about..."},
    {"role": "user", "content": "How will that help you?"}
  ],
  "temperature": 0.9,
  "max_tokens": 125,
  "top_p": 0.95
}
```

### Reliability Requirements
- **Uptime**: 24+ hours unattended operation
- **Error handling**: Graceful failures (don't crash the installation)
- **Health monitoring**: `/health` endpoint for external monitoring
- **Auto-recovery**: Handle device resets/errors without manual intervention

### Migration Simplicity
Target: < 10 lines of code change in existing projects:
```python
# OLD
from openai import AzureOpenAI
client = AzureOpenAI(azure_endpoint="...", api_key="...")

# NEW  
from openai import OpenAI
client = OpenAI(base_url="http://localhost:8000/v1", api_key="not-needed")

# Same API calls work!
```
