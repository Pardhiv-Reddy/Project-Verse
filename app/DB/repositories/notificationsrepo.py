from asyncpg import Connection
class NotificationRepo:
    def __init__(self,conn:Connection):
        self.conn = conn
    async def create_notification(self,type:str,title:str,message:str,id:int | None):
        id = await self.conn.fetchval("insert into notifications(type,title,message,reference_id) values ($1,$2,$3,$4) returning id",type,title,message,id)
        return id
    async def get_student_notifications(self,student_id:int):
        return await self.conn.fetch("select nr.id AS recipient_id,n.id AS notification_id,n.type,n.title,n.message,n.reference_id,n.created_at,nr.is_read,nr.read_at from notification_recipients nr join notifications n on n.id = nr.notification_id where nr.student_id = $1 order by n.created_at desc",student_id)