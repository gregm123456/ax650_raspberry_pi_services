import sys
import pathlib

# Ensure the service src directory is on sys.path for imports during tests
HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE.parent / "src"
sys.path.insert(0, str(SRC))

import runtime_adapter
import config


def test_mock_runtime_reset_then_chat():
    orig = config.settings.MOCK_RUNTIME
    config.settings.MOCK_RUNTIME = True
    try:
        adapter = runtime_adapter.RuntimeAdapter()
        resp = adapter.reset_then_chat(system_prompt="You are helpful.", messages=[{"role":"user","content":"Hi"}])
        assert isinstance(resp, dict)
        assert "text" in resp
    finally:
        config.settings.MOCK_RUNTIME = orig
