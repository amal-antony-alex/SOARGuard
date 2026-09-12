from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String

from app.database.database import Base


class ThreatIntelligence(Base):
    __tablename__ = "threat_intelligence"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # --------------------------------------------------
    # RELATION TO ALERT
    # --------------------------------------------------

    alert_id = Column(
        Integer,
        nullable=False,
        index=True
    )

    # --------------------------------------------------
    # IOC INFORMATION
    # --------------------------------------------------

    ioc_type = Column(
        String(50),
        nullable=False,
        index=True
    )

    ioc_value = Column(
        String(1000),
        nullable=False,
        index=True
    )

    # Kept for backward compatibility with
    # the earlier IP-only implementation.
    ip_address = Column(
        String(50),
        nullable=True,
        index=True
    )

    # --------------------------------------------------
    # THREAT INTELLIGENCE RESULTS
    # --------------------------------------------------

    reputation = Column(
        String(50),
        nullable=False
    )

    confidence_score = Column(
        Float,
        nullable=False,
        default=0
    )

    malicious_detections = Column(
        Integer,
        nullable=True,
        default=0
    )

    suspicious_detections = Column(
        Integer,
        nullable=True,
        default=0
    )

    harmless_detections = Column(
        Integer,
        nullable=True,
        default=0
    )

    # --------------------------------------------------
    # THREAT INTELLIGENCE SOURCE
    # --------------------------------------------------

    source = Column(
        String(100),
        nullable=False
    )

    enriched_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )