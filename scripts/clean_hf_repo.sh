#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <path-to-repo> [--strip-threshold=<bytes>]"
  exit 1
fi

REPO_PATH="$1"
STRIP_THRESHOLD="100M"
if [ "$#" -ge 2 ]; then
  STRIP_THRESHOLD="$2"
fi

echo "Cleaning repo: $REPO_PATH (strip blobs bigger than $STRIP_THRESHOLD)"
pushd "$REPO_PATH" >/dev/null

# Recommend using a fresh clone because filter-repo rewrites history
if ! [ -d .git ]; then
  echo "$REPO_PATH appears not to be a Git repository"
  exit 2
fi

echo "Creating backup bundle (safety)"
BACKUP="../$(basename "$REPO_PATH")-backup-$(date -u +%Y%m%dT%H%M%SZ).bundle"
git bundle create "$BACKUP" --all

echo "Running git-filter-repo to remove blobs larger than $STRIP_THRESHOLD"
# NOTE: git-filter-repo is destructive and requires a fresh clone or a backup bundle.
git filter-repo --strip-blobs-bigger-than "$STRIP_THRESHOLD"

echo "Cleaning stashed refs and running GC"
git reflog expire --expire=now --all || true
git gc --prune=now --aggressive || true

echo "Repository cleaned. Created backup bundle at $BACKUP"
popd >/dev/null
