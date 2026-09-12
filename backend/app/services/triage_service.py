def perform_initial_triage(alert: dict) -> dict:
    """
    Perform rule-based SOC alert triage.

    The triage engine analyzes:
    - Alert severity
    - Event type
    - Risk score
    - Recommended SOC response
    """

    severity = alert["severity"]
    event_type = alert["event_type"]

    # Base risk score based on severity
    severity_scores = {
        "low": 20,
        "medium": 40,
        "high": 70,
        "critical": 90
    }

    risk_score = severity_scores.get(severity, 0)

    # Event-type risk adjustments
    event_risk_adjustments = {
        "brute_force": 15,
        "malware_detected": 25,
        "ransomware_detected": 40,
        "data_exfiltration": 35,
        "privilege_escalation": 30,
        "suspicious_login": 10,
        "port_scan": 5
    }

    risk_score += event_risk_adjustments.get(event_type, 0)

    # Ensure score never exceeds 100
    risk_score = min(risk_score, 100)

    # Determine SOC priority based on final risk score
    if risk_score >= 90:
        priority = "P1"
        recommended_action = (
            "Immediate investigation, containment, and escalation required"
        )
        requires_immediate_attention = True

    elif risk_score >= 70:
        priority = "P2"
        recommended_action = (
            "High-priority investigation required as soon as possible"
        )
        requires_immediate_attention = True

    elif risk_score >= 40:
        priority = "P3"
        recommended_action = (
            "Investigate during normal SOC operations"
        )
        requires_immediate_attention = False

    else:
        priority = "P4"
        recommended_action = (
            "Monitor and review for suspicious activity"
        )
        requires_immediate_attention = False

    return {
        "risk_score": risk_score,
        "priority": priority,
        "recommended_action": recommended_action,
        "requires_immediate_attention": requires_immediate_attention
    }