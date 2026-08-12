from fastapi import HTTPException, status
from urllib.parse import urlparse
from app.DB.repositories.projectgithubrepo import ProjectRepositoryRepo
from app.DB.repositories.projectsrepo import ProjectsRepo
from app.DB.repositories.teammemberepo import TeamMembersRepo
class GitHubRepositoryService:
    def __init__(self, repo:ProjectRepositoryRepo, projrepo:ProjectsRepo, tmrepo:TeamMembersRepo):
        self.repo = repo
        self.projrepo = projrepo
        self.tmrepo = tmrepo
    async def connect_repository(self,team_id: str,student_id: int,repository_url: str):
        team = await self.projrepo.get_team(team_id)
        if team is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Team Not Found.")
        if not await self.tmrepo.verify_team(team_id,student_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You are not a member of this team.")
        parsed = urlparse(repository_url)
        if parsed.netloc.lower() != "github.com":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Only GitHub repositories are supported.")
        parts = [part for part in parsed.path.strip("/").split("/")if part]
        if len(parts) != 2:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid GitHub repository URL.")
        owner, repository_name = parts
        repository_name = repository_name.removesuffix(".git")
        existing = await self.repo.get_by_team(team_id)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="A GitHub repository is already connected to this team.")
        return await self.repo.create(team_id,str(repository_url),owner,repository_name,student_id)
    async def get_repository(self,team_id: str,student_id: int):
        if not await self.tmrepo.verify_team(team_id,student_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You are not a member of this team.")
        repository = await self.repo.get_by_team(team_id)
        if repository is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No GitHub Repository Connected To This Team.")
        return repository