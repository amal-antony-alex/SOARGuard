from datetime import datetime

from app.services.threat_intelligence_service import (
    enrich_ip_reputation
)


def execute_brute_force_playbook(alert: dict) -> dict:

    execution_steps = []

    # Step 1: Start investigation
    execution_steps.append({
        "step": 1,
        "action": "Start automated brute-force investigation",
        "status": "completed"
    })

    # Step 2: Extract source IP
    source_ip = alert.get("source_ip")

    if not source_ip:
        execution_steps.append({
            "step": 2,
            "action": "Extract source IP",
            "status": "failed",
            "reason": "No source IP available"
        })

        return {
            "playbook_name": "Brute Force Response Playbook",
            "execution_status": "failed",
            "executed_at": datetime.utcnow().isoformat(),
            "steps": execution_steps
        }

    execution_steps.append({
        "step": 2,
        "action": f"Extract source IP: {source_ip}",
        "status": "completed"
    })

    # Step 3: Threat intelligence enrichment
    enrichment_result = enrich_ip_reputation(
        source_ip
    )

    execution_steps.append({
        "step": 3,
        "action": "Perform IP reputation investigation",
        "status": "completed",
        "details": enrichment_result
    })

    # Step 4: Determine automated response
    reputation = enrichment_result["reputation"]
    risk_score = alert.get("risk_score", 0)

    if reputation == "malicious":
        response_action = (
            "Escalate incident and recommend immediate "
            "source IP containment"
        )

    elif risk_score >= 70:
        response_action = (
            "Prioritize investigation and monitor source IP"
        )

    else:
        response_action = (
            "Monitor source IP and continue investigation"
        )

    execution_steps.append({
        "step": 4,
        "action": response_action,
        "status": "completed"
    })

    return {
        "playbook_name": "Brute Force Response Playbook",
        "execution_status": "completed",
        "executed_at": datetime.utcnow().isoformat(),
        "threat_intelligence": enrichment_result,
        "steps": execution_steps
    }