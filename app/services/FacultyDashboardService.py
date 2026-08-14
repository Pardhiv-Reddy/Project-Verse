from app.DB.repositories.facultyrepo import FacultyRepository
from app.DB.repositories.projectsrepo import ProjectsRepo
from app.DB.repositories.teammemberepo import TeamMembersRepo
from app.DB.repositories.studentrepo import StudentRepository
from app.DB.repositories.submissionrepo import SubmissionRepo
from app.models.Faculty import FacultyDashboard,FacultyDetails,TeamSummary,TeamMemberDetails,TeamDetails,SupervisorDetails
from fastapi import HTTPException,status
class FacultyDashboardService:
    def __init__(self,frepo:FacultyRepository,projrepo:ProjectsRepo,tmrepo:TeamMembersRepo,sturepo:StudentRepository,srepo:SubmissionRepo):
        self.frepo = frepo
        self.projrepo = projrepo
        self.tmrepo = tmrepo
        self.sturepo = sturepo
        self.srepo = srepo
    async def get_dashboard(self,faculty_id:int):
        faculty = await self.frepo.get_faculty_by_id(faculty_id)
        details = FacultyDetails(
            id=faculty["id"],
            eid=faculty["eid"],
            name=faculty["name"],
            dept=faculty["dept"],
            designation=faculty["designation"]
        )
        teams = await self.projrepo.get_supervisor_teams(details.id,details.dept)
        if teams is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Teams Are Not Found.")
        final_teams = [TeamSummary(team_id=team["team_id"],project_type=team["project_type"],academic_year=team["academic_year"]) for team in teams]
        return FacultyDashboard(faculty=details,teams=final_teams)
    async def get_team_detail(self,faculty_id:int,team_id:str):
        if not await self.projrepo.verify_team(team_id,faculty_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You Are Allowed Only To View The Details Of The Team You Supervise.")
        team = await self.projrepo.get_team(team_id)
        if team is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Team not found.")
        team_details = TeamSummary(team_id=team["team_id"],project_type=team["project_type"],academic_year=team["academic_year"])
        faculty = await self.frepo.get_faculty_by_id(faculty_id)
        faculty_details = SupervisorDetails(id=faculty["eid"],name=faculty["name"])
        ids = await self.tmrepo.get_students(team_id)
        members = []
        for index,id in enumerate(ids):
            student = await self.sturepo.get_details(id["student_id"])
            members.append(TeamMemberDetails(roll=student["roll"],name=student["name"],team_lead=(index==0))) # have to change this.
        return TeamDetails(team=team_details,supervisor=faculty_details,members=members)
    async def get_team_submissions(self,faculty_id: int,team_id: str):
        if not await self.projrepo.verify_team(team_id, faculty_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You are only allowed to view submissions of teams you supervise.")
        team = await self.projrepo.get_team(team_id)
        if team is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Team not found.")
        rows = await self.srepo.get_team_submission_summary(team_id,team["dept"],team["project_type"])
        result = []
        for row in rows:
            data = dict(row)
            if data["submission_id"] is None:
                data["status"] = "NOT_SUBMITTED"
            result.append(data)
        return result
    async def get_team_page(self,faculty_id:int,team_id:str):
        if not await self.projrepo.verify_team(team_id, faculty_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You are allowed only to view the details of the team you supervise.")
        team = await self.projrepo.get_team(team_id)
        if team is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Team not found.")
        faculty = await self.frepo.get_faculty_by_id(faculty_id)
        faculty_details = SupervisorDetails(id=faculty["eid"],name=faculty["name"])
        team_details = TeamSummary(team_id=team["team_id"],project_type=team["project_type"],academic_year=team["academic_year"])
        ids = await self.tmrepo.get_students(team_id)
        members = []
        for index, item in enumerate(ids):
            student = await self.sturepo.get_details(item["student_id"])
            members.append(
                TeamMemberDetails(roll=student["roll"],name=student["name"],team_lead=(index == 0)))
        rows = await self.srepo.get_team_submission_summary(team_id,team["dept"],team["project_type"])
        submissions = []
        for row in rows:
            data = dict(row)
            if data["submission_id"] is None:
                data["status"] = "NOT_SUBMITTED"
            submissions.append(data)
        return {
            "team": team_details,
            "supervisor": faculty_details,
            "members": members,
            "submissions": submissions
        }