**Overview**
- **Purpose**: Provide a concrete specification for a Raspberry Pi chat-completion service that runs Qwen3-4B on AX650 / LLM8850-class hardware (Raspberry Pi 5 + AX accelerator support). The implementation will be housed primarily in a new subfolder of this repository (recommended name: `services/qwen3-4b-raspi`).
- **Scope**: Architecture, folder layout, dependencies, build and deploy steps, hardware/runtime constraints, tests, performance targets, and acceptance criteria.

**References**
- **Project documents**: `project_design_documents/01_planning.md`, `project_design_documents/PROJECT_VISION.md`.
- **Submodules / repos**: `reference_projects_and_documentation/Qwen3-4B` (contains `main_ax650`, `main_api_ax650` and run scripts), `reference_projects_and_documentation/ax-llm`, `reference_projects_and_documentation/axcl-samples`, `reference_projects_and_documentation/SmolVLM-256M-Instruct` (examples for axera packaging and run scripts).

**Goals & Constraints**
- **Primary goal**: Deliver a production-ready chat-completion microservice that exposes a simple HTTP API, runs Qwen3-4B efficiently on ax650/llm8850 Raspberry Pi 5 (Bookworm), and integrates with the existing repo as a subfolder.
- **Secondary goals**: Reproducible cross-compilation/build flows, systemd service for local deployment, automated tests and CI, easy model artifact management for updates.
- **Constraints**:
	- Target OS: Raspberry Pi Bookworm (fall 2025)
	- Hardware: Raspberry Pi 5 with AX650/LLM8850 accelerator (AX runtime + axcl binaries available in submodules)
	- Initial deployment environment: 100% local and trusted (service binds to localhost by default; operators are trusted).
	- Target LLM: Qwen3-4B (use the `Qwen3-4B` reference code and `main_ax650` binaries as the canonical runtime)
	- Memory & performance: must operate within Pi 5 limits; prefer INT8/quantized runtimes and use AX accelerator drivers provided by `ax-llm`/`axcl`.

**High-level Architecture**
- **Service folder**: `services/qwen3-4b-raspi/`
- **Components**:
	- **API layer**: Lightweight HTTP server (recommendation: `FastAPI` + `uvicorn`), exposes endpoints:
		- `POST /v1/completions` - chat completion request (messages, params)
		- `GET /v1/models` - list available model artifacts and versions
		- `POST /v1/models/load` - load/switch model (admin)
		- `GET /health` - liveness + readiness
	- **Runtime adapter**: Small wrapper that launches `main_api_ax650` as a subprocess and communicates via HTTP REST API (localhost:8000). Implements the reset-then-chat pattern to ensure conversation independence.
		- **Port configuration**: Both the `main_api_ax650` runtime and the Python service should expose default ports but be easily configurable. Default values: runtime `main_api_ax650` → 8000, service `uvicorn` → 8080. Configuration should be available via `config.py` (environment variables override) so deployments can change ports without code edits.
	- **Tokenizer**: Use the repo tokenizer utilities from `Qwen3-4B` (e.g., `qwen3_tokenizer*`) or a Python wrapper that loads prebuilt tokenizer files.
	- **Model manager**: Handles model artifacts on disk (paths, versions, checksum), provides load/unload, and reports memory/accelerator usage.
	- **Request queue & concurrency**: Single-process concurrency limited by memory and accelerator; use asyncio concurrency with a small worker pool and request size limits to avoid OOM.
	- **System service**: `systemd` unit file and `service` wrapper script `bin/run_qwen3_4b_service.sh` for startup.

**Folder Layout (proposed)**
```
services/qwen3-4b-raspi/
	README.md                # usage, build, and deployment notes
	src/
		api.py                 # FastAPI app + request validation
		runtime_adapter.py     # launch & communicate with ax650 runtime binary
		model_manager.py       # model artifact load/unload
		tokenizer.py           # tokenizer wrapper (calls shared tokenizer utils)
		config.py              # runtime configs (paths, ports, limits)
		utils/                 # helpers, metrics, logging
	bin/
		run_qwen3_4b_service.sh
	systemd/
		qwen3-4b.service
	docker/                  # Dockerfile/device packaging for builds (if useful)
	tests/
		test_api.py
		test_runtime_adapter.py
	requirements.txt         # pinned Python deps for the service
	build/                   # cross-build artifacts, packaging helpers
```

**Integration with existing submodules**
- **Model runtime binary**: Use `reference_projects_and_documentation/Qwen3-4B/main_api_ax650` as the primary accelerated runtime. This binary exposes an HTTP REST API (default port 8000) from `ax-llm/src/main_api.cpp`.
- **Runtime IPC protocol**: HTTP-based communication with the following endpoints:
  - `POST /api/reset {"system_prompt": "..."}` - Reset conversation state and prefill system prompt (~50-100ms)
  - `POST /api/chat {"messages": [...]}` - Synchronous chat completion
  - `POST /api/generate {"prompt": "..."}` - Start async generation
  - `GET /api/generate_provider` - Poll for generated text chunks (streaming)
  - `GET /api/stop` - Stop current generation
- **Conversation independence**: `main_api_ax650` maintains a single global KV cache. To ensure each chat completion is independent:
  - Call `POST /api/reset` before each new conversation (clears KV cache, adds ~50-100ms latency)
  - Then call `POST /api/chat` with the user messages
  - The `runtime_adapter.py` implements this reset-then-chat workflow automatically
  - **Trade-off**: Prefill overhead (~50-100ms) is negligible compared to generation time (6-12s for 512 tokens)
- **Model persistence**: The model stays loaded in `main_api_ax650` memory across all requests; no reloading occurs during reset operations.
- **Tokenizer & scripts**: Pull tokenizer utils from `Qwen3-4B/qwen3_tokenizer*` (copy or import). Document necessary exports and include wrapper utilities.
- **Build tools**: Reuse `ax-llm`, `axcl-samples` examples for cross-compilation and packaging steps. Reference `run_qwen3_4b_int8_ctx_ax650.sh` as a canonical run configuration.

**Build & Packaging Steps**
- **Local developer flow**:
	- Create a Python venv and install `requirements.txt` from `services/qwen3-4b-raspi/`.
	- Point `config.py` model path to a local copy of the Qwen3-4B artifacts.
	- Start `uvicorn src.api:app --host 0.0.0.0 --port 8080` for local testing.
- **Raspberry Pi target build**:
	- Cross-build or natively build the AX runtime tools from `reference_projects_and_documentation/ax-llm` and `Qwen3-4B` following their `run_*_ax650.sh` scripts.
	- Package: assemble Python app, model artifacts, and the `main_ax650` binary into a deployment tarball or APT package.
	- Deploy: copy package onto Pi, extract into `/opt/qwen3-4b/`, enable `systemd` unit `qwen3-4b.service`.
	- Optionally provide a container-based approach: `docker build` for a Bookworm base image that includes necessary runtime and model artifacts (note: container size and device access must be validated on Pi).

**Runtime & Resource Management**
- **Memory caps**: enforce request token limits and disallow large batch requests; implement graceful rejection with informative error.
- **Accelerator binding**: ensure `runtime_adapter.py` validates accelerator availability before accepting requests.
- **Fallback handling**: if accelerator is unavailable, service should optionally run in a degraded CPU-only mode (with explicit config) or reject requests.

**Testing & Validation**
- **Unit tests**: `tests/test_api.py`, `tests/test_runtime_adapter.py` mocking subprocess / binary.
- **Integration tests**: end-to-end tests that start the service, call `/v1/completions` with small prompt and assert response shape.
- **Performance tests**: scripted latency and throughput tests on target hardware (Pi 5 + AX650) using representative prompts. Measure p99, p50 latencies and memory usage.

**Performance Targets (initial)**
- **Latency**: single-stream generation (512 tokens) target p50 < 6s, p95 < 12s on AX650 using INT8 optimized runtime. (Empirical targets — update after first real device run.)
- **Throughput**: safe concurrent requests = 1–2 depending on model size; provide queueing and backpressure.

**Security & Privacy**
- **Default (local & trusted)**: initial deployments are assumed to be 100% local and trusted. The service MUST bind to `127.0.0.1` by default and restrict administrative endpoints to the local host or a local unix domain socket. For local use, TLS is not required; protect admin operations using OS-level ACLs, local-only sockets, or a minimal static token file.
- **Production guidance**: if the service is later exposed beyond the local host, require TLS and stronger authentication (e.g., OAuth2, mTLS), run behind a reverse proxy (`nginx`/`traefik`) and enable network-level firewall rules.
- **Logging**: Keep logs for debugging. This service is intended for art projects and is not expected to handle PII.

**CI / Automation**
- **Unit test runs**: GitHub Actions that run `pytest` for Python service code on push.
- **Build/packaging job**: optionally run cross-build scripts from `ax-llm` and `Qwen3-4B`, producing tarballs/artifacts in CI artifacts.

**Acceptance Criteria**
- `services/qwen3-4b-raspi` exists with runnable `src/api.py` and `runtime_adapter.py` locally.
- CI runs unit tests and passes.
- Deployed package successfully starts as `systemd` service on Raspberry Pi Bookworm (manual verification step) and responds to `/v1/completions`.
- Basic performance test meets the defined latency envelope on AX650 hardware (or documented deviations).

**Milestones**
1. Spec (this document) — complete.
2. Initial API + runtime adapter scaffolding in `services/qwen3-4b-raspi`.
3. Local dev run with small model or mocked runtime.
4. Cross-build and package runtime binaries; deploy to Pi.
5. Real-device performance tuning and acceptance.

**Resolved Decisions**
- **IPC model**: HTTP REST API via `main_api_ax650` (port 8000). This provides clean request/response handling, built-in concurrency, and easy monitoring.
- **Conversation state**: Use reset-then-chat pattern (`POST /api/reset` before each new conversation) to ensure independence. Model stays loaded; reset adds ~50-100ms prefill overhead.
- **Model artifacts**: Store in repo submodules for MVP; transition to external storage with checksum validation in production.
- **Auth for admin endpoints**: Static token file or OS-level ACLs for local deployment; defer complex auth until network exposure is required.

**Appendix: Quick start (developer)**
- Create venv and install deps:
```
python -m venv .venv
source .venv/bin/activate
pip install -r services/qwen3-4b-raspi/requirements.txt
```
- Run locally (development):
```
uvicorn services.qwen3_4b_raspi.src.api:app --host 0.0.0.0 --port 8080 --reload
```

Note: On Raspberry Pi systems configured for the AX650/LLM8850 runtime, make sure the system environment for AXCL tools is loaded before running accelerator commands or the runtime binary. In a shell session run:

```bash
# Ensure AXCL CLI and library paths are available to your shell/session
source /etc/profile
```


-----
Spec authored to integrate with the repository's `reference_projects_and_documentation` submodules and to be implementable in a contained `services/qwen3-4b-raspi` subfolder.

