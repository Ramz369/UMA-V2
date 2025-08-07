import argparse
import hashlib
import re
from datetime import datetime
from pathlib import Path

def compute_hash(content: str) -> str:
    block_pattern = r"@cognimap:fingerprint\n(.*?)@end:cognimap"
    # Remove fingerprint block entirely when hashing so that updating
    # metadata doesn't influence the content hash.
    content_wo = re.sub(block_pattern, "", content, flags=re.DOTALL)
    return hashlib.blake2b(content_wo.encode('utf-8'), digest_size=8).hexdigest()


def update_file(path: Path) -> bool:
    content = path.read_text(encoding='utf-8')
    pattern = r"@cognimap:fingerprint\n(.*?)@end:cognimap"
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        return False
    block = match.group(1)
    lines = block.splitlines()
    new_lines = []
    file_hash = compute_hash(content)
    now = datetime.utcnow().isoformat()
    for line in lines:
        if line.strip().startswith('hash:'):
            new_lines.append(f'hash: {file_hash}')
        elif line.strip().startswith('last_sync:'):
            new_lines.append(f'last_sync: {now}')
        else:
            new_lines.append(line)
    new_block = "\n".join(new_lines)
    new_content = content[:match.start(1)] + new_block + content[match.end(1):]
    path.write_text(new_content, encoding='utf-8')
    return True


def iter_files(target: Path):
    if target.is_file():
        yield target
    else:
        for p in target.rglob('*.py'):
            yield p


def main():
    parser = argparse.ArgumentParser(description='Update CogniMap fingerprints')
    parser.add_argument('paths', nargs='*', default=['cognimap'], help='Files or directories to update')
    args = parser.parse_args()
    for p in args.paths:
        for file in iter_files(Path(p)):
            if update_file(file):
                print(f'Updated {file}')

if __name__ == '__main__':
    main()
