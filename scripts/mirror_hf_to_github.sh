#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <huggingface-repo-url> <github-repo-url> [--clean]"
  echo "Example: $0 https://huggingface.co/AXERA-TECH/PyAXEngine git@github.com:gregm123456/PyAXEngine.git --clean"
  exit 1
fi

HF_URL="$1"
GH_URL="$2"
DO_CLEAN=false
if [ "${3:-}" = "--clean" ]; then
  DO_CLEAN=true
fi

NAME=$(basename "$HF_URL" | sed 's/.git$//; s/.axera$//; s/\//-/g')
MIRROR_DIR="hf_mirrors/${NAME}.git"
WORK_DIR="reference_projects_and_documentation/huggingface_mirrors/${NAME}"

mkdir -p hf_mirrors reference_projects_and_documentation/huggingface_mirrors

if [ ! -d "$MIRROR_DIR" ]; then
  echo "Creating bare mirror $MIRROR_DIR from $HF_URL"
  git clone --mirror "$HF_URL" "$MIRROR_DIR"
else
  echo "Mirror already exists: $MIRROR_DIR"
fi

if [ -d "$WORK_DIR" ]; then
  echo "Work dir already exists, updating from mirror: $WORK_DIR"
  pushd "$WORK_DIR" >/dev/null
  git fetch origin
  popd >/dev/null
else
  echo "Creating working clone $WORK_DIR from mirror"
  git clone "$MIRROR_DIR" "$WORK_DIR"
fi

if [ "$DO_CLEAN" = true ]; then
  ./scripts/clean_hf_repo.sh "$WORK_DIR"
fi

echo "Preparing to push mirror to GitHub: $GH_URL"
pushd "$WORK_DIR" >/dev/null
if ! git remote | grep -q github; then
  git remote add github "$GH_URL"
else
  git remote set-url github "$GH_URL"
fi

echo "Run this command to verify and push to GitHub (you will need appropriate credentials):"
echo "  cd \"$WORK_DIR\" && git push --mirror github"
popd >/dev/null

echo "Mirror and working clone are ready. Pushing is a manual step to allow credential handling and safe review."
