from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.database.database import Base


class PlaybookAction(Base):
    __tablename__ = "playbook_actions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    execution_id = Column(
        Integer,
        nullable=False,
        index=True
    )

    step_number = Column(
        Integer,
        nullable=False
    )

    action = Column(
        String(255),
        nullable=False
    )

    status = Column(
        String(30),
        nullable=False
    )

    details = Column(
        Text,
        nullable=True
    )

    executed_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )