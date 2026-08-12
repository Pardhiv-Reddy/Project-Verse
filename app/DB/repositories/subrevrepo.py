from asyncpg import Connection
class SubmissionReviewRepo:
    def __init__(self,conn:Connection):
        self.conn = conn
    async def add_remark_review(self,submission_id:int,reviewer_id:int,remarks:str):
        await self.conn.execute("insert into submission_reviews(submission_id,reviewer_id,status,remarks) values ($1,$2,'CHANGES_REQUIRED',$3)",submission_id,reviewer_id,remarks)
    async def add_submission_approved(self,submission_id:int,reviewer_id:int):
        await self.conn.execute("insert into submission_reviews(submission_id,reviewer_id,status) values ($1,$2,'APPROVED')",submission_id,reviewer_id)