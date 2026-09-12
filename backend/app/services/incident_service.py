from sqlalchemy.orm import Session

from app.models.incident import Incident


def find_or_create_incident(
    db: Session,
    normalized_alert: dict,
    triage_result: dict
):

    event_type = normalized_alert.get(
        "event_type"
    )

    destination_ip = normalized_alert.get(
        "destination_ip"
    )

    priority = triage_result.get(
        "priority"
    )

    severity = normalized_alert.get(
        "severity"
    )

    # ==============================================
    # STEP 1: SEARCH FOR A RELATED OPEN INCIDENT
    # ==============================================

    existing_incident = (
        db.query(Incident)
        .filter(
            Incident.status.in_([
                "open",
                "investigating"
            ]),
            Incident.severity == severity,
            Incident.priority == priority,
            Incident.title == (
                f"{event_type.replace('_', ' ').title()} "
                f"Incident"
            ),
            Incident.description.contains(
                destination_ip
            )
        )
        .first()
    )

    # ==============================================
    # STEP 2: RETURN EXISTING INCIDENT
    # ==============================================

    if existing_incident:

        return existing_incident

    # ==============================================
    # STEP 3: CREATE NEW INCIDENT
    # ==============================================

    incident_title = (
        f"{event_type.replace('_', ' ').title()} "
        f"Incident"
    )

    incident_description = (
        f"Automatically created incident for "
        f"{event_type}. "
        f"Affected destination: "
        f"{destination_ip or 'Unknown'}."
    )

    new_incident = Incident(
        title=incident_title,
        severity=severity,
        priority=priority,
risk_score=triage_result.get(
    "risk_score",
    0
),
        status="open",
        description=incident_description
    )

    db.add(new_incident)

    db.commit()

    db.refresh(new_incident)

    return new_incident