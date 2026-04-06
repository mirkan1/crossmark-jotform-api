from typing import Any

def fix_query_key(key: str) -> str:
    """ Ensures that the query key starts with 'q'. If it doesn't, prepends 'q' to the key."""
    if not key.startswith("q"):
        return "q" + key
    return key

def parse_boolean(s: Any) -> bool:
    """Takes a string and returns the equivalent as a boolean value."""
    if not s:
        return False
    if isinstance(s, bool):
        return s
    elif not isinstance(s, str):
        raise TypeError("Expected a string")
    s = s.strip().lower()
    if s in ("yes", "true", "on", "1"):
        return True
    elif s in ("no", "false", "off", "0", "none"):
        return False
    else:
        raise ValueError(f"Invalid boolean value {s}")