from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text
)

from app.database.database import Base


class ApprovalDecision(Base):

    __tablename__ = "approval_decisions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    alert_id = Column(
        Integer,
        ForeignKey("alerts.id"),
        nullable=False
    )

    decision = Column(
        String(20),
        nullable=False
    )

    analyst = Column(
        String(100),
        nullable=False
    )

    comments = Column(
        Text,
        nullable=True
    )

    decided_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )