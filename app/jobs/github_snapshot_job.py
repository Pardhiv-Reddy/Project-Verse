import asyncio
from app.DB.db import db
from app.DB.repositories.projectgithubrepo import ProjectRepositoryRepo
from app.DB.repositories.snapshotrepo import GitHubSnapshotRepo
from app.services.GitHubService import GitHubService
from app.services.SnapshotService import SnapshotService
from app.models.github import Repository
async def run():
    await db.connect()
    try:
        async with db.pool.acquire() as conn:
            project_repo = ProjectRepositoryRepo(conn)
            snapshot_repo = GitHubSnapshotRepo(conn)
            github_service = GitHubService(project_repo)
            snapshot_service = SnapshotService(snapshot_repo=snapshot_repo,github_service=github_service)
            repositories = await project_repo.get_repositories_due_for_snapshot()
            for repository in repositories:
                    rep = github_service.build_repository(repository["id"],repository["repository__url"])
                    await snapshot_service.capture_snapshot(rep)
    finally:
        await db.close()
if __name__ == "__main__":
    asyncio.run(run())