from pydantic import BaseModel,field_validator,computed_field,model_validator
from enum import Enum
from datetime import datetime
class Person(BaseModel):
    id :int
    roll : str
    name : str
    cgpa : float
    dept : str
    is_team_lead : bool = False
class Supervisor(BaseModel):
    id: int
    eid: str
    name: str
    designation: str
    teams: int = 0
    is_dr: bool
    @computed_field
    @property
    def lock(self) -> bool:
        limits = {
            "Professor": 4,
            "Associate Professor": 3,
            "Assistant Professor": 2,
        }
        limit = limits.get(self.designation)
        if limit is None:
            raise ValueError("Designation Not Found!")
        return self.teams >= limit
class Team(BaseModel):
    Team_id : str
    members : list[Person]
    guide : Supervisor | None = None
    dept : str
    section : str
    batch : int = datetime.now().year
class Bucket(BaseModel):
    students : list[Person]
class TeamBucket(BaseModel):
    teams : list[str]