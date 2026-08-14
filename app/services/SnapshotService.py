from app.DB.repositories.snapshotrepo import GitHubSnapshotRepo
from app.services.GitHubService import GitHubService
from app.models.github import Repository
from datetime import datetime, timedelta, timezone
class SnapshotService:
    def __init__(self,snapshot_repo:GitHubSnapshotRepo,github_service:GitHubService):
        self.snapshot_repo = snapshot_repo
        self.github_service = github_service
    async def capture_snapshot(self, repository:Repository):
        now = datetime.now(timezone.utc)
        last_snapshot = await self.snapshot_repo.get_latest_snapshot(repository["id"])
        if last_snapshot is None:
            period_start = repository["connected_at"]
        else:
            period_start = last_snapshot["period_end"]
        period_end = now
        snapshot = await self.github_service.build_snapshot(repository,period_start,period_end)
        await self.snapshot_repo.add_snapshot(repository_id=repository["id"],period_start=period_start,period_end=period_end,captured_at=now,snapshot=snapshot.model_dump())