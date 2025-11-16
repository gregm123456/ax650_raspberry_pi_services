# Contributing

This file documents how to work with the repository and its included upstream forks as git submodules.

Working with submodules
- Initialize and update submodules: `git submodule update --init --recursive`
- Clone with submodules: `git clone --recurse-submodules <repo-url>`
- Pull updates for all submodules: `git submodule foreach --recursive git pull --rebase origin main || git pull origin main`
- Add a new forked repo as a submodule: `git submodule add <url> reference_projects_and_documentation/<name>`

When to fork vs submodule
- If you expect to make local changes and contribute back, fork the upstream and add the *fork* as a submodule. Maintain upstream via a separate remote named `upstream` on the fork.

Large files and model weights
- Do not commit large model weights. Keep them in a model manifest and download at runtime or keep them on HF, S3, or GitHub Releases.

Branch naming
- The main branch used in this repo is `main`. Submodules may track other default branches; please verify and update them if needed.
