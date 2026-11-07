"""Fail-closed read-only demonstration selection and local upload burst bounds."""

import threading
import time
from collections import defaultdict, deque
from . import config

DEMO_KEYS = {"synthetic-v1", "paired-research-v1"}
_uploads = defaultdict(deque)
_lock = threading.Lock()


def visible(session):
    return config.APP_MODE != "demo_readonly" or (
        session.id in config.DEMO_SESSION_IDS
        and session.demo_key in DEMO_KEYS
        and session.dataset_kind == "synthetic"
    )


def upload_allowed(client, timestamp=None):
    stamp = time.monotonic() if timestamp is None else timestamp
    with _lock:
        queue = _uploads[client]
        while queue and queue[0] <= stamp - 60:
            queue.popleft()
        if len(queue) >= config.MAX_UPLOADS_PER_MINUTE:
            return False
        queue.append(stamp)
        return True
