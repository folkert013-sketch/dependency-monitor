import os
import re

import requests
from crewai.tools import BaseTool


class GitHubChangelogTool(BaseTool):
    name: str = "GitHub Changelog"
    description: str = (
        "Fetches release notes from a GitHub repository to identify breaking changes. "
        "Input: GitHub repository URL or 'owner/repo' format (e.g. 'django/django' or "
        "'https://github.com/django/django'). "
        "Returns: recent release notes focusing on breaking changes and deprecations."
    )

    def _run(self, repo: str) -> str:
        # Parse owner/repo from URL or direct input
        repo = repo.strip()
        match = re.match(r"(?:https?://github\.com/)?([^/]+/[^/]+?)(?:\.git)?/?$", repo)
        if not match:
            return f"ERROR: Could not parse GitHub repo from '{repo}'. Use 'owner/repo' format."

        owner_repo = match.group(1)

        headers = {"Accept": "application/vnd.github.v3+json"}
        token = os.environ.get("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"token {token}"

        try:
            resp = requests.get(
                f"https://api.github.com/repos/{owner_repo}/releases",
                params={"per_page": 5},
                headers=headers,
                timeout=15,
            )
            if resp.status_code == 404:
                return f"{owner_repo}: Repository not found or no releases."
            resp.raise_for_status()
        except requests.RequestException as e:
            return f"{owner_repo}: ERROR fetching releases - {e}"

        releases = resp.json()
        if not releases:
            return f"{owner_repo}: No releases found."

        results = []
        for release in releases[:5]:
            tag = release.get("tag_name", "unknown")
            name = release.get("name", "")
            body = release.get("body", "") or ""

            # Truncate very long release notes
            if len(body) > 2000:
                body = body[:2000] + "\n... (truncated)"

            results.append(
                f"=== {tag} {f'- {name}' if name and name != tag else ''} ===\n"
                f"{body}\n"
            )

        header = (
            f"GitHub releases for {owner_repo} (latest {len(releases)}):\n"
            f"INSTRUCTION: Analyze these release notes for BREAKING CHANGES and "
            f"DEPRECATIONS only. Ignore minor features and bug fixes.\n\n"
        )
        return header + "\n".join(results)
