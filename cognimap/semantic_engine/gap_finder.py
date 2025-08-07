from collections import defaultdict
from itertools import combinations


def find_gaps(symbols, connections, fingerprints):
    """Identify simple semantic gaps based on fingerprints and connections.

    If two symbols share a tag but have no direct connection, we mark this as a
    potential gap for further investigation.
    """
    tags_to_symbols = defaultdict(list)
    for sid, fp in fingerprints.items():
        for tag in fp["tags"]:
            tags_to_symbols[tag].append(sid)

    gaps = []
    for tag, syms in tags_to_symbols.items():
        for a, b in combinations(syms, 2):
            a_file = symbols[a]["file"]
            b_file = symbols[b]["file"]
            a_connections = connections.get(a_file, {"outgoing": set(), "incoming": set()})
            if b_file not in a_connections["outgoing"] and b_file not in a_connections["incoming"]:
                gaps.append({"tag": tag, "from": a_file, "to": b_file})
    return gaps
