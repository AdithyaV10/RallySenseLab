"""Exercise actual Alembic revisions in an isolated PostgreSQL schema."""

from pathlib import Path
from uuid import uuid4
from alembic import command
from alembic.config import Config
from sqlalchemy import text, inspect
from rallysense.db import engine


def test_upgrade_from_mvp_preserves_rows_and_matches_models():
    schema = "migration_test_" + uuid4().hex
    sid = str(uuid4())
    root = Path(__file__).resolve().parents[1]
    config = Config(str(root / "alembic.ini"))
    config.set_main_option("script_location", str(root / "migrations"))
    with engine.begin() as connection:
        connection.execute(text(f'CREATE SCHEMA "{schema}"'))
    try:
        with engine.connect() as connection:
            connection.execute(text(f'SET search_path TO "{schema}"'))
            connection.commit()
            config.attributes["connection"] = connection
            command.upgrade(config, "0001_mvp")
            connection.execute(
                text(
                    "INSERT INTO sessions (id,created_at,title,dataset_kind,handedness,notes) VALUES (:id,now(),'Preserved MVP session','synthetic','right','migration fixture')"
                ),
                {"id": sid},
            )
            connection.commit()
            command.upgrade(config, "head")
            assert (
                connection.execute(text("SELECT title FROM sessions WHERE id=:id"), {"id": sid}).scalar_one()
                == "Preserved MVP session"
            )
            assert {"experiments", "reference_snapshots"} <= set(inspect(connection).get_table_names())
            connection.commit()
            command.check(config)
            command.downgrade(config, "0001_mvp")
            assert (
                connection.execute(
                    text("SELECT count(*) FROM sessions WHERE id=:id"), {"id": sid}
                ).scalar_one()
                == 1
            )
            connection.commit()
            command.upgrade(config, "head")
    finally:
        with engine.begin() as connection:
            connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
