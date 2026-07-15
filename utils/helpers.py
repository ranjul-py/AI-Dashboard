def format_currency(val: float) -> str:
    """Formats numerical values to currency, e.g., $1.70M or $250K."""
    if val >= 1_000_000:
        return f"${val / 1_000_000:.2f}M"
    elif val >= 1_000:
        return f"${val / 1_000:.0f}K"
    else:
        return f"${val:.2f}"

def format_percent(val: float) -> str:
    """Formats percentage values."""
    return f"{val:.1f}%"
