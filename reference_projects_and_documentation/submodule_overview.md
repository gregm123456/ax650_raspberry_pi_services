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
		- **✅ CRITICAL - Primary API reference** — Contains complete documentation of Runtime API (`axclrt*`) and Native API (`AXCL_*`) functions needed for all device operations.
		- **✅ Device monitoring documentation** — Documents `axcl-smi` tool which provides temperature, memory, CPU/NPU usage monitoring - essential for Goal 4 (device health monitoring).
		- **✅ Memory architecture explained** — Clarifies System Memory (~945MB) vs CMM (~7040MB) distinction, critical for understanding model persistence (Goal 3).
		- **✅ Error handling reference** — Documents AXCL error codes and proper cleanup sequences (`axclInit` → `axclrtSetDevice` → work → `axclrtResetDevice` → `axclFinalize`).
		- **🔍 VALIDATED**: Hardware interaction strategy document confirms these docs are authoritative source for production implementation patterns.

- `axcl-samples`: Practical sample applications and CMake examples demonstrating how to use AXCL. Contains minimal example projects, sample build setups, and usage patterns for integrating AXCL into applications.
	- How this helps the Project Vision:
		- **✅ Reference implementation patterns** — `axcl_sample_runtime`, `axcl_sample_memory`, `axcl_sample_sys` demonstrate correct initialization/cleanup sequences.
		- **✅ Device monitoring examples** — `axcl_sample_runtime` shows how to query `axclrtDeviceProperties` for temperature, memory, CPU/NPU usage (Goal 4).
		- **✅ Memory management patterns** — `axcl_sample_memory` demonstrates `axclrtMalloc`, `axclrtMemcpy` (Host↔Device, Device↔Device), `axclrtMemset` for buffer initialization.
		- **✅ Model execution patterns** — Shows proper context creation, buffer allocation, and model lifecycle for persistent operation (Goal 3).
		- **🔍 VALIDATED**: Hardware strategy document extracted initialization flows and best practices directly from these samples (`axcl_sample_runtime` → Section 2.2 initialization flow).

- `pulsar2-docs`: Documentation repository for the Pulsar2 project. Provides user-facing and developer documentation, build instructions, and any project-specific guides housed separately from code samples.
	- How this helps the Project Vision:
		- **Model conversion & toolchain docs** — Pulsar2 docs contain exact steps for converting Huggingface models to Axera formats (axmodel/quantization) and are key for adding new models (Goal 2 & non-goal note on avoiding upstream changes).
		- **Operational guidance** — compatibility and operation notes for Pulsar2 tools will help ensure conversion workflows are repeatable and documented.

- `pyaxcl`: Python package and bindings for AXCL. Contains `setup.py`, packaging metadata, sample code, and tests for the Python-facing APIs that wrap the AXCL runtime.
	- How this helps the Project Vision:
		- **✅ Low-level Python control** — Provides `axcl.rt` module with direct wrappers for `axclrtMalloc`, `axclrtMemcpy`, `axclrtEngineLoadFromFile` etc. (Goal 5: Python-first).
		- **✅ Device health monitoring via Python** — Can query `axclrtDeviceProperties` for temperature (in millidegrees), CPU/NPU loading, memory usage programmatically.
		- **✅ Complete API coverage** — Wraps both Runtime API (NPU inference) and Native API (VDEC, VENC, IVPS, IVE) for full hardware access.
		- **⚠️ Reality check** — Sample code (`sample/engine/sample_engine.py`) shows **one-shot inference** pattern (load model, run, exit). No built-in API server or persistent model hosting.
		- **⚠️ Steeper learning curve** — Low-level C-like API requiring manual memory management (`axclrtMalloc`/`axclrtFree`).
		- **🔧 Recommended use** — Device health monitoring, low-level control. For model inference, PyAXEngine provides simpler high-level API.
		- **🔍 VALIDATED**: Hardware strategy confirms pyaxcl is production-ready but lower-level than needed for rapid development.

- `PyAXEngine`: Prebuilt Python wheel and runtime configuration for the Axera inference engine. This repo packages a ready-to-install wheel and config files used to run models with the Axera engine from Python.
	- How this helps the Project Vision:
		- **✅ PREFERRED for rapid development** — Provides ONNX Runtime-style API (`axengine.InferenceSession`) for loading and running axmodel files directly from Python (Goal 5).
		- **✅ Proven in Stable Diffusion examples** — Used successfully in `sd1.5-lcm.axera/python/` scripts. Can load models, run inference, minimal code needed.
		- **✅ Automatic memory management** — No manual `malloc`/`free` like pyaxcl. Handles device memory allocation internally.
		- **✅ Simple persistent model pattern** — Load once: `session = axengine.InferenceSession(model_path, device_id=0)`, then call `session.run()` repeatedly for each request.
		- **⚠️ Limitation from README** — Explicitly states it's "better suited for rapid prototyping" and "cannot call some codec-related modules on card environments". For production M.2 card deployments, recommends pyaxcl instead.
		- **⚠️ NPU inference only** — Cannot access Native API features (VDEC, VENC, IVPS). For pure model inference this is fine.
		- **🔧 Recommended use** — **PRIMARY CHOICE** for both LLM and SD services during development. Clean API, proven examples, fast iteration. Monitor for stability issues; can fall back to pyaxcl if needed.
		- **🔍 VALIDATED**: Hardware strategy confirms PyAXEngine is best for achieving "Python-first" goal despite "prototyping" caveat in README.

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

**Option A: Wrap existing C++ binary (faster to deploy) — ❌ NOT RECOMMENDED**
- ✅ Use pre-built `main_axcl_aarch64` or `main_ax650` binaries from Qwen3-4B or ax-llm
- ✅ Run separate tokenizer Python service (e.g., `qwen3_tokenizer_uid.py`)
- ✅ Build thin FastAPI/Flask wrapper that proxies requests to C++ HTTP API (port 8000)
- ✅ Manages both services via systemd for persistence
- ⚠️ Maintains two-process architecture, harder to debug, less Pythonic
- **❌ CRITICAL LIMITATION**: The C++ server maintains **ONE SINGLE GLOBAL CONVERSATION STATE** (`Worker worker` with one set of `k_caches`, `v_caches`, `last_reply`). It does NOT support multiple independent client conversations - all requests append to the same conversation history.
- **❌ This breaks multi-client requirement**: "Each request should be considered to be fresh and independent" is NOT possible without calling `/api/reset` between requests, which would disrupt concurrent clients.
- **Models stay loaded**: ✅ YES - model is loaded once at startup and kept in memory
- **Multi-client independent conversations**: ❌ NO - needs significant modification to add session management (map of session_id → conversation state)
- **🔍 HARDWARE VALIDATION**: Section 6.4 confirms this limitation and recommends Option B for multi-client support.

**Option B: Pure Python implementation (more work, cleaner) — ✅ RECOMMENDED**
- 🔧 Use PyAXEngine to load axmodel files from Python
- 🔧 Reimplement LLM inference logic (prefill, decode loop, KV cache management) - significant work
- 🔧 Use transformers library for tokenization (no separate service needed)
- 🔧 Build FastAPI server with streaming responses
- 🔧 Add session management for per-client conversation state
- ⚠️ May not achieve same performance as optimized C++ runtime (acceptable for interactive art installations)
- ⚠️ PyAXEngine noted as "prototyping tool" not production-ready for M.2 cards
- **Models stay loaded**: ✅ YES - can load models once and keep in memory
- **Multi-client independent conversations**: ✅ YES - can implement session-based state management
- **✅ HARDWARE VALIDATION**: Section 5.1 provides complete architecture diagram and code skeleton. Section 2.2 confirms `axclrtEngineLoadFromFile()` keeps models in CMM until `axclrtEngineUnload()` called.
- **✅ MEMORY CONFIRMED**: Section 1.2 shows ~7040 MB CMM available, enough for Qwen3-4B (~4GB) with headroom.
- **✅ DEVICE MONITORING**: Section 3 provides complete `axcl-smi` integration pattern for health checks.

**Recommended**: **Option B is now required** for independent multi-client conversations. Option A would need significant C++ modifications to add session management (defeating the "wrap existing binary" advantage).

### For Stable Diffusion Image Generation (Success Metric 2):

**Option C: Extend existing Python scripts (straightforward) — ✅ RECOMMENDED**
- ✅ Use `run_txt2img_axe_infer.py` and `run_img2img_axe_infer.py` as reference
- ✅ Refactor to load models once (global or class-level), not per-request
- ✅ Wrap in FastAPI with endpoints like `/v1/txt2img` and `/v1/img2img`
- ✅ Return images as base64 or save to disk and return URLs
- ✅ Pure Python, uses PyAXEngine (simple, clean)
- ✅ Aligns well with Goal 5 (Python preferred)
- **✅ HARDWARE VALIDATION**: Section 5.2 provides complete service architecture with code skeleton showing how to load text_encoder, unet, vae_decoder as separate `axengine.InferenceSession` instances.
- **✅ PROVEN PATTERN**: sd1.5-lcm.axera scripts already use PyAXEngine successfully - just need to move model loading outside request loop.
- **✅ MEMORY CONFIRMED**: Section 1.2 estimates SD 1.5 needs ~2-3GB CMM, well within available ~7040 MB.

**Recommended**: **Option C** is the clear winner - already working Python code, just needs API wrapper.

---

Note: Priorities for the `PROJECT_VISION.md` goals

- **Highest**: `ax-llm`, `pyaxcl`, `PyAXEngine`, `Qwen3-4B`, `sd1.5-lcm.axera`, `axcl-docs`, `axcl-samples`
  - **axcl-docs** & **axcl-samples**: ✅ **FOUNDATIONAL** - Complete API reference and working examples validated in hardware strategy doc (Sections 2.2, 3.1, 3.2). Essential for understanding Runtime API lifecycle, device monitoring patterns, and memory management.
  - **PyAXEngine**: ✅ **PRIMARY INFERENCE ENGINE** - Despite "prototyping" label, this is the recommended path for both services (validated in Section 4.2). Simple API, proven in SD examples, automatic memory management.
  - **sd1.5-lcm.axera**: ✅ **CLOSEST TO PRODUCTION** - Pure Python with PyAXEngine, just needs FastAPI wrapper (Section 5.2 provides complete skeleton). Est. 1-2 weeks to production.
  - **ax-llm**: ⚠️ **REFERENCE ONLY** - C++ implementation useful for understanding LLM inference patterns, but NOT recommended due to single-conversation limitation. Use as reference for KV cache strategies.
  - **pyaxcl**: ✅ **DEVICE MONITORING** - Used for programmatic health checks via `axclrtDeviceProperties` (Section 3.2), though `axcl-smi` subprocess is simpler (Section 4.3).
  - **Qwen3-4B**: ✅ **MODEL ARTIFACTS** - Pre-built axmodel files ready to use. Binaries not recommended, but model files + tokenizer are essential.

- **High**: `Qwen3-VL.AXERA`, `SmolVLM-256M-Instruct`, `SmolVLM-256M-Instruct.axera` — VLM support for vision-language tasks. Similar architecture challenges as LLMs. Will require same pure-Python approach.

- **Medium**: `ax-pipeline`, `pulsar2-docs` — Infrastructure, toolchain, docs for model conversion and packaging. Important for understanding but not directly used in runtime services. Refer to when adding new models.

- **Utility**: `init_submodules.sh`, `urls_of_source_repos_and_pages.md` — Useful bootstrapping and reference information.

## Action Items

1. **For Chat Completion Service**: **Option B (Pure Python) is now strongly recommended** due to multi-client requirement. Option A's C++ binary only supports single conversation state and would need major modifications to add session management.
   - **✅ STRATEGY CONFIRMED**: Hardware interaction document Section 5.1 provides complete FastAPI + PyAXEngine skeleton with lifespan management, device monitoring, and proper cleanup.
   - **Implementation path**: Load model once at startup with `axengine.InferenceSession`, implement session-based KV cache in Python, wrap in FastAPI.
   - **Est. 2-3 weeks** for MVP (per Phase 2 in hardware strategy doc).

2. **For Image Generation Service**: Extend sd1.5-lcm.axera Python scripts with FastAPI wrapper (Option C). Most straightforward path and already supports stateless per-request inference.
   - **✅ STRATEGY CONFIRMED**: Hardware interaction document Section 5.2 shows loading text_encoder, unet, vae_decoder as separate `axengine.InferenceSession` instances with persistent model hosting.
   - **Implementation path**: Refactor `run_txt2img_axe_infer.py` to load models in global scope, wrap denoising loop in FastAPI endpoint.
   - **Est. 1-2 weeks** (per Phase 3 in hardware strategy doc).

3. **Device Monitoring (Goal 4)**: 
   - **✅ PRIMARY METHOD**: Use `axcl-smi` CLI tool via subprocess (Section 4.3 of hardware strategy doc provides complete Python wrapper functions).
   - **✅ SECONDARY METHOD**: Direct API via `axclrtDeviceProperties` (Section 3.2 shows both C++ and Python patterns).
   - **Implementation**: Background thread calling `axcl-smi info --temp/--cmm/--cpu/--npu` every 10 seconds, with threshold-based alerting.
   - **Critical thresholds**: 75°C warning, 80°C critical (pause inference), timeout → device reset via `axcl-smi reboot`.

4. **Memory Management**:
   - **✅ CMM allocation confirmed**: ~7040 MB available for models. Qwen3-4B needs ~4GB, SD 1.5 needs ~2-3GB.
   - **⚠️ Concurrent operation**: May need model swapping if running both services simultaneously. Must measure actual CMM usage during testing.
   - **Best practice**: Load models once, reuse buffers across requests (no per-request malloc/free).

5. **Installation & Setup** (Phase 1 from hardware strategy):
   - Install pyaxcl: `pip install reference_projects_and_documentation/pyaxcl/`
   - Install PyAXEngine: `pip install reference_projects_and_documentation/PyAXEngine/axengine-0.1.3-py3-none-any.whl`
   - Verify: `axcl-smi -d 0` (should show device info)
   - Test: Run `sd1.5-lcm.axera/python/run_txt2img_axe_infer.py` to validate end-to-end inference.

6. **Don't assume**: 
   - ❌ Gradio is not a server - it's a client UI
   - ❌ Examples are not production services - they're one-shot demo scripts
   - ❌ Python-only LLM runtime doesn't exist out-of-box - need to build or wrap C++
   - ❌ C++ API server supports multi-client conversations - it's single-state only
   - ✅ Stable Diffusion Python scripts are reusable with minimal changes
   - ✅ C++ API server keeps models loaded in memory
   - ✅ Models stay loaded with both Option A and Option B - no reload overhead
   - **✅ NEW**: PyAXEngine is production-viable despite "prototyping" label - used successfully in SD examples, automatic memory management
   - **✅ NEW**: Device monitoring via `axcl-smi` subprocess is simpler and more reliable than direct API calls
   - **✅ NEW**: CMM memory pool is separate from system memory - models persist in CMM until explicitly unloaded


