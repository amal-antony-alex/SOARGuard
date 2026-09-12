from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from app.database.database import Base


class Alert(Base):

    __tablename__ = "alerts"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    source = Column(
        String(100),
        nullable=False
    )

    event_type = Column(
        String(100),
        nullable=False
    )

    severity = Column(
        String(20),
        nullable=False
    )

    source_ip = Column(
        String(45),
        nullable=True
    )

    destination_ip = Column(
        String(45),
        nullable=True
    )

    raw_log = Column(
        Text,
        nullable=False
    )

    # Security event timestamp
    timestamp = Column(
        DateTime,
        nullable=False
    )

    # SOARGuard ingestion / creation timestamp
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    risk_score = Column(
        Integer,
        nullable=False
    )

    priority = Column(
        String(10),
        nullable=False
    )

    status = Column(
        String(30),
        default="new",
        nullable=False
    )

    incident_id = Column(
        Integer,
        ForeignKey("incidents.id"),
        nullable=True
    )