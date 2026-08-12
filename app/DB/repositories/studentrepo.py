'''
id serial primary key

'''
from asyncpg import Connection
from app.models.model import Person
class StudentRepository:
    def __init__(self,conn:Connection):
        self.conn = conn
    async def fetch_students(self,dept: str,year: int,section: str,limit :int ,offset : int) -> list[Person]:
        rows =  await self.conn.fetch("select id,roll,name,cgpa,dept from student where dept = $1 and year = $2 and section = $3 order by cgpa desc limit $4 offset $5",dept,year,section,limit,offset)
        return [Person(**dict(row)) for row in rows]
    async def get_count(self,dept:str,year: int,section: str)->int:
        return await self.conn.fetchval("select count(*) from student where dept = $1 and year = $2 and section = $3",dept,year,section)
    async def get_remaining_students(self,dept: str,year: int,section: str,remaining):
        return await self.conn.fetch("select id,roll,name,cgpa,dept from student where dept = $1 and year = $2 and section = $3 order by cgpa asc limit $4",dept,year,section,remaining)
    async def get_student_id(self,user_id: int) -> int | None:
        return await self.conn.fetchval("select id from student where user_id = $1",user_id)
    async def get_student(self,user_id:int):
        return await self.conn.execute("select * from student where user_id = $1",user_id)
    async def get_details(self,id:int):
        return await self.conn.fetchrow("select * from student where id = $1",id)
    async def add_user_id(self,user_id:int,roll:str):
        await self.conn.execute("update student set user_id = $1 where roll = $2",user_id,roll)