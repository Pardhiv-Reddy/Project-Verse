from collections import Counter
from datetime import datetime
from models.github import Analytics
from models.github import Snapshot


class AnalyticsService:

    def get_total_commits(self,snapshot: Snapshot)->int:
        return len(snapshot.commits)

    def get_total_contributors(self,snapshot: Snapshot)->int:
        return len(self.get_contribution_breakdown(snapshot))

    def get_total_additions(self,snapshot: Snapshot)->int:
        return sum(commit.additions for commit in snapshot.commits)

    def get_total_deletions(self,snapshot: Snapshot)->int:
        return sum(commit.deletions for commit in snapshot.commits)

    def get_total_files_changed(self,snapshot: Snapshot)->int:
        return sum(commit.files_changed for commit in snapshot.commits)

    def get_open_prs(self,snapshot: Snapshot)->int:
        return sum(1 for pr in snapshot.pull_requests if pr.state == "open")

    def get_merged_prs(self,snapshot: Snapshot)->int:
        return sum(1 for pr in snapshot.pull_requests if pr.merged_at is not None)

    def get_open_issues(self,snapshot: Snapshot) -> int:
        return sum(1 for issue in snapshot.issues if issue.state == "open")

    def get_closed_issues(self,snapshot: Snapshot)->int:
        return sum(1 for issue in snapshot.issues if issue.state == "closed")

    def get_last_activity(self,snapshot: Snapshot)->datetime|None:
        if not snapshot.commits:
            return None

        return max(commit.date for commit in snapshot.commits)

    def get_contribution_breakdown(self,snapshot: Snapshot)->dict[str, int]:
        contributions = Counter()
        for commit in snapshot.commits:
            contributions[commit.author] += 1
        return dict(contributions)

    def get_contribution_percentages(self,snapshot: Snapshot)->dict[str, float]:
        breakdown = self.get_contribution_breakdown(snapshot)
        total = sum(breakdown.values())
        if total == 0:
            return {}

        return {author: round((count / total) * 100,2) for author, count in breakdown.items()}

    def get_commit_messages(self,snapshot: Snapshot)->list[str]:
        return [commit.message for commit in snapshot.commits]

    def get_active_contributors(self,snapshot: Snapshot)->int:
        return len(self.get_contribution_breakdown(snapshot))

    def get_top_contributors(self,snapshot: Snapshot,limit: int = 3)->list[tuple[str, int]]:
        breakdown = self.get_contribution_breakdown(snapshot)
        return sorted(breakdown.items(),key=lambda item: item[1],reverse=True)[:limit]

    def get_period_days(self,snapshot: Snapshot)->int:
        return (snapshot.period_end -snapshot.period_start).days

    def get_changed_files(self,snapshot: Snapshot)->list[str]:
        files = set()
        for commit in snapshot.commits:
            files.update(commit.changed_files)

        return sorted(files)


    def build_analytics(self,snapshot: Snapshot)->Analytics:
        return Analytics(
            period_start=snapshot.period_start,
            period_end=snapshot.period_end,
            total_commits=self.get_total_commits(snapshot),
            total_contributors=self.get_total_contributors(snapshot),
            total_additions=self.get_total_additions(snapshot),
            total_deletions=self.get_total_deletions(snapshot),
            total_files_changed=self.get_total_files_changed(snapshot),
            open_prs=self.get_open_prs(snapshot),
            merged_prs=self.get_merged_prs(snapshot),
            open_issues=self.get_open_issues(snapshot),
            closed_issues=self.get_closed_issues(snapshot),
            last_activity=self.get_last_activity(snapshot),
            contribution_breakdown=self.get_contribution_breakdown(snapshot),
            contribution_percentages=self.get_contribution_percentages(snapshot),
            commit_messages=self.get_commit_messages(snapshot),
            active_contributors=self.get_active_contributors(snapshot),
            top_contributors=self.get_top_contributors(snapshot),
            period_days=self.get_period_days(snapshot),
            changed_files=self.get_changed_files(snapshot)
        )