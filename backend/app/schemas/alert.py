from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class AlertCreate(BaseModel):
    source: str = Field(..., min_length=2, max_length=100)
    event_type: str = Field(..., min_length=2, max_length=100)
    severity: AlertSeverity

    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None

    raw_log: str = Field(..., min_length=1)

    timestamp: datetime


class AlertResponse(AlertCreate):
    id: int
    status: AlertStatus

    class Config:
        from_attributes = True