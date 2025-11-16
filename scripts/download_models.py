#!/usr/bin/env python3
"""
Simple helper to read `models_manifest.yml` and print commands to download model artifacts.
This is a lightweight helper that demonstrates the preferred workflow: keep models outside git and fetch at build/runtime.
"""
import yaml
import os
import textwrap

MANIFEST = os.path.join(os.path.dirname(__file__), "..", "models_manifest.yml")


def main():
    with open(MANIFEST, "r") as fh:
        manifest = yaml.safe_load(fh)
    for m in manifest.get("models", []):
        print("# Model:", m.get("id"))
        if m.get("location") == "huggingface":
            print(
                textwrap.dedent(
                    f"""
                    # Download from Hugging Face Hub for {m.get('id')}:
                    # Install: pip install huggingface_hub
                    # Example (huggingface_hub):
                    # from huggingface_hub import snapshot_download
                    # snapshot_download(repo_id='{m.get('id')}', cache_dir='./models/{m.get('id').replace('/', '_')}')
                    """
                )
            )
        else:
            print(f"# model location for {m.get('id')} is {m.get('location')}; add a download method")


if __name__ == "__main__":
    main()
