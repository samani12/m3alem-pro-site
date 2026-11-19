"""Locale-tolerant parsing helpers for Search Console CSV imports."""

def parse_number(value):
    """Parse common English/French CSV numbers without misreading decimal commas."""
    raw = str(value or "").strip().replace("\\u00a0", "").replace(" ", "")
    if not raw:
        return 0.0
    raw = raw.replace("%", "")
    if "," in raw and "." not in raw and raw.count(",") == 1:
        left, right = raw.split(",")
        raw = left + "." + right if len(right) <= 2 else left + right
    else:
        raw = raw.replace(",", "")
    try:
        return float(raw)
    except ValueError:
        return 0.0
