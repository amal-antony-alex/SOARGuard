from datetime import datetime

from sqlalchemy.orm import Session

from app.models.playbook_execution import PlaybookExecution
from app.models.playbook_action import PlaybookAction


def save_playbook_execution(
    db: Session,
    alert_id: int,
    playbook_result: dict
) -> PlaybookExecution:
    """
    Save a completed playbook execution and all
    individual actions into the database.
    """

    # Create the playbook execution record
    execution = PlaybookExecution(
        alert_id=alert_id,
        playbook_name=playbook_result["playbook_name"],
        execution_status=playbook_result["execution_status"],
        started_at=datetime.utcnow(),
        completed_at=datetime.utcnow()
    )

    db.add(execution)
    db.commit()
    db.refresh(execution)

    # Save each individual playbook step
    for step in playbook_result.get("steps", []):

        action_record = PlaybookAction(
            execution_id=execution.id,
            step_number=step["step"],
            action=step["action"],
            status=step["status"],
            details=step.get("reason")
        )

        db.add(action_record)

    # Commit all actions
    db.commit()

    return execution
