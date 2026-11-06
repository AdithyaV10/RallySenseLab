from alembic import context
from rallysense.db import Base, engine
from rallysense import models  # noqa: F401


def migrate(connection):
    context.configure(connection=connection, target_metadata=Base.metadata, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()


provided_connection = context.config.attributes.get("connection")
if provided_connection is not None:
    migrate(provided_connection)
else:
    with engine.connect() as connection:
        migrate(connection)
