"""Test tests/__init__.py existence and package importability (T004)."""

import importlib
from pathlib import Path


def test_tests_init_file_exists():
    """Verify tests/__init__.py exists per Constitution Article VIII.1."""
    root = Path(__file__).parent.parent
    init_file = root / "tests" / "__init__.py"
    assert init_file.is_file(), "tests/__init__.py is required by Constitution Article VIII.1"


def test_tests_package_is_importable():
    """Verify tests package can be imported directly."""
    tests_pkg = importlib.import_module("tests")
    assert tests_pkg is not None, "tests package must be importable"
