"""Add collection metadata, explicit alignment evidence and worker readiness."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0003_collection_readiness"
down_revision = "a496e751b8a9"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "sessions",
        sa.Column(
            "collection_profile", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")
        ),
    )
    op.add_column(
        "sessions", sa.Column("collection_revision", sa.Integer(), nullable=False, server_default="1")
    )
    op.add_column("sync_configurations", sa.Column("video_id", sa.String(36), nullable=True))
    op.add_column(
        "sync_configurations",
        sa.Column("evidence", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
    )
    op.create_foreign_key(
        "fk_sync_configurations_video_id_video_assets",
        "sync_configurations",
        "video_assets",
        ["video_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_sync_configurations_video_id_owner",
        "sync_configurations",
        "video_assets",
        ["session_id", "video_id"],
        ["session_id", "id"],
    )
    op.create_table(
        "worker_heartbeats",
        sa.Column("id", sa.String(40), primary_key=True),
        sa.Column("heartbeat_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("state", sa.String(20), nullable=False),
    )


def downgrade():
    op.drop_table("worker_heartbeats")
    op.drop_constraint("fk_sync_configurations_video_id_owner", "sync_configurations", type_="foreignkey")
    op.drop_constraint(
        "fk_sync_configurations_video_id_video_assets", "sync_configurations", type_="foreignkey"
    )
    op.drop_column("sync_configurations", "evidence")
    op.drop_column("sync_configurations", "video_id")
    op.drop_column("sessions", "collection_revision")
    op.drop_column("sessions", "collection_profile")
