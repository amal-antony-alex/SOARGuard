from pydantic import BaseModel

from app.schemas.alert import AlertStatus


class AlertStatusUpdate(BaseModel):
    status: AlertStatus