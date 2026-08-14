from asyncpg import Connection
class ProjectRepositoryRepo:
    def __init__(self,conn:Connection):
        self.conn = conn
    async def get_by_team(self, team_id: str):
        return await self.conn.fetchrow("select id,team_id,repository_url,repository_owner,repository_name,connected_by,connected_at,is_active from project_repositories where team_id = $1 and is_active = true ",team_id)
    async def create(self,team_id: str,repository_url: str,repository_owner: str,repository_name: str,connected_by: int):
        return await self.conn.fetchrow("insert into project_repositories(team_id,repository_url,repository_owner,repository_name,connected_by) values ($1, $2, $3, $4, $5) returning * ",team_id,repository_url,repository_owner,repository_name,connected_by)
    async def get_owner_repo_name(self,team_id:str):
        return await self.conn.fetchrow("Select repository_owner,repository_name from project_repositories where team_id = $1",team_id)
    async def get_repositories_due_for_snapshot(self):
        return await self.conn.fetchrow("select pr.id,pr.repository_url,pr.repository_owner,pr.repository_name,pr.connected_at from project_repositories pr left join lateral (select captured_at from github_snapshots where repository_id = pr.id order by captured_at desc limit 1) s on true where s.captured_at is null or s.captured_at <= NOW() - INTERVAL '20 days'")