from app.playbooks.brute_force_playbook import (
    execute_brute_force_playbook
)

from app.playbooks.malware_playbook import (
    execute_malware_playbook
)

from app.playbooks.suspicious_login_playbook import (
    execute_suspicious_login_playbook
)


PLAYBOOK_REGISTRY = {
    "brute_force": execute_brute_force_playbook,
    "malware_detected": execute_malware_playbook,
    "suspicious_login": execute_suspicious_login_playbook
}


def select_and_execute_playbook(alert: dict) -> dict:
    """
    Select and execute the appropriate SOAR playbook
    using the playbook registry.
    """

    event_type = alert.get("event_type")

    playbook_function = PLAYBOOK_REGISTRY.get(
        event_type
    )

    if playbook_function:
        return playbook_function(alert)

    return {
        "playbook_name": None,
        "execution_status": "not_applicable",
        "message": (
            f"No automated playbook available for "
            f"event type: {event_type}"
        )
    }
