from fastapi import Depends, HTTPException,status
from app.auth.security import get_current_user
from app.models.users import CurrentUser
from app.DB.dependencies import get_student_repo, get_faculty_repo,get_team_members_repo
from app.DB.repositories.studentrepo import StudentRepository
from app.DB.repositories.facultyrepo import FacultyRepository
from app.DB.repositories.teammemberepo import TeamMembersRepo
async def get_current_student(current_user: CurrentUser = Depends(get_current_user),student_repo: StudentRepository = Depends(get_student_repo)):
    if current_user.role != "Student":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You Are Not a Student.")
    student = await student_repo.get_student_id(current_user.id)
    if student is None:
        raise HTTPException(status_code=403,detail="You Are not Eligible for Mini / Major Section.")
    return student
async def get_current_faculty(current_user: CurrentUser = Depends(get_current_user),faculty_repo: FacultyRepository = Depends(get_faculty_repo)):
    if current_user.role != "Faculty":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Faculty Access Only.")
    faculty = await faculty_repo.get_by_user_id(current_user.id)
    if faculty is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Faculty record not found.")
    return faculty
async def get_current_coordinator(faculty = Depends(get_current_faculty)):
    if not faculty["is_coordinator"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You Are Not A Project Coordinator")
    return faculty
async def get_current_hod(faculty = Depends(get_current_faculty)):
    if not faculty["is_hod"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You Are Not The HoD.")
    return faculty
async def get_team_lead(student_id = Depends(get_current_student),trepo : TeamMembersRepo = Depends(get_team_members_repo)):
    if not await trepo.team_lead(student_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only Team Lead can Submit.")
    return student_id