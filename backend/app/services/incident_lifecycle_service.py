from sqlalchemy.orm import Session

from app.models.incident import Incident
from app.models.alert import Alert


def update_incident_lifecycle(db: Session, incident_id: int):
    incident = (
        db.query(Incident)
        .filter(Incident.id == incident_id)
        .first()
    )

    if not incident:
        return None

    alerts = (
        db.query(Alert)
        .filter(Alert.incident_id == incident_id)
        .all()
    )

    if not alerts:
        return incident

    alert_statuses = [alert.status for alert in alerts]

    # --------------------------------------------------
    # High-risk active alerts
    # --------------------------------------------------
    active_high_risk_alert = any(
        alert.status in [
            "new",
            "open",
            "in_progress",
            "investigating",
            "awaiting_approval"
        ]
        and (
            alert.priority == "P1"
            or alert.risk_score >= 90
        )
        for alert in alerts
    )

    # --------------------------------------------------
    # Keep incident under investigation while
    # high-risk alerts are still active
    # --------------------------------------------------
    if active_high_risk_alert:
        incident.status = "investigating"

    # --------------------------------------------------
    # IMPORTANT:
    # Do NOT automatically resolve the incident.
    #
    # Even if all alerts are resolved/closed,
    # the incident requires explicit analyst resolution.
    # --------------------------------------------------
    elif any(
        status in [
            "in_progress",
            "investigating",
            "awaiting_approval"
        ]
        for status in alert_statuses
    ):
        incident.status = "investigating"

    # --------------------------------------------------
    # If alerts are resolved but the incident itself
    # has not been manually resolved, keep it open.
    # --------------------------------------------------
    elif all(
        status in ["resolved", "closed"]
        for status in alert_statuses
    ):
        if incident.status not in [
            "contained",
            "resolved",
            "closed"
        ]:
            incident.status = "open"

    db.commit()
    db.refresh(incident)

    return incident