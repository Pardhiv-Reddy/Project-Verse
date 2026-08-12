from asyncpg import Connection
class TeamMembersRepo:
    def __init__(self,conn:Connection):
        self.conn = conn
    async def add_students(self,rows):
        query = '''insert into team_members(team_id,student_id,is_team_lead) values ($1,$2,$3)'''
        await self.conn.executemany(query,rows)
    async def get_students(self,team_id:str):
        return await self.conn.fetch("select student_id from team_members where team_id = $1",team_id)
    async def team_lead(self,id:int):
        return await self.conn.fetchval("select exists (select 1 from team_members where student_id = $1 and is_team_lead)",id)
    async def verify_team(self,team_id:str,id:int):
        return await self.conn.fetchval("select exists (select 1 from team_members where team_id = $1 and student_id = $2)",team_id,id)
    async def get_team_by_student(self,id:int):
        return await self.conn.fetchrow("Select * from team_members where student_id = $1",id)