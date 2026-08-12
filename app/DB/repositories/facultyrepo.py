from asyncpg import Connection
class FacultyRepository:
    def __init__(self,conn : Connection):
        self.conn = conn
    async def get_faculty(self,dept:str):
        return await self.conn.fetch("select id,eid,name,designation,is_dr from Faculty where dept = $1",dept)
    async def get_assistants_by_experience(self,dept:str):
        return await self.conn.fetch("select id,eid,name,designation,is_dr from Faculty where dept = $1 and designation = 'Assistant Professor' and is_dr = False order by experience desc",dept)
    async def get_faculty_id(self,user_id:int):
        return await self.conn.fetchval("select id from Faculty where user_id = $1",user_id)
    async def get_by_user_id(self,user_id: int):
        return await self.conn.fetchrow("select * from Faculty where user_id = $1",user_id)
    async def add_user_id(self,user_id: int,eid: str) -> bool:
        result = await self.conn.execute("update Faculty set user_id = $1 where eid = $2",user_id,eid)
        return result == "UPDATE 1"
    async def get_faculty_by_id(self,id:int):
        return await self.conn.fetchrow("select * from Faculty where id = $1",id)