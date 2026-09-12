from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.alert import Alert
from app.models.incident import Incident


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db)
):
    total_alerts = db.query(Alert).count()

    total_incidents = db.query(Incident).count()

    open_incidents = (
        db.query(Incident)
        .filter(
            Incident.status.in_([
                "open",
                "investigating",
                "contained"
            ])
        )
        .count()
    )

    resolved_incidents = (
        db.query(Incident)
        .filter(
            Incident.status == "resolved"
        )
        .count()
    )

    closed_incidents = (
        db.query(Incident)
        .filter(
            Incident.status == "closed"
        )
        .count()
    )

    critical_alerts = (
        db.query(Alert)
        .filter(Alert.priority == "P1")
        .count()
    )

    high_risk_alerts = (
        db.query(Alert)
        .filter(Alert.risk_score >= 70)
        .count()
    )

    awaiting_approval = (
        db.query(Alert)
        .filter(Alert.status == "awaiting_approval")
        .count()
    )

    return {
        "alerts": {
            "total": total_alerts,
            "critical": critical_alerts,
            "high_risk": high_risk_alerts,
            "awaiting_approval": awaiting_approval
        },
        "incidents": {
            "total": total_incidents,
            "active": open_incidents,
            "resolved": resolved_incidents,
            "closed": closed_incidents
        }
    }

@router.get("/recent-alerts")
def get_recent_alerts(
    db: Session = Depends(get_db)
):
    alerts = (
        db.query(Alert)
        .order_by(Alert.timestamp.desc())
        .limit(10)
        .all()
    )

    return [
        {
            "id": alert.id,
            "source": alert.source,
            "event_type": alert.event_type,
            "severity": alert.severity,
            "priority": alert.priority,
            "risk_score": alert.risk_score,
            "status": alert.status,
            "source_ip": alert.source_ip,
            "destination_ip": alert.destination_ip,
            "incident_id": alert.incident_id,
            "timestamp": alert.timestamp
        }
        for alert in alerts
    ]
@router.get("/active-incidents")
def get_active_incidents(
    db: Session = Depends(get_db)
):
    incidents = (
        db.query(Incident)
        .filter(
            Incident.status.in_([
                "open",
                "investigating",
                "contained"
            ])
        )
        .order_by(Incident.updated_at.desc())
        .all()
    )

    return [
        {
            "id": incident.id,
            "title": incident.title,
            "severity": incident.severity,
            "priority": incident.priority,
            "status": incident.status,
            "risk_score": incident.risk_score,
            "description": incident.description,
            "created_at": incident.created_at,
            "updated_at": incident.updated_at
        }
        for incident in incidents
    ]