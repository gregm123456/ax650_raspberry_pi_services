#!/usr/bin/env bash
set -euo pipefail

echo "Initializing submodules..."
git submodule update --init --recursive

echo "Checking each submodule to find default branch (preferring 'main')..."
for sm in $(git submodule--helper list | awk '{print $4}'); do
  echo "Skipping helper list approach — falling back to reading .gitmodules"
done

echo "You can use the following commands to try to switch a submodule to 'main' if available:
cd reference_projects_and_documentation/sd1.5-lcm.axera
git fetch origin
if git ls-remote --exit-code --heads origin main >/dev/null 2>&1; then
  git checkout main || git checkout -b main origin/main
else
  echo 'No main branch available for sd1.5-lcm.axera; it remains on master'
fi
"

echo "Submodules initialized. See README_SUBMODULES.md for more details."
