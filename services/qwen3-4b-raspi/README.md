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

This will populate `reference_projects_and_documentation/Qwen3-4B/qwen3-4b-ax650/` with the converted model artifacts.

### Starting all services (real device)

**Prerequisites:**
- AX650/LLM8850 hardware with AXCL runtime installed
- Project virtualenv activated
- AXCL environment sourced

**Step 1: Stop any existing services**

```bash
pkill -f qwen3_tokenizer_uid.py
pkill -f main_api_axcl_aarch64
pkill -f uvicorn
```

**Step 2: Start tokenizer service**

```bash
cd /home/robot/ax650_raspberry_pi_services/reference_projects_and_documentation/Qwen3-4B
source /etc/profile
source /home/robot/ax650_raspberry_pi_services/.venv/bin/activate
nohup python qwen3_tokenizer_uid.py \
  > /home/robot/ax650_raspberry_pi_services/qwen3_tokenizer.log 2>&1 &
echo $! > /home/robot/ax650_raspberry_pi_services/qwen3_tokenizer.pid
```

**Step 3: Start AX runtime (takes ~90 seconds to load)**

```bash
cd /home/robot/ax650_raspberry_pi_services/reference_projects_and_documentation/Qwen3-4B
source /etc/profile
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
  --devices 0 \
  > /home/robot/ax650_raspberry_pi_services/qwen3_runtime.log 2>&1 &
echo $! > /home/robot/ax650_raspberry_pi_services/qwen3_runtime.pid

# Wait for model to load (~90 seconds)
echo "Waiting for runtime to load model..."
sleep 95
tail -n 20 /home/robot/ax650_raspberry_pi_services/qwen3_runtime.log
```

**Step 4: Start FastAPI service**

```bash
cd /home/robot/ax650_raspberry_pi_services/services/qwen3-4b-raspi/src
source /etc/profile
source /home/robot/ax650_raspberry_pi_services/.venv/bin/activate
nohup uvicorn api:app --host 0.0.0.0 --port 8080 --log-level info \
  > /home/robot/ax650_raspberry_pi_services/fastapi.log 2>&1 &
echo $! > /home/robot/ax650_raspberry_pi_services/fastapi.pid
```

**Step 5: Test end-to-end**

```bash
# Health check
curl -sS http://127.0.0.1:8080/health

# Chat completion request
curl -sS -X POST http://127.0.0.1:8080/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3-4b",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Say hello in one sentence."}
    ]
  }' | jq .

# Another test
curl -sS -X POST http://127.0.0.1:8080/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3-4b",
    "messages": [
      {"role": "user", "content": "What is 2+2? Answer in one word."}
    ]
  }' | jq -r '.choices[0].message.content'
```

**Monitoring logs:**

```bash
# View tokenizer log
tail -f /home/robot/ax650_raspberry_pi_services/qwen3_tokenizer.log

# View runtime log
tail -f /home/robot/ax650_raspberry_pi_services/qwen3_runtime.log

# View FastAPI log
tail -f /home/robot/ax650_raspberry_pi_services/fastapi.log
```

**Stopping services:**

```bash
kill $(cat /home/robot/ax650_raspberry_pi_services/qwen3_tokenizer.pid)
kill $(cat /home/robot/ax650_raspberry_pi_services/qwen3_runtime.pid)
kill $(cat /home/robot/ax650_raspberry_pi_services/fastapi.pid)
```

