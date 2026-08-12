from pydantic import BaseModel,HttpUrl
from datetime import datetime
from typing import Optional
from enum import Enum
class SubmissionStatus(str, Enum):
    NOT_SUBMITTED = "NOT_SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    CHANGES_REQUIRED = "CHANGES_REQUIRED"
    APPROVED = "APPROVED"

class TeamSubmission(BaseModel):
    requirement_id: int
    title: str
    description: str
    deadline: datetime
    submission_id: Optional[int] = None
    version: Optional[int] = None
    status: SubmissionStatus
    document_name: Optional[str] = None
    document_path: Optional[str] = None
    submitted_at: Optional[datetime] = None

class GitHubRepositoryRequest(BaseModel):
    repository_url: HttpUrl