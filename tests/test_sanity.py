from __future__ import annotations

import importlib
import sys


def test_python_version() -> None:
    major, minor = sys.version_info.major, sys.version_info.minor
    assert (major, minor) >= (3, 12), "Python 3.12+ is required"


def test_app_importable() -> None:
    module = importlib.import_module("app")
    assert module is not None
