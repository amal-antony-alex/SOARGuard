from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.models.incident import Incident
from app.models.alert import Alert
from app.models.approval_decision import ApprovalDecision
from app.models.incident_action import IncidentAction
from app.models.playbook_execution import PlaybookExecution


router = APIRouter(
    prefix="/incidents",
    tags=["Incidents"]
)


# ==================================================
# GET ALL INCIDENTS
# ==================================================

@router.get("/")
def get_incidents(
    db: Session = Depends(get_db)
):
    incidents = (
        db.query(Incident)
        .order_by(Incident.id.desc())
        .all()
    )

    return incidents


# ==================================================
# GET SINGLE INCIDENT
# ==================================================

@router.get("/{incident_id}")
def get_incident(
    incident_id: int,
    db: Session = Depends(get_db)
):
    incident = (
        db.query(Incident)
        .filter(Incident.id == incident_id)
        .first()
    )

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    return incident


# ==================================================
# GET ALERTS BELONGING TO INCIDENT
# ==================================================

@router.get("/{incident_id}/alerts")
def get_incident_alerts(
    incident_id: int,
    db: Session = Depends(get_db)
):
    incident = (
        db.query(Incident)
        .filter(Incident.id == incident_id)
        .first()
    )

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    alerts = (
        db.query(Alert)
        .filter(Alert.incident_id == incident_id)
        .order_by(Alert.id.desc())
        .all()
    )

    return {
        "incident_id": incident.id,
        "incident_title": incident.title,
        "alert_count": len(alerts),
        "alerts": alerts
    }


# ==================================================
# UPDATE INCIDENT STATUS
# ==================================================

@router.patch("/{incident_id}/status")
def update_incident_status(
    incident_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    incident = (
        db.query(Incident)
        .filter(Incident.id == incident_id)
        .first()
    )

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    allowed_statuses = [
        "open",
        "investigating",
        "contained",
        "resolved",
        "closed"
    ]

    if status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Invalid incident status",
                "allowed_statuses": allowed_statuses
            }
        )

    current_status = incident.status

    valid_transitions = {
        "open": ["investigating"],
        "investigating": ["contained"],
        "contained": ["resolved"],
        "resolved": ["closed"],
        "closed": []
    }

    if status not in valid_transitions[current_status]:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Invalid incident status transition",
                "current_status": current_status,
                "requested_status": status,
                "allowed_next_statuses":
                    valid_transitions[current_status]
            }
        )

    incident.status = status

    db.commit()
    db.refresh(incident)

    return {
        "message": "Incident status updated successfully",
        "incident_id": incident.id,
        "previous_status": current_status,
        "status": incident.status,
        "risk_score": incident.risk_score
    }


# ==================================================
# CONTAIN INCIDENT
# ==================================================

@router.post("/{incident_id}/contain")
def contain_incident(
    incident_id: int,
    analyst: str = "SOC Analyst",
    comments: str | None = None,
    db: Session = Depends(get_db)
):
    incident = (
        db.query(Incident)
        .filter(Incident.id == incident_id)
        .first()
    )

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    if incident.status not in [
        "open",
        "investigating"
    ]:
        raise HTTPException(
            status_code=400,
            detail=(
                "Only open or investigating incidents "
                "can be contained"
            )
        )

    previous_status = incident.status

    incident.status = "contained"

    action = IncidentAction(
        incident_id=incident.id,
        action="contain",
        analyst=analyst,
        comments=comments,
        previous_status=previous_status,
        new_status="contained"
    )

    db.add(action)

    db.commit()
    db.refresh(incident)

    return {
        "message": "Incident marked as contained",
        "incident_id": incident.id,
        "previous_status": previous_status,
        "status": incident.status,
        "risk_score": incident.risk_score,
        "analyst": analyst,
        "comments": comments
    }


# ==================================================
# RESOLVE INCIDENT
# ==================================================

@router.post("/{incident_id}/resolve")
def resolve_incident(
    incident_id: int,
    analyst: str = "SOC Analyst",
    comments: str | None = None,
    db: Session = Depends(get_db)
):
    incident = (
        db.query(Incident)
        .filter(Incident.id == incident_id)
        .first()
    )

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    # --------------------------------------------------
    # GET INCIDENT ALERTS
    # --------------------------------------------------

    alerts = (
        db.query(Alert)
        .filter(Alert.incident_id == incident_id)
        .all()
    )

    if not alerts:
        raise HTTPException(
            status_code=400,
            detail="Incident has no associated alerts"
        )

    # --------------------------------------------------
    # CHECK FOR ACTIVE ALERTS
    # --------------------------------------------------

    active_alerts = [
        alert
        for alert in alerts
        if alert.status not in [
            "resolved",
            "closed"
        ]
    ]

    if active_alerts:
        raise HTTPException(
            status_code=400,
            detail={
                "message": (
                    "Incident cannot be resolved "
                    "while active alerts remain"
                ),
                "active_alert_count": len(active_alerts),
                "active_alert_ids": [
                    alert.id
                    for alert in active_alerts
                ]
            }
        )

    # --------------------------------------------------
    # RESOLVE INCIDENT
    # --------------------------------------------------

    previous_status = incident.status

    incident.status = "resolved"

    action = IncidentAction(
        incident_id=incident.id,
        action="resolve",
        analyst=analyst,
        comments=comments,
        previous_status=previous_status,
        new_status="resolved"
    )

    db.add(action)

    db.commit()
    db.refresh(incident)

    return {
        "message": "Incident resolved successfully",
        "incident_id": incident.id,
        "previous_status": previous_status,
        "status": incident.status,
        "risk_score": incident.risk_score,
        "analyst": analyst,
        "comments": comments
    }


# ==================================================
# CLOSE INCIDENT
# ==================================================

@router.post("/{incident_id}/close")
def close_incident(
    incident_id: int,
    analyst: str = "SOC Analyst",
    comments: str | None = None,
    db: Session = Depends(get_db)
):
    incident = (
        db.query(Incident)
        .filter(Incident.id == incident_id)
        .first()
    )

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    # --------------------------------------------------
    # ONLY RESOLVED INCIDENTS CAN BE CLOSED
    # --------------------------------------------------

    if incident.status != "resolved":
        raise HTTPException(
            status_code=400,
            detail="Only resolved incidents can be closed"
        )

    previous_status = incident.status

    incident.status = "closed"

    action = IncidentAction(
        incident_id=incident.id,
        action="close",
        analyst=analyst,
        comments=comments,
        previous_status=previous_status,
        new_status="closed"
    )

    db.add(action)

    db.commit()
    db.refresh(incident)

    return {
        "message": "Incident closed successfully",
        "incident_id": incident.id,
        "previous_status": previous_status,
        "status": incident.status,
        "risk_score": incident.risk_score,
        "analyst": analyst,
        "comments": comments
    }


# ==================================================
# GET INCIDENT ACTIONS
# ==================================================

@router.get("/{incident_id}/actions")
def get_incident_actions(
    incident_id: int,
    db: Session = Depends(get_db)
):
    incident = (
        db.query(Incident)
        .filter(Incident.id == incident_id)
        .first()
    )

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    actions = (
        db.query(IncidentAction)
        .filter(
            IncidentAction.incident_id == incident_id
        )
        .order_by(
            IncidentAction.created_at.desc()
        )
        .all()
    )

    return [
        {
            "id": action.id,
            "incident_id": action.incident_id,
            "action": action.action,
            "analyst": action.analyst,
            "comments": action.comments,
            "previous_status": action.previous_status,
            "new_status": action.new_status,
            "created_at": action.created_at
        }
        for action in actions
    ]


# ==================================================
# GET INCIDENT TIMELINE
# ==================================================

@router.get("/{incident_id}/timeline")
def get_incident_timeline(
    incident_id: int,
    db: Session = Depends(get_db)
):
    incident = (
        db.query(Incident)
        .filter(Incident.id == incident_id)
        .first()
    )

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    timeline = []

    # --------------------------------------------------
    # INCIDENT CREATED
    # --------------------------------------------------

    timeline.append({
        "type": "incident",
        "event": "incident_created",
        "timestamp": incident.created_at,
        "description": (
            f"Incident created: {incident.title}"
        )
    })

    # --------------------------------------------------
    # GET INCIDENT ALERTS
    # --------------------------------------------------

    alerts = (
        db.query(Alert)
        .filter(
            Alert.incident_id == incident_id
        )
        .all()
    )

    alert_ids = [
        alert.id
        for alert in alerts
    ]

    # --------------------------------------------------
    # ALERT CREATED
    # --------------------------------------------------

    for alert in alerts:
        timeline.append({
            "type": "alert",
            "event": "alert_created",
            "timestamp": alert.created_at,
            "alert_id": alert.id,
            "severity": alert.severity,
            "priority": alert.priority,
            "risk_score": alert.risk_score,
            "status": alert.status,
            "description": (
                f"Alert #{alert.id} ingested from "
                f"{alert.source}"
            )
        })

    # --------------------------------------------------
    # PLAYBOOK EXECUTIONS
    # --------------------------------------------------

    if alert_ids:

        executions = (
            db.query(PlaybookExecution)
            .filter(
                PlaybookExecution.alert_id.in_(alert_ids)
            )
            .all()
        )

        for execution in executions:

            timeline.append({
                "type": "playbook",
                "event": "playbook_executed",
                "timestamp": (
                    execution.completed_at
                    or execution.started_at
                ),
                "execution_id": execution.id,
                "alert_id": execution.alert_id,
                "playbook_name": execution.playbook_name,
                "status": execution.execution_status,
                "description": (
                    f"Playbook '{execution.playbook_name}' "
                    f"executed for Alert #{execution.alert_id}"
                )
            })

    # --------------------------------------------------
    # APPROVAL DECISIONS
    # --------------------------------------------------

    if alert_ids:

        decisions = (
            db.query(ApprovalDecision)
            .filter(
                ApprovalDecision.alert_id.in_(alert_ids)
            )
            .all()
        )

        for decision in decisions:

            timeline.append({
                "type": "approval",
                "event": decision.decision,
                "timestamp": decision.decided_at,
                "alert_id": decision.alert_id,
                "analyst": decision.analyst,
                "comments": decision.comments,
                "description": (
                    f"Approval decision "
                    f"'{decision.decision}' "
                    f"for Alert #{decision.alert_id}"
                )
            })

    # --------------------------------------------------
    # INCIDENT ACTIONS
    # --------------------------------------------------

    actions = (
        db.query(IncidentAction)
        .filter(
            IncidentAction.incident_id == incident_id
        )
        .all()
    )

    for action in actions:

        timeline.append({
            "type": "incident_action",
            "event": action.action,
            "timestamp": action.created_at,
            "analyst": action.analyst,
            "comments": action.comments,
            "previous_status": action.previous_status,
            "new_status": action.new_status,
            "description": (
                f"Incident action: {action.action}"
            )
        })

    # --------------------------------------------------
    # SORT ALL EVENTS CHRONOLOGICALLY
    # --------------------------------------------------

    timeline.sort(
        key=lambda event: event["timestamp"]
    )

    # --------------------------------------------------
    # RETURN TIMELINE
    # --------------------------------------------------

    return {
        "incident_id": incident.id,
        "incident_title": incident.title,
        "status": incident.status,
        "severity": incident.severity,
        "priority": incident.priority,
        "risk_score": incident.risk_score,
        "timeline": timeline
    }


# ==================================================
# GET COMPLETE INCIDENT CASE
# ==================================================

@router.get("/{incident_id}/case")
def get_incident_case(
    incident_id: int,
    db: Session = Depends(get_db)
):
    incident = (
        db.query(Incident)
        .filter(Incident.id == incident_id)
        .first()
    )

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    # ==================================================
    # ALERTS
    # ==================================================

    alerts = (
        db.query(Alert)
        .filter(
            Alert.incident_id == incident_id
        )
        .order_by(Alert.id.desc())
        .all()
    )

    alert_data = []

    for alert in alerts:

        alert_data.append({
            "id": alert.id,
            "source": alert.source,
            "event_type": alert.event_type,
            "severity": alert.severity,
            "source_ip": alert.source_ip,
            "destination_ip": alert.destination_ip,
            "timestamp": alert.timestamp,
            "risk_score": alert.risk_score,
            "priority": alert.priority,
            "status": alert.status,
            "incident_id": alert.incident_id
        })

    # ==================================================
    # APPROVAL DECISIONS
    # ==================================================

    alert_ids = [
        alert.id
        for alert in alerts
    ]

    approval_data = []

    if alert_ids:

        decisions = (
            db.query(ApprovalDecision)
            .filter(
                ApprovalDecision.alert_id.in_(alert_ids)
            )
            .order_by(
                ApprovalDecision.decided_at.desc()
            )
            .all()
        )

        for decision in decisions:

            approval_data.append({
                "id": decision.id,
                "alert_id": decision.alert_id,
                "decision": decision.decision,
                "analyst": decision.analyst,
                "comments": decision.comments,
                "decided_at": decision.decided_at
            })

    # ==================================================
    # INCIDENT ACTIONS
    # ==================================================

    actions = (
        db.query(IncidentAction)
        .filter(
            IncidentAction.incident_id == incident_id
        )
        .order_by(
            IncidentAction.created_at.desc()
        )
        .all()
    )

    action_data = []

    for action in actions:

        action_data.append({
            "id": action.id,
            "action": action.action,
            "analyst": action.analyst,
            "comments": action.comments,
            "previous_status": action.previous_status,
            "new_status": action.new_status,
            "created_at": action.created_at
        })

    # ==================================================
    # PLAYBOOK EXECUTIONS
    # ==================================================

    playbook_data = []

    if alert_ids:

        executions = (
            db.query(PlaybookExecution)
            .filter(
                PlaybookExecution.alert_id.in_(alert_ids)
            )
            .order_by(
                PlaybookExecution.started_at.desc()
            )
            .all()
        )

        for execution in executions:

            playbook_data.append({
                "id": execution.id,
                "alert_id": execution.alert_id,
                "playbook_name": execution.playbook_name,

                # Frontend-compatible status
                "status": execution.execution_status,

                # Original model field
                "execution_status":
                    execution.execution_status,

                "started_at": execution.started_at,
                "completed_at": execution.completed_at
            })

    # ==================================================
    # RETURN COMPLETE SOC CASE
    # ==================================================

    return {
        "incident": {
            "id": incident.id,
            "title": incident.title,
            "severity": incident.severity,
            "priority": incident.priority,
            "status": incident.status,
            "risk_score": incident.risk_score,
            "description": incident.description,
            "created_at": incident.created_at,
            "updated_at": incident.updated_at
        },

        "alerts": alert_data,

        "approval_decisions": approval_data,

        "incident_actions": action_data,

        "playbook_executions": playbook_data
    }