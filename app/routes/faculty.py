from fastapi import APIRouter,Depends
from fastapi.responses import FileResponse
from uuid import UUID
import mimetypes
from datetime import datetime
from app.DB.dependencies import get_team_service,get_notification_service,get_submission_service,get_faculty_dashboard_service
from app.models.Faculty import TeamRequest,MeetingRequest,SubmissionRequirement,RemarkRequest
from app.services.TeamService import TeamService
from app.services.NotificationService import NotificationService
from app.services.SubmissionService import SubmissionService
from app.services.FacultyDashboardService import FacultyDashboardService
from app.auth.permissions import get_current_faculty,get_current_coordinator,get_current_hod
router = APIRouter(prefix="/Faculty",tags=["Faculty"])
@router.post("/generate/teams",response_model= UUID)
async def form_teams(req:TeamRequest,service:TeamService=Depends(get_team_service),coordinator = Depends(get_current_coordinator)):
    session_id = await service.generate_teams(req.dept,req.year,req.sections,req.team_size)
    return session_id
@router.get("/team-generation/{session_id}")
async def get_teams(session_id:UUID,service:TeamService=Depends(get_team_service),coordinator = Depends(get_current_coordinator)):
    return await service.get_teams(session_id)
@router.post("/teams/{session_id}/publish")
async def publish_teams(session_id:UUID,service:TeamService=Depends(get_team_service),coordinator = Depends(get_current_coordinator)):
    await service.publish(session_id,coordinator["dept"])
    return {"Message":"Posted To Projects Table Successfully."}
@router.post("/teams/{team_id}/meeting",response_model=str)
async def schedule_meeting(req:MeetingRequest,team_id:str,service:NotificationService=Depends(get_notification_service),faculty = Depends(get_current_faculty)):
    await service.schedule_meeting(faculty["id"],req.title,req.description,req.meeting_time,req.venue,team_id,req.notification_message)
    return f"Scheduled Meeting with Team {team_id} at {req.meeting_time} Successfully."
@router.post("/submission/requirement",response_model=str)
async def post_requirements(req:SubmissionRequirement,service:SubmissionService= Depends(get_submission_service),hod = Depends(get_current_hod)):
    await service.add_submission_requirement(hod["dept"],req.proj_type,req.title,req.description,req.deadline,f"{datetime.now().year}-{datetime.now().year+1}")
    return f"Successfully Posted {req.title} Requirement Under {hod['dept']}."
@router.post("/teams/{team_id}/submissions/{submission_id}/review",response_model=str)
async def changes_required(team_id:str,submission_id:int,req:RemarkRequest,notification_service:NotificationService=Depends(get_notification_service),service : SubmissionService = Depends(get_submission_service),faculty = Depends(get_current_faculty)):
    await service.add_remarks(submission_id,faculty["id"],req.remarks)
    await notification_service.re_submission(faculty["id"],"Requires Re - Submission",team_id,req.remarks)
    return f"Requested Team : {team_id} For ReSubmission."
@router.post("/teams/{team_id}/submissions/{submission_id}/approve",response_model=str)
async def approve_submission(team_id:str,submission_id:int,notification_service:NotificationService=Depends(get_notification_service),service : SubmissionService = Depends(get_submission_service),faculty = Depends(get_current_faculty)):
    await service.add_approved(submission_id,faculty["id"])
    await notification_service.approved(faculty["id"],"Approved Submission",team_id)
    return f"Approved Submission."
@router.get("/dashboard")
async def faculty_dashboard(faculty=Depends(get_current_faculty),service: FacultyDashboardService = Depends(get_faculty_dashboard_service)):
    return await service.get_dashboard(faculty["id"])
@router.get("/teams/{team_id}")
async def get_team_details(team_id:str,faculty=Depends(get_current_faculty),service : FacultyDashboardService = Depends(get_faculty_dashboard_service)):
    return await service.get_team_detail(faculty["id"],team_id)
@router.get("/teams/{team_id}/submissions")
async def view_submissions(team_id:str,service : SubmissionService = Depends(get_submission_service),faculty = Depends(get_current_faculty)):
    return await service.view_team_submissions(team_id,faculty["id"])
@router.get("/submissions/{submission_id}/download")
async def download_submission(submission_id:int,faculty=Depends(get_current_faculty),service:SubmissionService=Depends(get_submission_service)):
    file_path, file_name = await service.get_submission_file(submission_id,faculty["id"])
    media_type, _ = mimetypes.guess_type(file_name)
    return FileResponse(path=file_path,media_type=media_type or "application/octet-stream",filename=file_name)