# Submodule overview

This document provides a concise, distinguishing summary for each submodule and related helper files contained in the `reference_projects_and_documentation` folder. Use these short descriptions to quickly identify each repo's purpose and where to look for detailed code, docs, or conversion tools.

## ⚠️ Reality Checks & Architecture Notes

**Key Finding**: These are demo projects, NOT production-ready service architectures. Significant adaptation needed.

**Critical Constraint**: M5Stack AX650/LLM8850 PCIe card on Raspberry Pi 5
- This is an **M.2 accelerator card** not a development board
- Requires **AXCL** (Axera Compute Library) runtime, not standard SDK
- Examples show both on-device (`ax650`) and M.2 card (`axcl_aarch64`, `axcl_x86`) variants
- **Must verify**: Raspberry Pi 5 compatibility and driver installation for M.2 card - check axcl-docs

**LLM Architecture Pattern (ax-llm)**:
- ✅ Has C++ HTTP API server (`main_api.cpp`) with basic endpoints (`/api/generate`, `/api/reset`, `/api/stop`)
- ✅ Uses httplib (single-header C++ library) for HTTP server
- ⚠️ Tokenizer runs as **separate Python HTTP service** (not embedded) - tokenizer must run alongside C++ runtime
- ⚠️ C++ binary loads models and keeps them in memory - Python calls via HTTP
- ⚠️ gradio_demo.py is a **client UI**, NOT the server - it calls an existing API at port 8000
- 🔧 **Adaptation needed**: Wrap C++ binary as system service OR rewrite in Python using pyaxcl/PyAXEngine

**Stable Diffusion Architecture Pattern (sd1.5-lcm.axera)**:
- ✅ Pure Python inference scripts using PyAXEngine (axengine Python package)
- ✅ Loads models (text_encoder, unet, vae_decoder) as axmodel files via axengine.InferenceSession
- ⚠️ Scripts are **one-shot CLI tools** - generate one image and exit
- ⚠️ No HTTP server, no persistent model loading, no API endpoints
- 🔧 **Adaptation needed**: Build FastAPI/Flask wrapper that loads models once and serves requests

---

- `ax-llm`: Core LLM repository and tooling targeting Axera devices. Contains model source, tokenizers, CMake build scripts, demo scripts (e.g., Gradio), and utilities for preparing and running large language models on Axera hardware.
	- How this helps the Project Vision:
		- **Has working C++ API server** — `main_api.cpp` implements HTTP endpoints for chat generation with model persistence (Goal 3). Uses httplib for lightweight HTTP serving.
		- **Two-process architecture** — C++ runtime binary + separate Python tokenizer HTTP service. The tokenizer scripts (e.g., `qwen3_tokenizer_uid.py`) run as standalone HTTP servers using Python's http.server.
		- **Model hosting patterns** — demonstrates prefill/kv cache strategies and persistent runtime usage; useful to achieve the "keep models loaded" goal.
		- **⚠️ Reality check** — This is a working reference but requires running TWO services (C++ + Python tokenizer). Gradio demo is just a UI client. Need to decide: wrap C++ binary as-is OR reimplement using pyaxcl/PyAXEngine for pure Python solution (Goal 5).

- `ax-pipeline`: Build and deployment pipeline for Axera BSPs and models. Includes CMake configuration, scripts to download or switch AX BSP versions, and pipeline helpers used to prepare images, toolchains, and runtime artifacts for AX650-class deployments.
	- How this helps the Project Vision:
		- **Build & packaging automation** — use to produce reproducible device images and runtime artifacts for the AX650 and M.2 cards (Goal 1 and 2).
		- **Model conversion & image build helpers** — scripts and docs show how to create deployable images and pipelines to copy AR artifacts and prebuilt models onto Raspberry Pi devices.

- `axcl-docs`: Documentation for the AXCL (Axera Compute Library) and related developer guides. Includes ReadTheDocs configuration, documentation source, example usage, and reference material for the compute library APIs.
	- How this helps the Project Vision:
		- **Single authoritative API reference** — use to understand device-level and driver-level APIs, memory/engine configs, and how to integrate device monitoring and reset logic into python services (Goal 4).
		- **Guides for hardware integration** — the docs can be used to build robust device health monitoring and resource cleanup logic for persistence (Goal 3 and 4).

- `axcl-samples`: Practical sample applications and CMake examples demonstrating how to use AXCL. Contains minimal example projects, sample build setups, and usage patterns for integrating AXCL into applications.
	- How this helps the Project Vision:
		- **Concrete examples** — code templates and sample pipelines show how to orchestrate multiple NPU/IVPS/codec flows, which is helpful for production endpoints that combine image input, preprocessing, and inference.
		- **Reference model-run patterns** — adopt these patterns to keep models loaded and orchestrate multiple model contexts simultaneously (Goal 3).

- `pulsar2-docs`: Documentation repository for the Pulsar2 project. Provides user-facing and developer documentation, build instructions, and any project-specific guides housed separately from code samples.
	- How this helps the Project Vision:
		- **Model conversion & toolchain docs** — Pulsar2 docs contain exact steps for converting Huggingface models to Axera formats (axmodel/quantization) and are key for adding new models (Goal 2 & non-goal note on avoiding upstream changes).
		- **Operational guidance** — compatibility and operation notes for Pulsar2 tools will help ensure conversion workflows are repeatable and documented.

- `pyaxcl`: Python package and bindings for AXCL. Contains `setup.py`, packaging metadata, sample code, and tests for the Python-facing APIs that wrap the AXCL runtime.
	- How this helps the Project Vision:
		- **Python device control & management** — provides a production-oriented Python interface to AXCL (preferred language for the project), enabling device setup, model load/unload, status checks, and resets (Goal 4 & Goal 5).
		- **⚠️ Reality check** — Sample code (`sample/engine/sample_engine.py`) shows **one-shot inference** pattern (load model, run, exit). No built-in API server or persistent model hosting. Focus is on codec, IVPS, and multimedia, NOT LLM-specific workflows.
		- **🔧 Adaptation needed** — Use pyaxcl for device health monitoring and low-level control. For LLM inference, may need to combine with PyAXEngine or wrap ax-llm C++ binary.

- `PyAXEngine`: Prebuilt Python wheel and runtime configuration for the Axera inference engine. This repo packages a ready-to-install wheel and config files used to run models with the Axera engine from Python.
	- How this helps the Project Vision:
		- **Python-first NPU inference** — PyAXEngine provides an ONNX Runtime-style API (`axengine.InferenceSession`) for loading and running axmodel files directly from Python (Goal 5).
		- **✅ Best fit for pure Python services** — Used successfully in sd1.5-lcm.axera Python scripts. Can load models, run inference, and be wrapped in FastAPI/Flask for persistent API endpoints.
		- **⚠️ Limitation** — PyAXEngine README explicitly states it's "better suited for rapid prototyping" and "cannot call some codec-related modules on card environments". For production M.2 card deployments, recommends pyaxcl instead.
		- **🔧 Decision point** — Use PyAXEngine for initial development and lightweight deployments (e.g., SD image gen). For robust production LLM chat or multi-model scenarios, may need pyaxcl or C++ runtime.

- `Qwen3-4B`: Packaged model runtime and tooling for the Qwen 3 4B model optimized for Axera/AX650. Contains compiled binaries, tokenizer code, runtime examples, and scripts to run the model on target hardware.
	- How this helps the Project Vision:
		- **Production-ready axmodel files** — Contains 36 layer axmodel files (qwen3_p128_l0-35_together.axmodel) and post-processing model for AX650 hardware.
		- **Three runtime variants** — `main_ax650` (on-device), `main_axcl_aarch64` (M.2 card on ARM), `main_axcl_x86` (M.2 card on x86). These are the SAME C++ binaries from ax-llm, just pre-compiled.
		- **Tokenizer service required** — Includes `qwen3_tokenizer_uid.py` which is a standalone HTTP server (Python http.server) that must run separately from the C++ inference binary.
		- **⚠️ Reality check** — This is NOT a self-contained model package. It's pre-compiled binaries + model files + tokenizer script. Still requires two-process architecture (C++ + Python tokenizer).
		- **🔧 Adaptation** — Can use binaries as-is wrapped in systemd services OR use model files with PyAXEngine to build pure Python solution (but would need to reimplement LLM inference logic).

- `Qwen3-VL.AXERA`: Vision–language variant resources and conversion tools. Includes model-conversion helpers, Python utilities and assets for running Qwen vision-language models on Axera platforms.
	- How this helps the Project Vision:
		- **Vision+LLM (VLM) support** — includes example inference pipelines that combine image embeddings and text decoding; essential to build vision endpoints and multi-modal chat completion (Goal 2: Vision LLM).
		- **Model conversion focus** — `model_convert/` contains scripts for exporting, quantizing, and building VLM models. `python/` has inference scripts (`infer_image.py`, `infer_video.py`).
		- **⚠️ CLI inference scripts, not services** — Python scripts load model, process one image/video, print output, and exit. No persistent model hosting or API.
		- **Pre- & post-processing utilities** — the code demonstrates how to preprocess images and stitch embeddings into the text prompt, which informs how to handle image inputs in the service design.
		- **🔧 Similar adaptation as LLMs** — Would need to wrap in API service with persistent model loading. Architecture likely mirrors ax-llm (C++ runtime + tokenizer service).

- `sd1.5-lcm.axera`: Stable Diffusion 1.5 (LCM variant) converted and packaged for Axera. Holds conversion scripts, runtime assets, and Axera-optimized model artifacts used for image generation on-device.
	- How this helps the Project Vision:
		- **✅ Pure Python inference** — Scripts in `python/` folder use PyAXEngine to load and run text_encoder, unet, and vae_decoder axmodels. This is a complete working example (Goal 5).
		- **Image generation pipeline** — `run_txt2img_axe_infer.py` and `run_img2img_axe_infer.py` show end-to-end text-to-image and image-to-image workflows using transformers (CLIP tokenizer) + axengine.InferenceSession.
		- **⚠️ Reality check** — Scripts are **CLI one-shot tools** - they parse args, load models, generate ONE image, save to disk, and exit. No HTTP server, no persistent model loading, no streaming.
		- **🔧 Adaptation needed** — Relatively straightforward to wrap in FastAPI/Flask: load models once at startup (in global scope or class), accept prompts via POST endpoint, return generated images. This is closest to "production-ready Python" pattern we need (Success Metric 2).
		- **Model conversion & runtime best practices** — Shows conversion and runtime patterns (quantization, onnx, axmodel) we should replicate for artifact packaging and fast startup.

- `SmolVLM-256M-Instruct`: Compact vision-language model with tokenizer and run scripts for smaller Axera devices (AX630/AX650). Contains the reference model, tokenizers, and shell scripts to run the model in example environments.
	- How this helps the Project Vision:
		- **Low-resource VLM example** — Small VLM suitable for devices with tighter resources; helpful for multi-listener CPU/RAM-constrained deployments on Raspberry Pi + M.2 card (Goal 3: keep models loaded).
		- **Pre-built binaries + models** — Contains `main` binary (C++), axmodel files in `smolvlm-256m-ax650/` folder, and tokenizer script `smolvlm_tokenizer_512.py`.
		- **⚠️ Same architecture as Qwen3-4B** — Uses C++ binary for inference + separate Python HTTP tokenizer service. Same two-process pattern.
		- **Shell scripts are launchers** — `run_smolvlm_ax650.sh` just sets environment variables and calls the C++ binary with command-line args. Not a service wrapper.

- `SmolVLM-256M-Instruct.axera`: Axera-optimized build and supporting files for the SmolVLM 256M instruct model. Includes conversion outputs, C++ examples, and Python helpers tailored to Axera deployments.
	- How this helps the Project Vision:
		- **Axera-optimized artifacts & helpers** — use the exported axmodels and the Python examples to build production endpoints running on Axera hardware.
		- **Model conversion & packaging** — conversion and packaging scripts here are reusable to scale to other small models we wish to offer as endpoints.

- `init_submodules.sh` (script): Helper script to initialize the repository's submodules. Use this to fetch and initialize each referenced submodule into the workspace.
	- How this helps the Project Vision:
		- **Repo bootstrap** — speeds environment setup and ensures the submodule workflow is reproducible.

- `urls_of_source_repos_and_pages.md` (doc): A mapping of upstream source URLs, mirrors, and reference pages for the various submodules and third-party components maintained in this folder.
	- How this helps the Project Vision:
		- **External references** — easily locate model sources, conversion tooling, and upstream doc references when adding new models or validating SDK/tooling versions (Goal 1 & 2).

---

## Recommended Implementation Approaches

Based on the reality checks above, here are the viable paths forward:

### For LLM Chat Completion (Success Metric 1):

**Option A: Wrap existing C++ binary (faster to deploy)**
- ✅ Use pre-built `main_axcl_aarch64` or `main_ax650` binaries from Qwen3-4B or ax-llm
- ✅ Run separate tokenizer Python service (e.g., `qwen3_tokenizer_uid.py`)
- ✅ Build thin FastAPI/Flask wrapper that proxies requests to C++ HTTP API (port 8000)
- ✅ Manages both services via systemd for persistence
- ⚠️ Maintains two-process architecture, harder to debug, less Pythonic
- **❌ CRITICAL LIMITATION**: The C++ server maintains **ONE SINGLE GLOBAL CONVERSATION STATE** (`Worker worker` with one set of `k_caches`, `v_caches`, `last_reply`). It does NOT support multiple independent client conversations - all requests append to the same conversation history.
- **❌ This breaks multi-client requirement**: "Each request should be considered to be fresh and independent" is NOT possible without calling `/api/reset` between requests, which would disrupt concurrent clients.
- **Models stay loaded**: ✅ YES - model is loaded once at startup and kept in memory
- **Multi-client independent conversations**: ❌ NO - needs significant modification to add session management (map of session_id -> conversation state)

**Option B: Pure Python implementation (more work, cleaner)**
- 🔧 Use PyAXEngine to load axmodel files from Python
- 🔧 Reimplement LLM inference logic (prefill, decode loop, KV cache management) - significant work
- 🔧 Use transformers library for tokenization (no separate service needed)
- 🔧 Build FastAPI server with streaming responses
- 🔧 Add session management for per-client conversation state
- ⚠️ May not achieve same performance as optimized C++ runtime
- ⚠️ PyAXEngine noted as "prototyping tool" not production-ready for M.2 cards
- **Models stay loaded**: ✅ YES - can load models once and keep in memory
- **Multi-client independent conversations**: ✅ YES - can implement session-based state management

**Recommended**: **Option B is now required** for independent multi-client conversations. Option A would need significant C++ modifications to add session management (defeating the "wrap existing binary" advantage).

### For Stable Diffusion Image Generation (Success Metric 2):

**Option C: Extend existing Python scripts (straightforward)**
- ✅ Use `run_txt2img_axe_infer.py` and `run_img2img_axe_infer.py` as reference
- ✅ Refactor to load models once (global or class-level), not per-request
- ✅ Wrap in FastAPI with endpoints like `/v1/txt2img` and `/v1/img2img`
- ✅ Return images as base64 or save to disk and return URLs
- ✅ Pure Python, uses PyAXEngine (simple, clean)
- ✅ Aligns well with Goal 5 (Python preferred)

**Recommended**: **Option C** is the clear winner - already working Python code, just needs API wrapper.

---

Note: Priorities for the `PROJECT_VISION.md` goals

- **Highest**: `ax-llm`, `pyaxcl`, `PyAXEngine`, `Qwen3-4B`, `sd1.5-lcm.axera` — These provide the most practical building blocks. **sd1.5-lcm.axera** is closest to production Python pattern. **ax-llm** has working API but requires C++/Python split. **Qwen3-4B** has pre-built binaries + models.
- **High**: `Qwen3-VL.AXERA`, `SmolVLM-256M-Instruct`, `SmolVLM-256M-Instruct.axera` — VLM support for vision-language tasks. Similar architecture challenges as LLMs.
- **Medium**: `ax-pipeline`, `axcl-docs`, `axcl-samples`, `pulsar2-docs` — Infrastructure, toolchain, docs, and sample code for packaging and production deployments. Essential for understanding but not directly used in runtime services.
- **Utility**: `init_submodules.sh`, `urls_of_source_repos_and_pages.md` — Useful bootstrapping and reference information.

## Action Items

1. **For Chat Completion Service**: **Option B (Pure Python) is now strongly recommended** due to multi-client requirement. Option A's C++ binary only supports single conversation state and would need major modifications to add session management.

2. **For Image Generation Service**: Extend sd1.5-lcm.axera Python scripts with FastAPI wrapper (Option C). Most straightforward path and already supports stateless per-request inference.

3. **Device Monitoring (Goal 4)**: Use `axcl-smi` command-line tool (from pyaxcl README examples) for health checks. Can call via subprocess from Python service.

4. **Don't assume**: 
   - ❌ Gradio is not a server - it's a client UI
   - ❌ Examples are not production services - they're one-shot demo scripts
   - ❌ Python-only LLM runtime doesn't exist out-of-box - need to build or wrap C++
   - ❌ C++ API server supports multi-client conversations - it's single-state only
   - ✅ Stable Diffusion Python scripts are reusable with minimal changes
   - ✅ C++ API server keeps models loaded in memory
   - ✅ Models stay loaded with both Option A and Option B - no reload overhead


