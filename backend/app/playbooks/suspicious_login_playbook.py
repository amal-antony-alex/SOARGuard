from datetime import datetime


def execute_suspicious_login_playbook(alert: dict) -> dict:
    """
    Execute the automated suspicious login investigation playbook.
    """

    execution_steps = []

    # Step 1
    execution_steps.append({
        "step": 1,
        "action": "Start suspicious login investigation",
        "status": "completed"
    })

    # Step 2
    source_ip = alert.get("source_ip")

    if source_ip:
        execution_steps.append({
            "step": 2,
            "action": (
                f"Extract suspicious source IP: "
                f"{source_ip}"
            ),
            "status": "completed"
        })
    else:
        execution_steps.append({
            "step": 2,
            "action": "Extract suspicious source IP",
            "status": "failed",
            "reason": "No source IP available"
        })

    # Step 3
    execution_steps.append({
        "step": 3,
        "action": "Perform suspicious login investigation",
        "status": "simulated"
    })

    # Step 4
    if alert.get("risk_score", 0) >= 70:
        response_action = (
            "Escalate for account verification and recommend "
            "credential protection measures"
        )
    else:
        response_action = (
            "Monitor account activity and investigate login context"
        )

    execution_steps.append({
        "step": 4,
        "action": response_action,
        "status": "completed"
    })

    return {
        "playbook_name": "Suspicious Login Investigation Playbook",
        "execution_status": "completed",
        "executed_at": datetime.utcnow().isoformat(),
        "steps": execution_steps
    }