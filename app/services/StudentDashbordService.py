from fastapi import HTTPException, status
from app.DB.repositories.facultyrepo import FacultyRepository
from app.DB.repositories.projectsrepo import ProjectsRepo
from app.DB.repositories.projectgithubrepo import ProjectRepositoryRepo
from app.DB.repositories.studentrepo import StudentRepository
from app.DB.repositories.teammemberepo import TeamMembersRepo
class StudentDashboardService:
    def __init__(self,sturepo:StudentRepository,tmrepo:TeamMembersRepo,projrepo:ProjectsRepo,frepo:FacultyRepository,github_repo:ProjectRepositoryRepo):
        self.sturepo = sturepo
        self.tmrepo = tmrepo
        self.projrepo = projrepo
        self.frepo = frepo
        self.github_repo = github_repo
    async def get_dashboard(self,student_id:int):
        student = await self.sturepo.get_details(student_id)
        if student is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Student Not Found.")
        team = await self.tmrepo.get_team_by_student(student_id)
        if team is None:
            return {
                "student": {
                    "roll": student["roll"],
                    "name": student["name"],
                    "dept": student["dept"]
                },
                "team": None
            }
        team_id = team["team_id"]
        members = []
        project = await self.projrepo.get_team(team_id)
        ids = await self.tmrepo.get_students(team_id)
        for id in ids:
            print(id)
            m = await self.sturepo.get_details(id["student_id"])
            members.append(m)
        supervisor = None
        if project["supervisor_id"] is not None:
            supervisor = await self.frepo.get_faculty_by_id(project["supervisor_id"])
        github = await self.github_repo.get_by_team(team_id)
        return {
            "student": {
                "roll": student["roll"],
                "name": student["name"],
                "dept": student["dept"]
            },
            "team": {
                "team_id": team_id,
                "project_title": project["project_title"],
                "project_type": project["project_type"],
                "academic_year": project["academic_year"]
            },
            "members": [
                {
                    "roll": member["roll"],
                    "name": member["name"],
                }
                for member in members
            ],
            "supervisor": (
                {
                    "id": supervisor["eid"],
                    "name": supervisor["name"],
                    "designation": supervisor["designation"]
                }
                if supervisor
                else None
            ),
            "github": (
                {
                    "repository_url": github["repository_url"],
                    "repository_owner": github["repository_owner"],
                    "repository_name": github["repository_name"]
                }
                if github
                else None
            )
        }