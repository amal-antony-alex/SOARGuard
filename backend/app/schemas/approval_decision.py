from pydantic import BaseModel


class ApprovalDecisionCreate(BaseModel):

    analyst: str

    comments: str | None = None