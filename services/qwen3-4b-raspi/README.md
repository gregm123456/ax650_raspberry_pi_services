Qwen3-4B Raspberry Pi AX650 Service
=================================

Lightweight FastAPI wrapper and runtime adapter to host Qwen3-4B on AX650/LLM8850 hardware.

Quickstart (development):

1. Create a virtualenv and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r services/qwen3-4b-raspi/requirements.txt
```

2. Run the service (development):

```bash
uvicorn services.qwen3_4b_raspi.src.api:app --host 127.0.0.1 --port 8080 --reload
```

Notes:
- By default the runtime adapter tries to connect to a runtime at `http://127.0.0.1:8000`.
- For development without the AX runtime, set `QWEN3_MOCK_RUNTIME=1` to use a lightweight mock runtime.

Model setup (real device)
--------------------------

The converted Qwen3-4B axmodel files are large and are not included in this repository. Use the helper script to download them from the official AXERA-TECH Hugging Face repo before attempting a real-device test:

```bash
./scripts/download_qwen3_models.sh
```

This will populate `reference_projects_and_documentation/Qwen3-4B/qwen3-4b-ax650/` with the converted model artifacts. After download, start the tokenizer service and the AX runtime (see `reference_projects_and_documentation/Qwen3-4B/README.md`):

```bash
# start tokenizer
cd reference_projects_and_documentation/Qwen3-4B
python3 qwen3_tokenizer_uid.py --host 127.0.0.1 --port 12345 &

# start AX runtime (on device with AX650/LLM8850 and AXCL available)
./run_qwen3_4b_int8_ctx_ax650.sh
```

Then set the Python service to use the real runtime and start it (unset mock):

```bash
export QWEN3_MOCK_RUNTIME=0
export RUNTIME_HOST=127.0.0.1
export RUNTIME_PORT=8000
uvicorn services.qwen3_4b_raspi.src.api:app --host 127.0.0.1 --port 8080
```

