from models.github import Analytics
class SummaryService:

    def build_summary_context(self,analytics_history: list[Analytics]) -> str:
        if not analytics_history:
            return "No analytics data available."
        sections = []
        for index, analytics in enumerate(analytics_history, start=1):
            section = f"""
            Analytics Period {index}
            Period:
            {analytics.period_start} to {analytics.period_end}
            Commits:
            {analytics.total_commits}
            Contributors:
            {analytics.total_contributors}
            Code Changes:
            Additions: {analytics.total_additions}
            Deletions: {analytics.total_deletions}
            Files Changed Count: {len(analytics.changed_files)}
            Pull Requests:
            Open PRs: {analytics.open_prs}
            Merged PRs: {analytics.merged_prs}
            Issues:
            Open Issues: {analytics.open_issues}
            Closed Issues: {analytics.closed_issues}
            Last Activity:
            {analytics.last_activity}
            Contribution Percentages:
            {analytics.contribution_percentages}
            Top Contributors:
            {analytics.top_contributors}
            Changed Files:
            {", ".join(analytics.changed_files[:30])}
            Commit Messages:
            {chr(10).join(f"- {message}" for message in analytics.commit_messages[-20:])}
            """
            sections.append(section.strip())

        return "\n\n".join(sections)

    def build_prompt(self,analytics_history: list[Analytics]) -> str:
        if not analytics_history:
            raise ValueError("No analytics available for summary generation.")
        context = self.build_summary_context(analytics_history)
        review_start = analytics_history[0].period_start
        review_end = analytics_history[-1].period_end

        return f"""
You are evaluating a student software project repository.

Review Period:
{review_start} to {review_end}

Analyze the repository activity across the review period.

Your task is to determine:

1. Project Progress Overview
2. Feature Development Status
3. Contribution Analysis
4. Potential Concerns
5. Supervisor Recommendation

Guidelines:

- Use only the provided analytics.
- Infer completed and ongoing features from commit messages and changed files.
- Infer contribution distribution from contribution percentages.
- Identify low activity areas if evidence exists.
- Do not invent technologies or features that are not present.
- Keep the report concise and professional.

Analytics History:

{context}

Generate the report in the following format:

Project Progress Overview

Feature Development Status

Completed:
- ...

Under Development:
- ...

Limited Activity:
- ...

Contribution Analysis

Potential Concerns

Supervisor Recommendation
"""

    async def generate_summary(self,analytics_history: list[Analytics],ai_service) -> str:
        prompt = self.build_prompt(analytics_history)
        response = await ai_service.generate(prompt)
        return response