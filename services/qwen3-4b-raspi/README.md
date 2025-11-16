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
