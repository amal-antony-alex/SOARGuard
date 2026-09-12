from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.models.alert import Alert

from app.models.threat_intelligence import (
    ThreatIntelligence
)

from app.models.playbook_execution import (
    PlaybookExecution
)

from app.models.approval_decision import (
    ApprovalDecision
)

from app.schemas.alert import AlertCreate

from app.services.normalization_service import (
    normalize_alert
)

from app.services.ioc_extraction_service import (
    extract_iocs
)

from app.services.multi_ioc_enrichment_service import (
    enrich_all_iocs
)

from app.services.triage_service import (
    perform_initial_triage
)

from app.services.playbook_service import (
    select_and_execute_playbook
)

from app.services.playbook_tracking_service import (
    save_playbook_execution
)

from app.services.threat_intelligence_tracking_service import (
    save_threat_intelligence
)

from app.services.incident_service import (
    find_or_create_incident
)

from app.services.incident_risk_service import (
    update_incident_risk
)

from app.services.incident_lifecycle_service import (
    update_incident_lifecycle
)


router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"]
)


# ==================================================
# CREATE AND PROCESS ALERT
# ==================================================

@router.post("/")
def create_alert(
    alert: AlertCreate,
    db: Session = Depends(get_db)
):

    # ==================================================
    # STEP 1: NORMALIZE INCOMING ALERT
    # ==================================================

    normalized_alert = normalize_alert(
        alert
    )

    # ==================================================
    # STEP 2: EXTRACT IOCs
    # ==================================================

    extracted_iocs = extract_iocs(
        normalized_alert["raw_log"]
    )

    # ==================================================
    # STEP 3: ENRICH ALL EXTRACTED IOCs
    # ==================================================

    multi_ioc_enrichment = enrich_all_iocs(
        extracted_iocs
    )

    # ==================================================
    # STEP 4: SOC TRIAGE
    # ==================================================

    triage_result = perform_initial_triage(
        normalized_alert
    )

    # ==================================================
    # STEP 5: INCIDENT CORRELATION
    # ==================================================

    incident = find_or_create_incident(
        db=db,
        normalized_alert=normalized_alert,
        triage_result=triage_result
    )

    # ==================================================
    # STEP 6: SAVE ALERT TO DATABASE
    # ==================================================

    db_alert = Alert(
        incident_id=incident.id,
        source=normalized_alert["source"],
        event_type=normalized_alert["event_type"],
        severity=normalized_alert["severity"],
        source_ip=normalized_alert.get(
            "source_ip"
        ),
        destination_ip=normalized_alert.get(
            "destination_ip"
        ),
        raw_log=normalized_alert["raw_log"],
        timestamp=normalized_alert["timestamp"],
        risk_score=triage_result["risk_score"],
        priority=triage_result["priority"],
        status="new"
    )

    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)

    # ==================================================
    # STEP 6.1: UPDATE INCIDENT RISK SCORE
    # ==================================================

    incident = update_incident_risk(
        db=db,
        incident_id=incident.id
    )

    # ==================================================
    # STEP 7: SAVE ALL ENRICHED IOC RESULTS
    # ==================================================

    saved_threat_intelligence = []

    for ioc_category in multi_ioc_enrichment.values():

        for enrichment_result in ioc_category:

            threat_record = save_threat_intelligence(
                db=db,
                alert_id=db_alert.id,
                enrichment_result=enrichment_result
            )

            saved_threat_intelligence.append(
                {
                    "id": threat_record.id,
                    "ioc_type": threat_record.ioc_type,
                    "ioc_value": threat_record.ioc_value,
                    "reputation": threat_record.reputation,
                    "confidence_score": (
                        threat_record.confidence_score
                    )
                }
            )

    # ==================================================
    # STEP 8: EXECUTE APPROPRIATE SOAR PLAYBOOK
    # ==================================================

    playbook_result = select_and_execute_playbook(
        normalized_alert
    )

    # ==================================================
    # STEP 9: SAVE PLAYBOOK EXECUTION
    # ==================================================

    execution = save_playbook_execution(
        db=db,
        alert_id=db_alert.id,
        playbook_result=playbook_result
    )

    # ==================================================
    # STEP 10: HUMAN-GATED RESPONSE LOGIC
    # ==================================================

    risk_score = triage_result.get(
        "risk_score",
        0
    )

    priority = triage_result.get(
        "priority"
    )

    # ==================================================
    # P1 OR VERY HIGH-RISK ALERTS
    # ==================================================

    if priority == "P1" or risk_score >= 90:

        db_alert.status = (
            "awaiting_approval"
        )

    # ==================================================
    # P2 ALERTS
    # ==================================================

    elif priority == "P2":

        db_alert.status = (
            "investigating"
        )

    # ==================================================
    # LOWER-RISK ALERTS
    # ==================================================

    else:

        db_alert.status = "open"

    # ==================================================
    # STEP 10.1: SAVE FINAL ALERT STATUS
    # ==================================================

    db.commit()
    db.refresh(db_alert)

    # ==================================================
    # STEP 10.2: UPDATE INCIDENT LIFECYCLE
    # ==================================================

    incident = update_incident_lifecycle(
        db=db,
        incident_id=incident.id
    )

    # ==================================================
    # STEP 10.3: REFRESH INCIDENT
    # ==================================================

    if incident:

        db.refresh(incident)

    # ==================================================
    # FINAL RESPONSE
    # ==================================================

    return {
        "message": (
            "Alert processed and playbook executed"
        ),

        "alert_id": db_alert.id,

        "incident": (
            {
                "incident_id": incident.id,
                "title": incident.title,
                "status": incident.status,
                "severity": incident.severity,
                "priority": incident.priority,
                "risk_score": incident.risk_score
            }
            if incident
            else None
        ),

        "normalized_alert": normalized_alert,

        "extracted_iocs": extracted_iocs,

        "multi_ioc_enrichment": (
            multi_ioc_enrichment
        ),

        "saved_threat_intelligence": (
            saved_threat_intelligence
        ),

        "triage": triage_result,

        "playbook": playbook_result,

        "playbook_execution_id": (
            execution.id
            if execution
            else None
        ),

        "status": db_alert.status
    }


# ==================================================
# GET ALL ALERTS
# ==================================================

@router.get("/")
def get_alerts(
    db: Session = Depends(get_db)
):

    alerts = (
        db.query(Alert)
        .order_by(Alert.id.desc())
        .all()
    )

    return alerts


# ==================================================
# GET SINGLE ALERT
# ==================================================

@router.get("/{alert_id}")
def get_alert(
    alert_id: int,
    db: Session = Depends(get_db)
):

    alert = (
        db.query(Alert)
        .filter(Alert.id == alert_id)
        .first()
    )

    if not alert:

        raise HTTPException(
            status_code=404,
            detail="Alert not found"
        )

    return alert


# ==================================================
# UPDATE ALERT STATUS
# ==================================================

@router.patch("/{alert_id}/status")
def update_alert_status(
    alert_id: int,
    status: str,
    db: Session = Depends(get_db)
):

    allowed_statuses = [
        "new",
        "open",
        "in_progress",
        "investigating",
        "awaiting_approval",
        "resolved",
        "closed"
    ]

    if status not in allowed_statuses:

        raise HTTPException(
            status_code=400,
            detail={
                "message": "Invalid status",
                "allowed_statuses": (
                    allowed_statuses
                )
            }
        )

    alert = (
        db.query(Alert)
        .filter(Alert.id == alert_id)
        .first()
    )

    if not alert:

        raise HTTPException(
            status_code=404,
            detail="Alert not found"
        )

    # ==================================================
    # SAVE PREVIOUS STATUS
    # ==================================================

    previous_status = alert.status

    # ==================================================
    # UPDATE ALERT STATUS
    # ==================================================

    alert.status = status

    db.commit()
    db.refresh(alert)

    # ==================================================
    # UPDATE INCIDENT LIFECYCLE
    # ==================================================

    incident = None

    if alert.incident_id:

        incident = update_incident_lifecycle(
            db=db,
            incident_id=alert.incident_id
        )

    # ==================================================
    # RESPONSE
    # ==================================================

    return {
        "message": (
            "Alert status updated successfully"
        ),

        "alert_id": alert.id,

        "previous_status": previous_status,

        "status": alert.status,

        "incident": (
            {
                "incident_id": incident.id,
                "status": incident.status,
                "risk_score": incident.risk_score
            }
            if incident
            else None
        )
    }


# ==================================================
# GET ALERT THREAT INTELLIGENCE
# ==================================================

@router.get("/{alert_id}/intelligence")
def get_alert_intelligence(
    alert_id: int,
    db: Session = Depends(get_db)
):

    alert = (
        db.query(Alert)
        .filter(Alert.id == alert_id)
        .first()
    )

    if not alert:

        raise HTTPException(
            status_code=404,
            detail="Alert not found"
        )

    intelligence_records = (
        db.query(ThreatIntelligence)
        .filter(
            ThreatIntelligence.alert_id
            == alert_id
        )
        .all()
    )

    return {
        "alert_id": alert_id,
        "threat_intelligence": (
            intelligence_records
        )
    }


# ==================================================
# GET ALERT PLAYBOOK EXECUTIONS
# ==================================================

@router.get("/{alert_id}/executions")
def get_alert_executions(
    alert_id: int,
    db: Session = Depends(get_db)
):

    alert = (
        db.query(Alert)
        .filter(Alert.id == alert_id)
        .first()
    )

    if not alert:

        raise HTTPException(
            status_code=404,
            detail="Alert not found"
        )

    executions = (
        db.query(PlaybookExecution)
        .filter(
            PlaybookExecution.alert_id
            == alert_id
        )
        .order_by(
            PlaybookExecution.id.desc()
        )
        .all()
    )

    return {
        "alert_id": alert_id,
        "playbook_executions": executions
    }


# ==================================================
# HUMAN APPROVAL WORKFLOW
# ==================================================

@router.post("/{alert_id}/approve")
def approve_alert(
    alert_id: int,
    analyst: str = "SOC Analyst",
    comments: str = None,
    db: Session = Depends(get_db)
):

    alert = (
        db.query(Alert)
        .filter(Alert.id == alert_id)
        .first()
    )

    if not alert:

        raise HTTPException(
            status_code=404,
            detail="Alert not found"
        )

    # ==================================================
    # VALIDATE APPROVAL STATE
    # ==================================================

    if alert.status != "awaiting_approval":

        raise HTTPException(
            status_code=400,
            detail=(
                "Only alerts awaiting approval "
                "can be approved"
            )
        )

    previous_status = alert.status

    # ==================================================
    # SAVE HUMAN APPROVAL DECISION
    # ==================================================

    approval_decision = ApprovalDecision(
        alert_id=alert.id,
        decision="approved",
        analyst=analyst,
        comments=comments
    )

    db.add(approval_decision)

    # ==================================================
    # UPDATE ALERT STATUS
    # ==================================================

    alert.status = "resolved"

    db.commit()

    db.refresh(alert)
    db.refresh(approval_decision)

    # ==================================================
    # UPDATE INCIDENT LIFECYCLE
    # ==================================================

    incident = None

    if alert.incident_id:

        incident = update_incident_lifecycle(
            db=db,
            incident_id=alert.incident_id
        )

    # ==================================================
    # RESPONSE
    # ==================================================

    return {
        "message": (
            "Alert response approved by human analyst"
        ),

        "alert_id": alert.id,

        "previous_status": previous_status,

        "status": alert.status,

        "decision": "approved",

        "approval_decision_id": (
            approval_decision.id
        ),

        "analyst": approval_decision.analyst,

        "comments": approval_decision.comments,

        "decided_at": approval_decision.decided_at,

        "incident": (
            {
                "incident_id": incident.id,
                "status": incident.status,
                "risk_score": incident.risk_score
            }
            if incident
            else None
        )
    }


# ==================================================
# HUMAN REJECTION WORKFLOW
# ==================================================

@router.post("/{alert_id}/reject")
def reject_alert(
    alert_id: int,
    analyst: str = "SOC Analyst",
    comments: str = None,
    db: Session = Depends(get_db)
):

    alert = (
        db.query(Alert)
        .filter(Alert.id == alert_id)
        .first()
    )

    if not alert:

        raise HTTPException(
            status_code=404,
            detail="Alert not found"
        )

    # ==================================================
    # VALIDATE REJECTION STATE
    # ==================================================

    if alert.status != "awaiting_approval":

        raise HTTPException(
            status_code=400,
            detail=(
                "Only alerts awaiting approval "
                "can be rejected"
            )
        )

    previous_status = alert.status

    # ==================================================
    # SAVE HUMAN REJECTION DECISION
    # ==================================================

    rejection_decision = ApprovalDecision(
        alert_id=alert.id,
        decision="rejected",
        analyst=analyst,
        comments=comments
    )

    db.add(rejection_decision)

    # ==================================================
    # UPDATE ALERT STATUS
    # ==================================================

    alert.status = "investigating"

    db.commit()

    db.refresh(alert)
    db.refresh(rejection_decision)

    # ==================================================
    # UPDATE INCIDENT LIFECYCLE
    # ==================================================

    incident = None

    if alert.incident_id:

        incident = update_incident_lifecycle(
            db=db,
            incident_id=alert.incident_id
        )

    # ==================================================
    # RESPONSE
    # ==================================================

    return {
        "message": (
            "Alert response rejected by human analyst"
        ),

        "alert_id": alert.id,

        "previous_status": previous_status,

        "status": alert.status,

        "decision": "rejected",

        "approval_decision_id": (
            rejection_decision.id
        ),

        "analyst": rejection_decision.analyst,

        "comments": rejection_decision.comments,

        "decided_at": rejection_decision.decided_at,

        "incident": (
            {
                "incident_id": incident.id,
                "status": incident.status,
                "risk_score": incident.risk_score
            }
            if incident
            else None
        )
    }


# ==================================================
# GET ALERT APPROVAL DECISIONS
# ==================================================

@router.get("/{alert_id}/approval-decisions")
def get_approval_decisions(
    alert_id: int,
    db: Session = Depends(get_db)
):

    alert = (
        db.query(Alert)
        .filter(Alert.id == alert_id)
        .first()
    )

    if not alert:

        raise HTTPException(
            status_code=404,
            detail="Alert not found"
        )

    decisions = (
        db.query(ApprovalDecision)
        .filter(
            ApprovalDecision.alert_id
            == alert_id
        )
        .order_by(
            ApprovalDecision.id.desc()
        )
        .all()
    )

    return {
        "alert_id": alert_id,
        "approval_decisions": decisions
    }