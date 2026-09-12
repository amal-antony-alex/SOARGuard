from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from app.database.database import Base


class PlaybookExecution(Base):
    __tablename__ = "playbook_executions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    alert_id = Column(
        Integer,
        nullable=False,
        index=True
    )

    playbook_name = Column(
        String(150),
        nullable=False
    )

    execution_status = Column(
        String(30),
        nullable=False
    )

    started_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    completed_at = Column(
        DateTime,
        nullable=True
    )