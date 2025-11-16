# Hugging Face → GitHub Mirror & Clean Workflow

This document captures the minimal, repeatable steps to mirror code from Hugging Face repos into GitHub without carrying large model weight files into your Git repository.

Overview
- We maintain two copies for each Hugging Face repo: a bare mirror in `hf_mirrors/` and a working clone in `reference_projects_and_documentation/huggingface_mirrors/`.
- The workflow emphasizes not storing model weights in Git: either keep them on HF (preferred), host them on an object store (S3/GCS), or use Git LFS with a careful policy.

Prereqs
- Homebrew: `git-lfs`, `git-filter-repo` installed (we use `brew install git-lfs git-filter-repo`).
- `gh` (GitHub CLI) optional for repo creation, or create repos manually in GitHub.
- A GitHub account and SSH or HTTPS credentials (we recommend SSH or `gh` auth).

Quick Commands
- Clone HF repo as a bare mirror:
```bash
git clone --mirror https://huggingface.co/AXERA-TECH/PyAXEngine hf_mirrors/PyAXEngine.git
```
- Create a working clone:
```bash
git clone hf_mirrors/PyAXEngine.git reference_projects_and_documentation/huggingface_mirrors/PyAXEngine
```
- Clean history/remove large blobs (destructive; create a backup bundle first):
```bash
./scripts/clean_hf_repo.sh reference_projects_and_documentation/huggingface_mirrors/PyAXEngine
```

Push to GitHub (manual step):
1. Create the new GitHub repo (via `gh` or the web):
```bash
gh repo create gregm123456/PyAXEngine --public --source=. --push
```
2. Or add a remote and push the mirror (manual):
```bash
cd reference_projects_and_documentation/huggingface_mirrors/PyAXEngine
git remote add github git@github.com:gregm123456/PyAXEngine.git
git push --mirror github
```

Notes on LFS and models
- If the HF repo uses LFS for large model objects, you'll see `.gitattributes` entries and pointer files (small) in the repo. If you want to _not_ keep the large files in GitHub, keep the pointers or strip the files and use HF to serve the weights.
- If you prefer to host model weights in S3/other object storage, add a small `models_manifest.yml` that points to the original HF model IDs and provides checksums.

Security & license
- Verify licenses for each HF repo before mirroring and distributing code.
- Do not push model weights or private keys to the mirrored repo. Use `git-filter-repo` to remove them from history if needed.

Next steps
- Choose one of the HF repos to push to GitHub as a trial following these steps (I can prepare the repo and the push commands), then add the GitHub repo as a submodule to this repo if desired.
