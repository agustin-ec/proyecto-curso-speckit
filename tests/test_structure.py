"""Test project directory and package structure (T001)."""

import importlib
import os
import sys
from pathlib import Path

# Add project root to sys.path
root = Path(__file__).parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))


def test_package_directories_exist():
    """Verify all planned package directories exist and contain __init__.py."""
    root = Path(__file__).parent.parent
    expected_packages = [
        "app",
        "app/core",
        "app/models",
        "app/schemas",
        "app/repositories",
        "app/services",
        "app/routers",
        "app/utils",
        "app/mcp",
        "app/mcp/tools",
    ]

    for pkg in expected_packages:
        pkg_dir = root / pkg
        assert pkg_dir.is_dir(), f"Package directory missing: {pkg}"
        init_file = pkg_dir / "__init__.py"
        assert init_file.is_file(), f"Missing __init__.py in: {pkg}"


def test_alembic_versions_directory_exists():
    """Verify alembic/versions directory exists."""
    root = Path(__file__).parent.parent
    versions_dir = root / "alembic" / "versions"
    assert versions_dir.is_dir(), "Alembic versions directory missing"


def test_packages_importable():
    """Verify app and subpackages are importable Python modules."""
    modules = [
        "app",
        "app.core",
        "app.models",
        "app.schemas",
        "app.repositories",
        "app.services",
        "app.routers",
        "app.utils",
        "app.mcp",
        "app.mcp.tools",
    ]
    for mod in modules:
        imported = importlib.import_module(mod)
        assert imported is not None, f"Could not import module: {mod}"
