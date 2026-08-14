from fastapi import HTTPException, status
from datetime import datetime,timezone
from app.DB.repositories.projectsrepo import ProjectsRepo
from app.DB.repositories.teammemberepo import TeamMembersRepo
from app.DB.repositories.facultyrepo import FacultyRepository
from app.DB.repositories.projectgithubrepo import ProjectRepositoryRepo
from app.DB.repositories.submissionrepo import SubmissionRepo
from app.DB.repositories.studentrepo import StudentRepository
from app.DB.repositories.subreqrepo import SubmissionRequirementRepo
class ProjectWorkSpaceService:
    def __init__(self,projrepo:ProjectsRepo,tmrepo:TeamMembersRepo,frepo:FacultyRepository,srepo:SubmissionRepo,github_repo:ProjectRepositoryRepo,sturepo:StudentRepository,sreqrepo:SubmissionRequirementRepo):
        self.projrepo = projrepo
        self.tmrepo = tmrepo
        self.frepo = frepo
        self.srepo = srepo
        self.github_repo = github_repo
        self.sturepo = sturepo
        self.sreqrepo = sreqrepo
    async def get_project_page(self,team_id: str,student_id: int):
        if not await self.tmrepo.verify_team(team_id,student_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You are not a member of this team.")
        project = await self.projrepo.get_team(team_id)
        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,detail="Project Not Found.")
        members = []
        student_ids = await self.tmrepo.get_students(team_id)
        for student in student_ids:
            m = await self.sturepo.get_details(student["student_id"])
            members.append(m)
        supervisor = None
        if project["supervisor_id"] is not None:
            supervisor = await self.frepo.get_faculty_by_id(project["supervisor_id"])
        submissions = await self.srepo.get_team_submission_summary(team_id,project["dept"],project["project_type"])
        timeline = await self.sreqrepo.get_project_timeline(project["dept"],project["project_type"],project["academic_year"])
        now = datetime.now(timezone.utc)
        review_timeline = []
        for item in timeline:
            if now < item["start_date"]:
                status_value = "UPCOMING"
            elif now <= item["deadline"]:
                status_value = "IN_PROGRESS"
            else:
                status_value = "COMPLETED"
            review_timeline.append({
                "requirement_id": item["id"],
                "title": item["title"],
                "description": item["description"],
                "start_date": item["start_date"],
                "deadline": item["deadline"],
                "status": status_value})
        github = await self.github_repo.get_by_team(team_id)
        return {
            "project": {
                "team_id": project["team_id"],
                "title": project["project_title"],
                "project_type": project["project_type"],
                "academic_year": project["academic_year"],
                "status": project["status"]
            },
            "supervisor": (
                {
                    "id": supervisor["eid"],
                    "name": supervisor["name"],
                    "designation": supervisor["designation"]
                }
                if supervisor
                else None
            ),
            "team": {
                "members": [
                    {
                        "roll": member["roll"],
                        "name": member["name"],
                    }
                    for member in members
                ]
            },
            "submissions": [
                {
                "requirement_id": row["requirement_id"],
                "title": row["title"],
                "description": row["description"],
                "deadline": row["deadline"],
                "submission_id": row["submission_id"],
                "version": row["version"],
                "status": (
                    row["status"]
                    if row["submission_id"] is not None
                    else "NOT_SUBMITTED"
                    ),
                "document_name": row["document_name"],
                "submitted_at": row["submitted_at"],
                "review": (
                    {
                        "status": row["review_status"],
                        "remarks": row["review_remarks"],
                        "reviewed_at": row["reviewed_at"]
                    }
                    if row["review_status"] is not None
                    else None
                    )
                }
                for row in submissions
            ],
            "github": (
                {
                    "repository_url": github["repository_url"],
                    "repository_owner": github["repository_owner"],
                    "repository_name": github["repository_name"]
                }
                if github
                else None
            ),
            "review_timeline": review_timeline
        }