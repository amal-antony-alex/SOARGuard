from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.incident import Incident


def calculate_incident_risk(
    db: Session,
    incident_id: int
):

    # ==============================================
    # GET ALL ALERTS BELONGING TO THIS INCIDENT
    # ==============================================

    alerts = (
        db.query(Alert)
        .filter(
            Alert.incident_id == incident_id
        )
        .all()
    )

    # ==============================================
    # IF NO ALERTS EXIST
    # ==============================================

    if not alerts:

        return 0

    # ==============================================
    # CALCULATE HIGHEST RISK SCORE
    # ==============================================

    highest_risk_score = max(
        alert.risk_score
        for alert in alerts
    )

    # ==============================================
    # RETURN INCIDENT RISK SCORE
    # ==============================================

    return highest_risk_score


def update_incident_risk(
    db: Session,
    incident_id: int
):

    # ==============================================
    # GET INCIDENT
    # ==============================================

    incident = (
        db.query(Incident)
        .filter(
            Incident.id == incident_id
        )
        .first()
    )

    if not incident:

        return None

    # ==============================================
    # CALCULATE NEW RISK SCORE
    # ==============================================

    new_risk_score = calculate_incident_risk(
        db=db,
        incident_id=incident_id
    )

    # ==============================================
    # UPDATE INCIDENT
    # ==============================================

    incident.risk_score = new_risk_score

    db.commit()

    db.refresh(incident)

    return incident