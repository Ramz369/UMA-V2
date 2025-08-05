"""Monitor git-based lock graph and abort dead-locks (stub)."""
import time, yaml, pathlib
CFG = yaml.safe_load(open('config/lock_graph.yaml'))

def run_once():
    # TODO: inspect .locks/* files, detect cycles, abort youngest holder
    pass

if __name__ == "__main__":
    while True:
        run_once()
        time.sleep(5)