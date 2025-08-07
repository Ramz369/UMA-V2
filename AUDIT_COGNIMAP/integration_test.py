"""Simple integration smoke test for cognimap with required services."""
import socket

SERVICES = [
    ("postgres", "localhost", 5432),
    ("redis", "localhost", 6379),
    ("minio", "localhost", 9000),
]


def check_port(name, host, port):
    try:
        with socket.create_connection((host, port), timeout=1):
            print(f"{name} reachable on {host}:{port}")
            return True
    except OSError as e:
        print(f"{name} not reachable on {host}:{port}: {e}")
        return False


def main():
    results = {name: check_port(name, host, port) for name, host, port in SERVICES}
    failed = [n for n, ok in results.items() if not ok]
    if failed:
        raise SystemExit(f"Unavailable services: {failed}")

if __name__ == "__main__":
    main()
