from uuid import UUID
from sqlalchemy import select
from . import __doc__  # noqa: F401
from .. import models as m
from ..errors import DomainError


def active_session(db, session_id):
    session = db.get(m.RecordingSession, str(session_id))
    if not session or session.deleted_at:
        raise DomainError("Session not found", "NOT_FOUND", 404)
    return session


def owned(db, model, object_id):
    value = db.get(model, str(object_id))
    if not value:
        raise DomainError("Resource not found", "NOT_FOUND", 404)
    active_session(db, value.session_id)
    return value


def query_owned(db, model, session_id):
    return list(
        db.scalars(select(model).where(model.session_id == str(session_id)).order_by(model.created_at))
    )


def safe_id(value):
    return str(UUID(str(value)))
