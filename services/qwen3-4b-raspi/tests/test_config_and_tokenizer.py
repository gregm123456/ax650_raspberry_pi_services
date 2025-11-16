import sys
import pathlib

# Ensure the service src directory is on sys.path for imports during tests
HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE.parent / "src"
sys.path.insert(0, str(SRC))

import config
import tokenizer


def test_settings_defaults():
    assert config.settings.MAX_CONTEXT_TOKENS >= 1


def test_tokenizer_fallback():
    t = tokenizer.load_tokenizer(None)
    enc = t.encode("hello world")
    assert isinstance(enc, list)
    dec = t.decode(enc)
    assert isinstance(dec, str)
