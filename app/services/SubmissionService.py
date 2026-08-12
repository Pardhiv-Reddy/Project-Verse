from app.DB.repositories.projectsrepo import ProjectsRepo
from app.DB.repositories.submissionrepo import SubmissionRepo
from app.DB.repositories.subreqrepo import SubmissionRequirementRepo
from app.DB.repositories.teammemberepo import TeamMembersRepo
from app.DB.repositories.subrevrepo import SubmissionReviewRepo
from datetime import datetime,timezone
from app.services.FileService import FileService
from fastapi import HTTPException,status,UploadFile
from pathlib import Path
class SubmissionService:
    def __init__(self,srepo :SubmissionRepo,srrepo:SubmissionRequirementRepo,tmrepo:TeamMembersRepo,projrepo : ProjectsRepo,fservice : FileService,srevrepo : SubmissionReviewRepo):
        self.srrepo = srrepo
        self.srepo = srepo
        self.tmrepo = tmrepo
        self.projrepo = projrepo
        self.fservice = fservice
        self.srevrepo = srevrepo
    async def add_submission_requirement(self,dept:str,proj_type:str,title:str,description:str,deadline:datetime,year:str):
        await self.srrepo.create_requirement(dept,proj_type,title,description,deadline,year)
    async def submit_requirement(self,team_id:str,requirement_id:int,submitted_by:int,file:UploadFile):
        requirement = await self.srrepo.get_requirement(requirement_id)
        team = await self.projrepo.get_team(team_id)
        version = await self.srepo.get_next_version(team_id,requirement_id)
        if requirement is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Requirement Doesnt Exist.")
        if team is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Team Not Found.")
        if not requirement["is_active"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="This Submission Requirement is inactive.")
        if not await self.tmrepo.verify_team(team_id,submitted_by):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="You Can Only Submit For Your team.")
        if datetime.now(timezone.utc) > requirement["deadline"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Deadline is Over to Submit.")
        if team["dept"] != requirement["dept"]:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Your Department Doesnt Have this Requirement.")
        if team["project_type"].upper() != requirement["project_type"]:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Project Type Doesn't Match.")
        doc_path = await self.fservice.save(team_id,file)
        try:
            await self.srepo.add_submission(team_id,requirement_id,submitted_by,file.filename,doc_path,version)
        except Exception:
            Path(doc_path).unlink(missing_ok=True)
    async def view_team_submissions(self, team_id: str, faculty_id: int):
        if not await self.projrepo.verify_team(team_id, faculty_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You Are Only Allowed To View Submissions Of The Teams You Supervise.")
        team = await self.projrepo.get_team(team_id)
        if team is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Team Not Found.")
        rows = await self.srepo.get_team_submission_summary(team_id,team["dept"],team["project_type"])
        result = []
        for row in rows:
            data = dict(row)
            if data["submission_id"] is None:
                data["status"] = "NOT_SUBMITTED"
            result.append(data)
        return result
    async def add_remarks(self,submission_id:int,reviewer_id:int,remarks:str):
        await self.srevrepo.add_remark_review(submission_id,reviewer_id,remarks)
    async def add_approved(self,submission_id:int,reviewer_id:int):
        await self.srevrepo.add_submission_approved(submission_id,reviewer_id)
    async def get_submission_file(self,submission_id: int,faculty_id: int):
        submission = await self.srepo.get_submission_file(submission_id)
        if submission is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Submission Not Found.")
        team_id = submission["team_id"]
        if not await self.projrepo.verify_team(team_id,faculty_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You are not allowed to access this submission.")
        file_path = Path(submission["document_path"])
        if not file_path.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Submission Document Not Found.")
        return file_path, submission["document_name"]