import logging
import threading
import time
from .jobs import claim_job, execute_job, heartbeat


def run_one():
    claimed = claim_job()
    if not claimed:
        return False
    stop = threading.Event()

    def renew():
        while not stop.wait(20):
            heartbeat(*claimed)

    thread = threading.Thread(target=renew, daemon=True)
    thread.start()
    try:
        execute_job(*claimed)
    finally:
        stop.set()
        thread.join(timeout=2)
    return True


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    from .maintenance import reconcile_storage

    # Startup can race a database restart; maintenance participates in the retry loop.
    next_maintenance = 0
    while True:
        try:
            if time.monotonic() >= next_maintenance:
                reconcile_storage()
                next_maintenance = time.monotonic() + 3600
            if not run_one():
                time.sleep(0.5)
        except Exception:
            logging.exception("Worker polling failed")
            time.sleep(2)
