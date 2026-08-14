from github import Auth
from github import Github
from settings import Settings
from urllib.parse import urlparse
from datetime import datetime,timezone
from github.GithubException import UnknownObjectException
from models.github import Commit
from models.github import Contributor
from models.github import Issue
from models.github import PullRequest
from models.github import Repository
from models.github import Snapshot
from models.github import Analytics
from app.DB.repositories.projectgithubrepo import ProjectRepositoryRepo

setting = Settings()

class GitHubService:
    def __init__(self,github_repo:ProjectRepositoryRepo):
        auth = Auth.Token(setting.github_token)
        self.client = Github(auth=auth,per_page=100)
        self.github_repo = github_repo

    def extract_owner_repo(self,repo_url: str) -> tuple[str, str]:
        parsed = urlparse(repo_url)

        if parsed.scheme != "https":
            raise ValueError(f"Invalid GitHub URL: {repo_url}")

        if parsed.netloc != "github.com":
            raise ValueError(f"Invalid GitHub URL: {repo_url}")
        
        path_parts = parsed.path.strip("/").split("/")

        if len(path_parts) < 2:
            raise ValueError(f"Invalid GitHub repository URL: {repo_url}")

        owner = path_parts[0]
        repo_name = path_parts[1]

        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]
        return owner, repo_name
    
    async def get_repository(self,repo_url: str):
        owner,name = await self.extract_owner_repo(repo_url)
        try:    
            return self.client.get_repo(f"{owner}/{name}")
        except UnknownObjectException:
            raise ValueError(f"Repository not found: {repo_url}")

    async def get_readme(self,github_repo) -> str | None:
        try:
            readme = github_repo.get_readme()
            return readme.decoded_content.decode("utf-8")

        except Exception:
            return None

    async def get_rate_limit(self):
        return self.client.get_rate_limit()

    async def build_repository(self,id:int,repo_url: str)->Repository:
        github_repo = await self.get_repository(repo_url)

        return Repository(
            github_repo_id=id,
            owner=github_repo.owner.login,
            name=github_repo.name,
            url=github_repo.html_url,
            description=github_repo.description,
            default_branch=github_repo.default_branch,
            readme_content=self.get_readme(github_repo),
            registered_at=datetime.now(timezone.utc)
            )

    async def build_commit(self,github_commit) -> Commit:
        author = (github_commit.author.login if github_commit.author else github_commit.commit.author.name)

        return Commit(
            sha=github_commit.sha,
            author=author,
            date=github_commit.commit.author.date.astimezone(timezone.utc),
            message=github_commit.commit.message,
            additions=github_commit.stats.additions,
            deletions=github_commit.stats.deletions,
            files_changed=len(list(github_commit.files))
            )

    
    async def get_commits(self, repo_url: str,since:datetime,until:datetime) -> list[Commit]:
        github_repo=self.get_repository(repo_url)
        commits =[]
        github_commits = github_repo.get_commits(since=since,until=until)

        for github_commit in github_commits:
            commits.append(await self.build_commit(github_commit))

        return commits

    async def build_contributor(self,github_contributor) -> Contributor:
        return Contributor(username=github_contributor.login,contributions=github_contributor.contributions)
    
        
    async def get_contributors(self, repo_url: str) -> list[Contributor]:
        github_repo = self.get_repository(repo_url)
        contributors=[]
        github_contributors=(github_repo.get_contributors())

        for github_contributor in github_contributors:
            contributors.append(await self.build_contributor(github_contributor))

        return contributors

    async def build_pull_request(self,github_pr) -> PullRequest:
        author = (github_pr.user.login if github_pr.user else "Unknown")

        return PullRequest(
            number=github_pr.number,
            title=github_pr.title,
            body=github_pr.body,
            author=author,
            state=github_pr.state,
            created_at=github_pr.created_at.astimezone(timezone.utc),
            merged_at=(github_pr.merged_at.astimezone(timezone.utc) if github_pr.merged_at else None)
            )
     
    async def get_pull_requests(self, repo_url: str,since:datetime,until:datetime) -> list[PullRequest]:
        github_repo = self.get_repository(repo_url)
        pull_requests=[]
        github_prs=github_repo.get_pulls(state="all",sort="created",direction="desc")

        for github_pr in github_prs:
            created_at=github_pr.created_at.astimezone(timezone.utc)

            if created_at<since:
                break

            if since<=created_at<=until:
                pull_requests.append(await self.build_pull_request(github_pr))

        return pull_requests

    async def build_issue(self,github_issue) -> Issue:
        author = (github_issue.user.login if github_issue.user else "Unknown")

        return Issue(
            number=github_issue.number,
            title=github_issue.title,
            body=github_issue.body,
            author=author,
            state=github_issue.state,
            created_at=github_issue.created_at.astimezone(timezone.utc),
            closed_at=(github_issue.closed_at.astimezone(timezone.utc) if github_issue.closed_at else None)
            )

    async def get_issues(self, repo_url: str,since:datetime,until:datetime) -> list[Issue]:
        github_repo = self.get_repository(repo_url)
        issues=[]
        github_issues=github_repo.get_issues(state="all")

        for github_issue in github_issues:
            if github_issue.pull_request is not None:
                continue

            created_at = (github_issue.created_at.astimezone(timezone.utc))

            if created_at<since:
                break

            if since<=created_at <=until:
                issues.append(await self.build_issue(github_issue))

        return issues


    async def build_snapshot(self,repository:Repository,period_start:datetime,period_end:datetime) -> Snapshot:
        commits= await self.get_commits(str(repository.url),period_start,period_end)
        contributors=await self.get_contributors(str(repository.url))
        pull_requests=await self.get_pull_requests(str(repository.url),period_start,period_end)
        issues=await self.get_issues(str(repository.url),period_start,period_end)
        return Snapshot(
            repository_id=repository.github_repo_id,
            period_start=period_start,
            period_end=period_end,
            collected_at=datetime.now(timezone.utc),
            commits=commits,
            pull_requests=pull_requests,
            issues=issues,
            contributors=contributors,
        )