from asyncpg import Record,Connection
from uuid import UUID
class TeamStageRepo:
    def __init__(self,conn:Connection):
        self.conn = conn
    async def create_teams(self,rows,session_id):
        rows = [(*row, session_id)for row in rows]
        query = '''INSERT INTO team_staging(team_id, supervisor_id, dept, section,session_id)VALUES ($1,$2,$3, $4,$5)'''
        await self.conn.executemany(query,rows)
    async def retrieve_teams(self,session_id:UUID,dept:str,section:str)->list[Record]:
        res =  await self.conn.fetch("select team_id from team_staging where session_id = $1 and dept = $2 and section = $3",session_id,dept,section)
        return res
    async def allot_supervisor(self,session_id:UUID,tid:str,sid:int):
        await self.conn.execute("update team_staging set supervisor_id = $1 where session_id = $2 and team_id = $3",sid,session_id,tid)
    async def get_remaining_teams(self,dept:str):
        return await self.conn.fetch("select team_id from team_staging where supervisor_id is null and dept = $1",dept)
    async def delete_done_teams(self,session_id:UUID):
        await self.conn.execute("delete from team_staging where session_id = $1",session_id)
    async def get_teams(self,session_id:UUID):
        res = await self.conn.fetch("select team_id,supervisor_id from team_staging where session_id = $1 order by id asc",session_id)
        if not res:
            return None
        return res