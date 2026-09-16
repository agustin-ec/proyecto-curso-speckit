"""Test pyproject.toml configuration (T002)."""

from pathlib import Path
import sys

# Python 3.11+ built-in tomllib
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


def test_pyproject_exists_and_parses():
    """Verify pyproject.toml exists and is valid TOML."""
    root = Path(__file__).parent.parent
    pyproject_file = root / "pyproject.toml"
    assert pyproject_file.is_file(), "pyproject.toml does not exist"

    with open(pyproject_file, "rb") as f:
        data = tomllib.load(f)
    assert "project" in data, "Missing [project] section in pyproject.toml"


def test_required_dependencies_declared():
    """Verify all required runtime and dev dependencies are declared."""
    root = Path(__file__).parent.parent
    with open(root / "pyproject.toml", "rb") as f:
        data = tomllib.load(f)

    deps = " ".join(data.get("project", {}).get("dependencies", []))
    required_deps = [
        "fastapi",
        "uvicorn[standard]",
        "sqlalchemy",
        "alembic",
        "pyjwt",
        "passlib[bcrypt]",
        "bcrypt<4.1",
        "pydantic-settings",
        "email-validator",
        "python-multipart",
        "mcp",
    ]
    for dep in required_deps:
        assert dep in deps, f"Required dependency missing: {dep}"

    dev_deps = " ".join(
        data.get("project", {}).get("optional-dependencies", {}).get("dev", [])
    )
    for dev_dep in ["pytest", "pytest-cov", "httpx"]:
        assert dev_dep in dev_deps, f"Required dev dependency missing: {dev_dep}"


def test_coverage_exclusions_configured():
    """Verify Constitution Article VII.3 coverage exclusions are configured."""
    root = Path(__file__).parent.parent
    with open(root / "pyproject.toml", "rb") as f:
        data = tomllib.load(f)

    coverage_run = data.get("tool", {}).get("coverage", {}).get("run", {})
    assert coverage_run.get("source") == ["app"], "Coverage source must be ['app']"

    omitted = coverage_run.get("omit", [])
    expected_omitted = [
        "app/main.py",
        "app/mcp/server.py",
        "app/mcp/auth.py",
        "app/logging_config.py",
    ]
    for pattern in expected_omitted:
        assert pattern in omitted, f"Missing coverage omission required by Art VII.3: {pattern}"
