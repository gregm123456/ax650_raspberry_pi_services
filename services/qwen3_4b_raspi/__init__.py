"""Package shim to expose the implementation under a valid Python package name.

This file adds the real source directory (which contains a hyphen in its name)
to sys.path so imports like `services.qwen3_4b_raspi.src` work in development.
"""
from __future__ import annotations
import os
import sys

# Determine the real implementation path (services/qwen3-4b-raspi/src)
HERE = os.path.dirname(__file__)
# Path to the implementation package directory (services/qwen3-4b-raspi)
impl_pkg = os.path.normpath(os.path.join(HERE, "..", "qwen3-4b-raspi"))
# Make the package import machinery search the hyphenated implementation dir
if impl_pkg not in __path__:
    __path__.insert(0, impl_pkg)

# Also add the src directory to sys.path for direct imports if needed
impl_src = os.path.join(impl_pkg, "src")
if os.path.isdir(impl_src) and impl_src not in sys.path:
    sys.path.insert(0, impl_src)

__all__ = []
