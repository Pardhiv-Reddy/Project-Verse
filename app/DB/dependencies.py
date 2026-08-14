from app.DB.db import db
from asyncpg import Connection
from app.DB.repositories.studentrepo import StudentRepository
from app.DB.repositories.facultyrepo import FacultyRepository
from app.DB.repositories.teamstagingepo import TeamStageRepo
from app.DB.repositories.teammemberepo import TeamMembersRepo
from app.DB.repositories.projectsrepo import ProjectsRepo
from app.DB.repositories.meetingsrepo import MeetingsRepo
from app.DB.repositories.notifrecip import NotificationRecipientRepo
from app.DB.repositories.notificationsrepo import NotificationRepo
from app.DB.repositories.userrepo import UserRepository
from app.DB.repositories.subreqrepo import SubmissionRequirementRepo
from app.DB.repositories.submissionrepo import SubmissionRepo
from app.DB.repositories.subrevrepo import SubmissionReviewRepo
from app.DB.repositories.projectgithubrepo import ProjectRepositoryRepo
from app.services.TeamService import TeamService
from app.services.NotificationService import NotificationService
from app.services.AuthService import AuthService
from app.services.SubmissionService import SubmissionService 
from app.services.FileService import FileService
from app.services.GitHubRepositoryService import GitHubRepositoryService
from app.services.FacultyDashboardService import FacultyDashboardService
from app.services.StudentDashbordService import StudentDashboardService
from app.services.ProjectWorkService import ProjectWorkSpaceService
from fastapi import Depends
async def get_connection():
    async with db.pool.acquire() as conn:
        yield conn
async def get_team_service(conn:Connection=Depends(get_connection))->TeamService:
    srepo = StudentRepository(conn)
    frepo = FacultyRepository(conn)
    tsrepo = TeamStageRepo(conn)
    tmrepo = TeamMembersRepo(conn)
    projrepo = ProjectsRepo(conn)
    return TeamService(srepo,frepo,tsrepo,tmrepo,projrepo)
async def get_notification_service(conn:Connection=Depends(get_connection))->NotificationService:
    tmrepo = TeamMembersRepo(conn)
    meetrepo = MeetingsRepo(conn)
    notirepo = NotificationRepo(conn)
    notrecrepo = NotificationRecipientRepo(conn)
    projrepo = ProjectsRepo(conn)
    return NotificationService(tmrepo,notirepo,meetrepo,notrecrepo,projrepo)
async def get_auth_service(conn:Connection=Depends(get_connection))->AuthService:
    urepo = UserRepository(conn)
    frepo = FacultyRepository(conn)
    sturepo = StudentRepository(conn)
    return AuthService(urepo,frepo,sturepo)
async def get_submission_service(conn:Connection=Depends(get_connection))->SubmissionService:
    srrepo = SubmissionRequirementRepo(conn)
    srepo = SubmissionRepo(conn)
    tmrepo = TeamMembersRepo(conn)
    projrepo = ProjectsRepo(conn)
    srevrepo = SubmissionReviewRepo(conn)
    fservice = FileService()
    return SubmissionService(srepo,srrepo,tmrepo,projrepo,fservice,srevrepo)
async def get_faculty_dashboard_service(conn:Connection=Depends(get_connection))->FacultyDashboardService:
    frepo = FacultyRepository(conn)
    projrepo = ProjectsRepo(conn)
    sturepo = StudentRepository(conn)
    tmrepo = TeamMembersRepo(conn)
    srepo = SubmissionRepo(conn)
    return FacultyDashboardService(frepo,projrepo,tmrepo,sturepo,srepo)
async def get_github_service(conn:Connection=Depends(get_connection))->GitHubRepositoryService:
    projrepo = ProjectsRepo(conn)
    rrepo = ProjectRepositoryRepo(conn)
    tmrepo = TeamMembersRepo(conn)
    return GitHubRepositoryService(rrepo,projrepo,tmrepo)
async def get_student_dashboard_service(conn:Connection=Depends(get_connection))->StudentDashboardService:
    sturepo = StudentRepository(conn)
    tmrepo = TeamMembersRepo(conn)
    git_repo = ProjectRepositoryRepo(conn)
    projrepo = ProjectsRepo(conn)
    frepo = FacultyRepository(conn)
    return StudentDashboardService(sturepo,tmrepo,projrepo,frepo,git_repo)
async def get_project_workspace_dashboard_service(conn:Connection=Depends(get_connection))->ProjectWorkSpaceService:
    sturepo = StudentRepository(conn)
    tmrepo = TeamMembersRepo(conn)
    git_repo = ProjectRepositoryRepo(conn)
    projrepo = ProjectsRepo(conn)
    srepo = SubmissionRepo(conn)
    frepo = FacultyRepository(conn)
    sreqrepo = SubmissionRequirementRepo(conn)
    return ProjectWorkSpaceService(projrepo,tmrepo,frepo,srepo,git_repo,sturepo,sreqrepo)
async def get_student_repo(conn:Connection=Depends(get_connection))->StudentRepository:
    return StudentRepository(conn)
async def get_faculty_repo(conn:Connection=Depends(get_connection))->FacultyRepository:
    return FacultyRepository(conn)
async def get_team_members_repo(conn:Connection=Depends(get_connection))->TeamMembersRepo:
    return TeamMembersRepo(conn)
async def get_submissions_repo(conn:Connection=Depends(get_connection))->SubmissionRepo:
    return SubmissionRepo(conn)