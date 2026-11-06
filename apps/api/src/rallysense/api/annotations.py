from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..db import get_db
from .. import models as m, schemas as s
from ..errors import DomainError
from .common import active_session, owned

router = APIRouter()


@router.post("/sessions/{session_id}/annotations", response_model=s.AnnotationOut, status_code=201)
def add_annotation(
    session_id: UUID,
    payload: s.AnnotationCreate,
    set_id: UUID | None = None,
    db: Session = Depends(get_db, scope="function"),
):
    session = active_session(db, session_id)
    db.get(m.RecordingSession, session.id, with_for_update=True)
    labels = db.scalars(
        select(m.AnnotationSet).where(
            m.AnnotationSet.session_id == session.id, m.AnnotationSet.provenance == "human"
        )
    ).first()
    if set_id:
        labels = owned(db, m.AnnotationSet, set_id)
        if labels.session_id != session.id or labels.provenance != "human":
            raise DomainError("Choose a human annotation set in this session", "INVALID_REFERENCE", 409)
    if not labels:
        labels = m.AnnotationSet(session_id=session.id, name="Manual observations", provenance="human")
        db.add(labels)
        db.flush()
    labels = db.get(m.AnnotationSet, labels.id, with_for_update=True, populate_existing=True)
    labels.revision += 1
    annotation = m.EventAnnotation(session_id=session.id, set_id=labels.id, **payload.model_dump())
    if payload.event_type == "synthetic_reference":
        raise DomainError("Generated references are created only by the synthetic fixture importer")
    db.add(annotation)
    db.flush()
    return annotation


@router.patch("/annotations/{annotation_id}", response_model=s.AnnotationOut)
def edit_annotation(
    annotation_id: UUID, payload: s.AnnotationUpdate, db: Session = Depends(get_db, scope="function")
):
    event = owned(db, m.EventAnnotation, annotation_id)
    labels = db.get(m.AnnotationSet, event.set_id, with_for_update=True)
    event = db.get(m.EventAnnotation, event.id, with_for_update=True, populate_existing=True)
    if labels.provenance != "human":
        raise DomainError("Generated references are immutable", "INVALID_STATE", 409)
    if event.revision != payload.revision:
        raise DomainError("Annotation changed; reload before editing", "REVISION_CONFLICT", 409)
    if payload.event_type == "synthetic_reference":
        raise DomainError("Human references cannot become generated fixture references")
    for key, value in payload.model_dump(exclude={"revision"}).items():
        setattr(event, key, value)
    event.revision += 1
    labels.revision += 1
    return event


@router.delete("/annotations/{annotation_id}", status_code=204)
def remove_annotation(
    annotation_id: UUID, revision: int = Query(ge=1), db: Session = Depends(get_db, scope="function")
):
    event = owned(db, m.EventAnnotation, annotation_id)
    labels = db.get(m.AnnotationSet, event.set_id, with_for_update=True)
    event = db.get(m.EventAnnotation, event.id, with_for_update=True, populate_existing=True)
    if labels.provenance != "human" or event.revision != revision:
        raise DomainError("Reference immutable or changed; reload", "REVISION_CONFLICT", 409)
    db.delete(event)
    labels.revision += 1
