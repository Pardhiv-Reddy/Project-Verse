from app.DB.repositories.teammemberepo import TeamMembersRepo
from app.DB.repositories.notificationsrepo import NotificationRepo
from app.DB.repositories.meetingsrepo import MeetingsRepo
from app.DB.repositories.notifrecip import NotificationRecipientRepo
from app.DB.repositories.projectsrepo import ProjectsRepo
from fastapi import HTTPException,status
from datetime import datetime
class NotificationService:
    def __init__(self,tmrepo:TeamMembersRepo,notirepo:NotificationRepo,meetrepo:MeetingsRepo,notrecrepo:NotificationRecipientRepo,projrepo:ProjectsRepo):
        self.tmrepo = tmrepo
        self.notirepo = notirepo
        self.notrecrepo = notrecrepo
        self.meetrepo = meetrepo
        self.projrepo = projrepo
    async def schedule_meeting(self,faculty_id:int,title:str,description:str,time:datetime,venue:str,team_id:str,message:str):
        if not await self.projrepo.verify_team(team_id,faculty_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You Can Only Schedule Meeting With The Teams You Supervise.")
        meeting_id = await self.meetrepo.create_meeting(title,description,time,venue,team_id)
        notification_id = await self.notirepo.create_notification("MEETING",title,message,meeting_id)
        members = await self.tmrepo.get_students(team_id)
        await self.notrecrepo.add_students(members,notification_id)
    async def re_submission(self,faculty_id:int,title:str,team_id:str,message:str):
        if not await self.projrepo.verify_team(team_id,faculty_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You Can Only Request for Re - Submission For The Teams You Supervise.")
        notification_id = await self.notirepo.create_notification("REMARK",title,message,None)
        members = await self.tmrepo.get_students(team_id)
        await self.notrecrepo.add_students(members,notification_id)
    async def approved(self,faculty_id:int,title:str,team_id:str):
        if not await self.projrepo.verify_team(team_id,faculty_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You Can Only Approve Submission For The Teams You Supervise.")
        notification_id = await self.notirepo.create_notification("REMARK",title,"APPROVED",None)
        members = await self.tmrepo.get_students(team_id)
        await self.notrecrepo.add_students(members,notification_id)
    async def get_student_notifications(self,student_id: int):
        notifications = await self.notirepo.get_student_notifications(student_id)
        unread_count = sum(1 for notification in notifications if not notification["is_read"])
        return {
            "unread_count": unread_count,
            "notifications": [
                {
                    "recipient_id": notification["recipient_id"],
                    "notification_id": notification["notification_id"],
                    "type": notification["type"],
                    "title": notification["title"],
                    "message": notification["message"],
                    "reference_id": notification["reference_id"],
                    "created_at": notification["created_at"],
                    "is_read": notification["is_read"],
                    "read_at": notification["read_at"]
                }for notification in notifications]}
    async def mark_student_notification_read(self,recipient_id:int,student_id: int):
        result = await self.notrecrepo.mark_notification_read(recipient_id,student_id)
        if result == "UPDATE 0":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Notification Not Found.")
        return {"message": "Notification Marked As Read."}