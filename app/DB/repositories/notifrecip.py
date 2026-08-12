from asyncpg import Connection
from typing import Any
class NotificationRecipientRepo:
    def __init__(self,conn:Connection):
        self.conn = conn
    async def add_students(self,members:list[Any],id:int):
        rows = [(id,m["student_id"])for m in members]
        query = '''insert into notification_recipients(notification_id,student_id) values ($1,$2)'''
        await self.conn.executemany(query,rows)
    async def mark_notification_read(self,recipient_id: int,student_id: int):
        return await self.conn.execute("update notification_recipients set is_read = true,read_at = NOW() where id = $1 and student_id = $2",recipient_id,student_id)