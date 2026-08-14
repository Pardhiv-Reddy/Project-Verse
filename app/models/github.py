from pydantic import BaseModel,Field,HttpUrl
from datetime import datetime

class Analytics(BaseModel):
    period_start:datetime
    period_end:datetime
    total_commits: int=0
    total_contributors: int=0
    total_additions:int=0
    total_deletions:int=0
    open_issues: int=0
    closed_issues: int=0
    open_prs: int=0
    merged_prs: int=0
    last_activity: datetime | None=None
    contribution_breakdown: dict[str, int]=Field(default_factory=dict)
    contribution_percentages: dict[str, float] = Field(default_factory=dict)
    commit_messages: list[str] = Field(default_factory=list)
    active_contributors: int = 0
    top_contributors: list[tuple[str, int]] = Field(default_factory=list)
    period_days: int = 0
    changed_files: list[str] = Field(default_factory=list)


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
