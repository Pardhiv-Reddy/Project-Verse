from asyncpg import Connection
from datetime import datetime
class SubmissionRequirementRepo:
    def __init__(self,conn:Connection):
        self.conn = conn
    async def create_requirement(self,dept:str,proj_type:str,title:str,description:str,deadline:datetime,year:str):
        await self.conn.execute("insert into submission_requirements(dept,project_type,title,description,deadline,academic_year) values ($1,$2,$3,$4,$5,$6)",dept,proj_type,title,description,deadline,year)
    async def get_requirement(self,id:int):
        return await self.conn.fetchrow("select * from submission_requirements where id = $1",id)
    async def get_project_timeline(self,dept:str,project_type:str,academic_year:str):
        return await self.conn.fetch("select id,title,description,start_date,deadline from submission_requirements where dept = $1 and project_type = $2 and academic_year = $3 and start_date is not null order by start_date asc",dept,project_type,academic_year)