from pydantic import BaseModel,Field,HttpUrl
from datetime import datetime

class Analytics(BaseModel):
    total_commits: int
    total_contributors: int
    open_issues: int
    closed_issues: int
    open_prs: int
    merged_prs: int
    last_activity: datetime | None
    contribution_breakdown: dict[str, int]
    activity_score: float
    activity_level: float

class Commit(BaseModel):
    sha :str
    author:str
    date:datetime
    message:str

    additions : int=0
    deletions : int=0
    files_changed : int=0

class Contributor(BaseModel):
    username:str
    contributions:int

class Issue(BaseModel):
    number:int
    title: str
    author: str

    state: str
    body:str|None=None

    created_at: datetime
    closed_at: datetime | None = None

class PullRequest(BaseModel):
    number:int
    title:str
    author:str
    state:str
    body:str|None=None

    created_at: datetime
    merged_at:datetime|None=None

class Repository(BaseModel):
    github_repo_id:int

    owner:str
    name:str

    url:HttpUrl

    description:str|None=None

    default_branch:str

    readme_content:str|None=None

    registered_at: datetime

class Snapshot(BaseModel):
    repository_id: int

    period_start: datetime
    period_end: datetime

    collected_at: datetime
    commits: list[Commit] = Field(default_factory=list)
    pull_requests: list[PullRequest]= Field(default_factory=list)
    issues: list[Issue]= Field(default_factory=list)
    contributors: list[Contributor]= Field(default_factory=list)
