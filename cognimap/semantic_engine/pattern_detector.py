import re


PATTERN_RULES = {
    "controller": re.compile(r"Controller$", re.IGNORECASE),
    "repository": re.compile(r"Repository$", re.IGNORECASE),
    "factory": re.compile(r"Factory$", re.IGNORECASE),
    "observer": re.compile(r"Observer$", re.IGNORECASE),
}


def detect_patterns(symbol_name: str):
    """Return a list of design pattern markers inferred from the symbol name."""
    matches = []
    for pattern, regex in PATTERN_RULES.items():
        if regex.search(symbol_name):
            matches.append(pattern)
    return matches
