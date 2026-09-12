from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from app.database.database import Base


class IncidentAction(Base):
    __tablename__ = "incident_actions"

    id = Column(Integer, primary_key=True, index=True)

    incident_id = Column(
        Integer,
        ForeignKey("incidents.id"),
        nullable=False
    )

    action = Column(String(50), nullable=False)

    analyst = Column(String(100), nullable=False)

    comments = Column(Text, nullable=True)

    previous_status = Column(String(30), nullable=True)

    new_status = Column(String(30), nullable=False)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )