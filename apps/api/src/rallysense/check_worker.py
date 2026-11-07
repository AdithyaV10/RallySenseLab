"""Compose health probe: actual worker heartbeat, no secret output."""

from sqlalchemy.orm import Session
from .db import engine
from .models import WorkerHeartbeat, now

if __name__ == "__main__":
    with Session(engine) as db:
        pulse = db.get(WorkerHeartbeat, "main")
        if not pulse or (now() - pulse.heartbeat_at).total_seconds() > 45:
            raise SystemExit(1)
