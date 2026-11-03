from alembic import context
from rallysense.db import Base, engine
from rallysense import models  # noqa: F401

with engine.connect() as connection:
    context.configure(connection=connection, target_metadata=Base.metadata, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()
