from sqlalchemy import create_engine
from sqlalchemy.orm import Session, DeclarativeBase
from .config import DATABASE_URL

engine = create_engine(DATABASE_URL, pool_pre_ping=True, hide_parameters=True)


class Base(DeclarativeBase):
    pass


def get_db():
    with Session(engine) as db:
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
