from asyncpg import Connection
from datetime import datetime
class ProjectsRepo:
    def __init__(self,conn:Connection):
        self.conn = conn
    async def create_teams(self,rows,dept:str):
        rows = [(*row,f"{datetime.now().year}-{datetime.now().year+1}","MINI",dept)for row in rows]
        query = '''insert into projects(team_id,supervisor_id,academic_year,project_type,dept) values ($1,$2,$3,$4,$5)'''
        await self.conn.executemany(query,rows)
    async def verify_team(self,team_id:str,faculty_id:int):
        return await self.conn.fetchval("select exists (select 1 from projects where team_id = $1 and supervisor_id = $2)",team_id,faculty_id)
    async def get_team(self,id:str):
        res =  await self.conn.fetchrow("select * from projects where team_id = $1",id)
        if not res:
            return None
        return res
    async def get_supervisor_teams(self,facult_id:int,faculty_dept:str):
        res = await self.conn.fetch("select team_id,project_type,academic_year from projects where supervisor_id = $1 and dept = $2 order by project_type,team_id",facult_id,faculty_dept)
        if not res:
            return None
        return res