import os
from pathlib import Path

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg://rallysense:rallysense_local_only@127.0.0.1:5433/rallysense"
)
STORAGE_ROOT = Path(os.getenv("STORAGE_ROOT", "storage")).resolve()
LOCAL_TOKEN = os.getenv("LOCAL_TOKEN", "rallysense-local-development")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://127.0.0.1:3000,http://localhost:3000").split(",")
MAX_VIDEO_BYTES = 500 * 1024 * 1024
MAX_CSV_BYTES = 50 * 1024 * 1024
