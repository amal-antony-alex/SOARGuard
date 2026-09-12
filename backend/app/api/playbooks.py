from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.playbook_execution import PlaybookExecution
from app.models.playbook_action import PlaybookAction


router = APIRouter(
    prefix="/playbooks",
    tags=["Playbooks"]
)


# --------------------------------------------------
# GET ALL PLAYBOOK EXECUTIONS FOR AN ALERT
# --------------------------------------------------

@router.get("/alerts/{alert_id}/executions")
def get_alert_executions(
    alert_id: int,
    db: Session = Depends(get_db)
):
    executions = (
        db.query(PlaybookExecution)
        .filter(
            PlaybookExecution.alert_id == alert_id
        )
        .order_by(
            PlaybookExecution.id.desc()
        )
        .all()
    )

    return executions


# --------------------------------------------------
# GET SINGLE PLAYBOOK EXECUTION
# --------------------------------------------------

@router.get("/executions/{execution_id}")
def get_playbook_execution(
    execution_id: int,
    db: Session = Depends(get_db)
):
    execution = (
        db.query(PlaybookExecution)
        .filter(
            PlaybookExecution.id == execution_id
        )
        .first()
    )

    if not execution:
        raise HTTPException(
            status_code=404,
            detail="Playbook execution not found"
        )

    return execution


# --------------------------------------------------
# GET ALL ACTIONS FOR AN EXECUTION
# --------------------------------------------------

@router.get("/executions/{execution_id}/actions")
def get_execution_actions(
    execution_id: int,
    db: Session = Depends(get_db)
):
    execution = (
        db.query(PlaybookExecution)
        .filter(
            PlaybookExecution.id == execution_id
        )
        .first()
    )

    if not execution:
        raise HTTPException(
            status_code=404,
            detail="Playbook execution not found"
        )

    actions = (
        db.query(PlaybookAction)
        .filter(
            PlaybookAction.execution_id == execution_id
        )
        .order_by(
            PlaybookAction.step_number.asc()
        )
        .all()
    )

    return actions