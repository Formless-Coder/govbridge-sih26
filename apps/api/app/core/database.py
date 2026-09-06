from __future__ import annotations

import json
import os
from datetime import datetime

from sqlalchemy import String, Text, create_engine, func
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./govbridge.db')


class Base(DeclarativeBase):
    pass


class CaseRecord(Base):
    __tablename__ = 'case_records'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    case_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    service_id: Mapped[str] = mapped_column(String(128), nullable=False, default='scholarship')
    applicant_name: Mapped[str] = mapped_column(String(255), nullable=False, default='Unknown')
    status: Mapped[str] = mapped_column(String(64), nullable=False, default='DRAFT')
    decision: Mapped[str] = mapped_column(Text, default='{}')
    review: Mapped[str] = mapped_column(Text, default='{}')
    timeline: Mapped[str] = mapped_column(Text, default='[]')
    department_checks: Mapped[str] = mapped_column(Text, default='[]')
    result: Mapped[str] = mapped_column(Text, default='{}')
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())


engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def is_database_ready() -> bool:
    try:
        with Session(engine) as session:
            session.execute(func.now())
        return True
    except Exception:
        return False


def _json_default(value: object, fallback: object) -> str:
    if value is None:
        value = fallback
    return json.dumps(value, default=str)


def _json_load(raw: str | None, fallback: object) -> object:
    if raw in (None, ''):
        return fallback
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return fallback


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


init_db()


def case_to_dict(case: CaseRecord) -> dict[str, object]:
    return {
        'case_id': case.case_id,
        'service_id': case.service_id,
        'applicant_name': case.applicant_name,
        'status': case.status,
        'decision': _json_load(case.decision, {}),
        'review': _json_load(case.review, {}),
        'timeline': _json_load(case.timeline, []),
        'department_checks': _json_load(case.department_checks, []),
        'result': _json_load(case.result, {}),
    }


def save_case_record(case: dict[str, object]) -> dict[str, object]:
    case_id = str(case.get('case_id'))
    with Session(engine) as session:
        record = session.query(CaseRecord).filter_by(case_id=case_id).first()
        if record is None:
            record = CaseRecord(case_id=case_id)
            session.add(record)

        record.service_id = str(case.get('service_id', record.service_id or 'scholarship'))
        record.applicant_name = str(case.get('applicant_name', record.applicant_name or 'Unknown'))
        record.status = str(case.get('status', record.status or 'DRAFT'))
        record.decision = _json_default(case.get('decision'), {})
        record.review = _json_default(case.get('review'), {})
        record.timeline = _json_default(case.get('timeline'), [])
        record.department_checks = _json_default(case.get('department_checks'), [])
        record.result = _json_default(case.get('result'), {})
        session.commit()
        session.refresh(record)

    return case_to_dict(record)


def load_case_record(case_id: str) -> dict[str, object] | None:
    with Session(engine) as session:
        record = session.query(CaseRecord).filter_by(case_id=case_id).first()
        if record is None:
            return None
        return case_to_dict(record)


def list_case_records() -> list[dict[str, object]]:
    try:
        with Session(engine) as session:
            records = session.query(CaseRecord).all()
            return [case_to_dict(record) for record in records]
    except OperationalError:
        init_db()
        with Session(engine) as session:
            records = session.query(CaseRecord).all()
            return [case_to_dict(record) for record in records]
