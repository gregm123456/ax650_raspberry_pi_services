#!/usr/bin/env bash
set -euo pipefail

echo "Initializing submodules..."
git submodule update --init --recursive

echo "Checking each submodule to find default branch (preferring 'main')..."
# Loop over submodule paths from .gitmodules and set a branch preference to 'main' if the remote supports it
while IFS= read -r line; do
  path="$line"
  url=$(git config -f .gitmodules --get "submodule.$path.url")
  if git ls-remote --exit-code --heads "$url" main >/dev/null 2>&1; then
    echo "Setting branch 'main' for submodule $path"
    git config -f .gitmodules "submodule.$path.branch" "main"
  else
    echo "Submodule $path: no 'main' branch available on remote; keeping default"
  fi
done < <(git config -f .gitmodules --get-regexp '^submodule\..*\.path' | awk '{print $2}')

echo "Syncing and updating submodules after branch preference adjustments..."
git submodule sync --recursive
git submodule update --init --recursive

echo "Submodules initialized. See README_SUBMODULES.md for more details."
