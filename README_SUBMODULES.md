# Submodules and Upstream Forks

This repository includes multiple upstream forks located under `reference_projects_and_documentation/`. They are added as git submodules and point at your personal forks on GitHub. The main reasons for this layout are:
- Keep a clear separation between your customized forks and the main project code in this repo.
- Make it easy to sync changes from upstream and contribute back.

Key operations
- Initialize and update submodules:
```bash
git submodule update --init --recursive
```
- To fetch the latest upstream for a forked submodule, add an `upstream` remote in the submodule and pull from it:
```bash
cd reference_projects_and_documentation/ax-llm
git remote add upstream https://github.com/original/ax-llm
git fetch upstream
git merge upstream/main
# or rebase
git rebase upstream/main
```

Hugging Face repositories
- For Hugging Face-hosted models and code, we prefer not to store large model weight files in git. Instead:
  - Mirror code to GitHub if you want a Git-based workflow: `git clone --mirror https://huggingface.co/AXERA-TECH/PyAXEngine` then push to a GitHub repo.
  - Keep models on HF (or S3), and add a manifest or stable ID (HF model ID) in `models_manifest.yml`.

Cleaning large files from history
- If you accidentally push large model files, use `git-filter-repo` or `BFG Repo-Cleaner` to remove them and force-push the cleaned history.

Submodule branch management
- Submodule pointers track a specific commit; to change the commit or branch, update submodule content and commit the updated pointer in the parent repo:
```bash
cd reference_projects_and_documentation/ax-llm
git fetch upstream
git checkout main
git pull upstream main
# update parent pointer
cd ../../
git add reference_projects_and_documentation/ax-llm
git commit -m "chore: update ax-llm submodule to latest upstream/main"
```
