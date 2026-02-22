import re

import requests
from crewai.tools import BaseTool
from packaging.version import InvalidVersion, Version


class PyPIVersionCheckerTool(BaseTool):
    name: str = "PyPI Version Checker"
    description: str = (
        "Checks the latest stable version of a Python package on PyPI. "
        "Input: a package name (e.g. 'django' or 'requests'). "
        "Returns: current latest version, whether it's a major update, and the GitHub URL if available."
    )

    def _run(self, package_name: str) -> str:
        package_name = package_name.strip().lower()
        # Clean extras from name
        package_name = re.sub(r"\[.*?\]", "", package_name)

        try:
            resp = requests.get(
                f"https://pypi.org/pypi/{package_name}/json",
                timeout=10,
            )
            if resp.status_code == 404:
                return f"{package_name}: NOT FOUND on PyPI"
            resp.raise_for_status()
        except requests.RequestException as e:
            return f"{package_name}: ERROR fetching from PyPI - {e}"

        data = resp.json()
        latest = data["info"]["version"]

        # Get project URLs for GitHub link
        project_urls = data["info"].get("project_urls") or {}
        github_url = ""
        for key, url in project_urls.items():
            if "github.com" in (url or ""):
                github_url = url
                break
        if not github_url:
            home_page = data["info"].get("home_page") or ""
            if "github.com" in home_page:
                github_url = home_page

        # Check if it's a pre-release
        try:
            v = Version(latest)
            is_prerelease = v.is_prerelease
        except InvalidVersion:
            is_prerelease = False

        result = f"Package: {package_name}\n"
        result += f"Latest version: {latest}\n"
        if is_prerelease:
            result += "Note: Latest version is a pre-release\n"
        if github_url:
            result += f"GitHub: {github_url}\n"
        result += f"Summary: {data['info'].get('summary', 'N/A')}\n"

        return result
