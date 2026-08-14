from asyncpg import Connection
import json
class GitHubSnapshotRepo:
    def __init__(self, conn: Connection):
        self.conn = conn
    async def get_latest_snapshot(self, repository_id: int):
        return await self.conn.fetchrow(
            "select id,repository_id,period_start,period_end,captured_at,snapshot from github_snapshots where repository_id = $1 order by captured_at desc limit 1",repository_id)
    async def add_snapshot(self,repository_id: int,period_start,period_end,captured_at,snapshot: dict):
        return await self.conn.fetchrow("insert into github_snapshots (repository_id,period_start,period_end,captured_at,snapshot)values ($1, $2, $3, $4, $5) returning id ",repository_id,period_start,period_end,captured_at,json.dumps(snapshot))