from pydantic import BaseModel,field_validator
from datetime import datetime
from enum import Enum
class TeamRequest(BaseModel):
    dept : str
    year : int
    sections : list[str]
    team_size : int
    @field_validator("sections")
    @classmethod
    def validate1(cls, val: list[str]):
        return [s.upper() for s in val]
    @field_validator("dept")
    @classmethod
    def validate2(cls,val):
        return val.upper()
class Proj_type(Enum):
    mini = "MINI"
    major = "MAJOR"
class notiftype(Enum):
    meeting =  "MEETING"
    remark = "REMARK"
    deadline = "DEADLINE"
    announcement = "ANNOUNCEMENT"
    system = "SYSTEM"
class MeetingRequest(BaseModel):
    title : str
    description : str
    meeting_time : datetime
    venue : str
    notification_message : str
class SubmissionRequirement(BaseModel):
    proj_type : str
    title : str
    description : str
    deadline : datetime
class RemarkRequest(BaseModel):
    remarks:str
class FacultyDetails(BaseModel):
    id: int
    eid: str
    name: str
    dept: str
    designation: str
class TeamSummary(BaseModel):
    team_id: str
    project_type: Proj_type
    academic_year: str
class FacultyDashboard(BaseModel):
    faculty: FacultyDetails
    teams: list[TeamSummary]
class SupervisorDetails(BaseModel):
    id : str
    name : str
class TeamMemberDetails(BaseModel):
    roll : str
    name : str
    team_lead : bool
class TeamDetails(BaseModel):
    team : TeamSummary
    supervisor : SupervisorDetails
    members : list[TeamMemberDetails]