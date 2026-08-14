from fastapi import APIRouter,Depends,UploadFile,File
from app.auth.permissions import get_team_lead,get_current_student
from app.DB.dependencies import get_submission_service,get_github_service,get_student_dashboard_service,get_project_workspace_dashboard_service,get_notification_service
from app.services.SubmissionService import SubmissionService
from app.services.GitHubRepositoryService import GitHubRepositoryService
from app.services.StudentDashbordService import StudentDashboardService
from app.services.ProjectWorkService import ProjectWorkSpaceService
from app.services.NotificationService import NotificationService
from app.models.submissions import GitHubRepositoryRequest
router = APIRouter(prefix="/Student",tags=["Student"])
@router.get("/dashboard")
async def student_dashboard(student=Depends(get_current_student),service: StudentDashboardService = Depends(get_student_dashboard_service)):
    return await service.get_dashboard(student)
@router.post("/teams/{team_id}/submission/{requirement_id}")
async def Submit(team_id:str,requirement_id:int,file : UploadFile = File(...),service : SubmissionService = Depends(get_submission_service),student = Depends(get_team_lead)):
    await service.submit_requirement(team_id,requirement_id,student,file)
@router.post("/teams/{team_id}/github")
async def connect_github(team_id:str,req:GitHubRepositoryRequest,student_id=Depends(get_team_lead),service:GitHubRepositoryService = Depends(get_github_service)):
    repository = await service.connect_repository(team_id,student_id,str(req.repository_url))
    return {
        "message": "GitHub Repository Connected Successfully.",
        "repository": {
            "team_id": repository["team_id"],
            "repository_url": repository["repository_url"],
            "repository_owner": repository["repository_owner"],
            "repository_name": repository["repository_name"]
        }
    }
@router.get("/teams/{team_id}/github")
async def get_github_repository(team_id: str,student_id=Depends(get_current_student),service: GitHubRepositoryService = Depends(get_github_service)):
    repository = await service.get_repository(team_id,student_id)
    return {
        "team_id": repository["team_id"],
        "repository_url": repository["repository_url"],
        "repository_owner": repository["repository_owner"],
        "repository_name": repository["repository_name"],
        "connected_at": repository["connected_at"]
    }
@router.get("/teams/{team_id}/project")
async def project_workspace(team_id: str,student_id=Depends(get_current_student),service: ProjectWorkSpaceService = Depends(get_project_workspace_dashboard_service)):
    return await service.get_project_page(team_id,student_id)
@router.get("/notifications")
async def get_notifications(student_id=Depends(get_current_student),service: NotificationService = Depends(get_notification_service)):
    return await service.get_student_notifications(student_id)
@router.patch("/notifications/{recipient_id}/read")
async def mark_notification_read(recipient_id: int,student_id=Depends(get_current_student),service: NotificationService = Depends(get_notification_service)):
    return await service.mark_student_notification_read(recipient_id,student_id)