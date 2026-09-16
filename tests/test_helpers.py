"""Test pure utility functions and independence (T009)."""

import ast
from pathlib import Path
from app.utils.helpers import clean_string, round_currency, format_currency


def test_clean_string():
    """Verify clean_string trims whitespace and handles None."""
    assert clean_string("  hola mundo  ") == "hola mundo"
    assert clean_string("   ") == ""
    assert clean_string(None) == ""
    assert clean_string("gasto") == "gasto"


def test_currency_functions():
    """Verify currency rounding and formatting."""
    assert round_currency(10.555) == 10.56
    assert round_currency(500.0) == 500.0
    assert format_currency(45.5) == "$45.50"
    assert format_currency(500) == "$500.00"


def test_helpers_has_no_disallowed_imports():
    """Verify app/utils/helpers.py does not import services, routers, or repositories per Art. I.4."""
    helpers_path = Path(__file__).parent.parent / "app" / "utils" / "helpers.py"
    tree = ast.parse(helpers_path.read_text(encoding="utf-8"))

    disallowed = {"services", "routers", "repositories", "app.services", "app.routers", "app.repositories"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                for d in disallowed:
                    assert not name.name.startswith(d), f"Disallowed import in utils: {name.name}"
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            for d in disallowed:
                assert not mod.startswith(d), f"Disallowed from-import in utils: {mod}"
