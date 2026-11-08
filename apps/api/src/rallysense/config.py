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
APP_MODE = os.getenv("APP_MODE", "local")
DEMO_SESSION_IDS = {value.strip() for value in os.getenv("DEMO_SESSION_IDS", "").split(",") if value.strip()}
BUILD_ID = os.getenv("BUILD_ID", "local-source")[:80]
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost,api,testserver").split(",")
MAX_UPLOADS_PER_MINUTE = int(os.getenv("MAX_UPLOADS_PER_MINUTE", "60"))
MAX_REQUESTS_PER_MINUTE = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "6000"))
if APP_MODE not in {"local", "demo_readonly"}:
    raise ValueError("APP_MODE must be local or demo_readonly")
if ENVIRONMENT == "production" and (
    LOCAL_TOKEN == "rallysense-local-development"
    or len(LOCAL_TOKEN) < 32
    or LOCAL_TOKEN.startswith("CHANGE_ME")
):
    raise ValueError("Production requires an explicitly configured LOCAL_TOKEN of at least 32 characters")
