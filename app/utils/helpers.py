"""Pure helper utility functions (Constitution Article I.4).

These functions are strictly pure: deterministic (same input -> same output),
free of side-effects, and do NOT import anything from services, routers, or repositories.
"""


from decimal import Decimal, ROUND_HALF_UP


def clean_string(value: str | None) -> str:
    """Trim leading/trailing whitespace; returns empty string if None."""
    if value is None:
        return ""
    return value.strip()


def round_currency(amount: float) -> float:
    """Round monetary amount to two decimal places using standard ROUND_HALF_UP."""
    d = Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return float(d)


def format_currency(amount: float) -> str:
    """Format numeric monetary amount as a standardized currency string."""
    rounded = round_currency(amount)
    return f"${rounded:.2f}"
