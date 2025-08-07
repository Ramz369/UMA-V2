import tempfile
from pathlib import Path
from AUDIT_COGNIMAP.fingerprint_updater import update_file

SAMPLE = """
# sample file
@cognimap:fingerprint
id: 123
birth: 2024-01-01T00:00:00
parent: None
intent: sample
semantic_tags: [demo]
version: 0.1.0
last_sync: 2024-01-01T00:00:00
hash: deadbeef
language: python
type: component
@end:cognimap
"""

def read_fp(path: Path):
    text = path.read_text()
    import re
    block = re.search(r"@cognimap:fingerprint\n(.*?)@end:cognimap", text, re.DOTALL).group(1)
    data = {}
    for line in block.strip().split('\n'):
        if ':' in line:
            k,v = line.split(':',1)
            data[k.strip()] = v.strip()
    return data

def test_updater_updates_and_idempotent():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp)/"mod.py"
        p.write_text(SAMPLE)
        assert update_file(p)
        first = read_fp(p)
        assert first['hash'] != 'deadbeef'
        assert first['last_sync'] != '2024-01-01T00:00:00'
        # run again should not change hash
        h1 = first['hash']
        assert update_file(p)
        second = read_fp(p)
        assert second['hash'] == h1
