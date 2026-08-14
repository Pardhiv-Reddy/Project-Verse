from asyncpg import Connection
class SubmissionRepo:
    def __init__(self,conn:Connection):
        self.conn = conn
    async def add_submission(self,team_id:str,requirement_id:int,document_name:str,document_path:str,version:int):
        await self.conn.execute("insert into submissions(team_id,requirement_id,document_name,document_path,version,status) values ($1,$2,$3,$4,$5,$6,'APPROVED')",team_id,requirement_id,document_name,document_path,version)
    async def view_submissions(self,team_id:str):
        res = await self.conn.fetch("select document_name,document_path from submissions where team_id = $1",team_id)
        if not res:
            return None
        return res
    async def get_next_version(self,team_id: str,requirement_id: int) -> int:
        version = await self.conn.fetchval("select coalesce(max(version), 0) + 1 from submissions where team_id = $1 and requirement_id = $2",team_id,requirement_id)
        return version
    async def get_team_submission_summary(self,team_id: str,dept: str,project_type: str):
        query = "select r.id as requirement_id,r.title,r.description,r.deadline,s.id AS submission_id,s.version,s.status,s.document_name,s.document_path,s.submitted_at,sr.status as review_status,sr.remarks as review_remarks,sr.reviewed_at from submission_requirements r left join (select * from (select s.*,row_number() over (partition by s.team_id, s.requirement_id order by s.version desc) as rn from submissions s where s.team_id = $1 ) latest where latest.rn = 1) s on s.requirement_id = r.id left join submission_reviews sr on sr.submission_id = s.id where r.dept = $2 and r.project_type = $3 order by r.deadline;"
        return await self.conn.fetch(query,team_id,dept,project_type)
    async def get_submission_file(self, submission_id: int):
        return await self.conn.fetchrow("select id,team_id,document_name,document_path from submissions where id = $1",submission_id)
    async def update_status(self,submission_id:int,status:str):
        await self.conn.execute("update submissions set status = $1 where id = $2",status,submission_id)