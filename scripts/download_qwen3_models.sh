#!/usr/bin/env bash
set -euo pipefail

# Download converted Qwen3-4B artifacts from Hugging Face into the repo's reference folder.
# This keeps large model blobs out of Git while providing a repeatable script to fetch them.

REPO_DIR="reference_projects_and_documentation/Qwen3-4B"
MODEL_SUBPATH="qwen3-4b-ax650"
HF_REPO="AXERA-TECH/Qwen3-4B"

echo "Downloading Qwen3-4B assets into ${REPO_DIR}/${MODEL_SUBPATH}"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required" >&2
  exit 1
fi

# Ensure huggingface_hub is installed in the active Python environment
python3 - <<PY - 2>/dev/null || true
import sys
try:
    import huggingface_hub
except Exception:
    sys.exit(1)
sys.exit(0)
PY

if [ $? -ne 0 ]; then
  echo "Installing huggingface_hub into the current Python environment..."
  python3 -m pip install --upgrade huggingface_hub
fi

mkdir -p "${REPO_DIR}"

python3 - <<PY
from huggingface_hub import snapshot_download
import os

repo_id = "${HF_REPO}"
local_dir = os.path.join(os.getcwd(), "${REPO_DIR}")
patterns = [f"${MODEL_SUBPATH}/*"]

print(f"Snapshot downloading {repo_id} -> {local_dir} (patterns={patterns})")
snapshot_download(
    repo_id=repo_id,
    local_dir=local_dir,
    allow_patterns=patterns,
    resume_download=True,
)
print("Download complete")
PY

echo "Model files should now be under ${REPO_DIR}/${MODEL_SUBPATH}"
du -sh "${REPO_DIR}/${MODEL_SUBPATH}" || true
