from pathlib import Path

import requests
import yaml
from bs4 import BeautifulSoup
from crewai.tools import BaseTool
from pydantic import Field


class APIStatusCheckerTool(BaseTool):
    name: str = "API Status Checker"
    description: str = (
        "Checks the deprecation/sunset status of monitored APIs (Meta/WhatsApp Graph API, "
        "Stripe, Django, etc.) by fetching their status pages. "
        "Input: 'all' to check all configured APIs, or a specific API name. "
        "Returns: status information including whether any APIs are deprecated or sunset."
    )
    config_path: str = Field(default="")

    def _run(self, api_name: str = "all") -> str:
        config_file = Path(self.config_path) if self.config_path else Path(__file__).parent.parent / "config" / "monitored_apis.yaml"

        if not config_file.exists():
            return f"ERROR: Config file not found at {config_file}"

        config = yaml.safe_load(config_file.read_text(encoding="utf-8"))
        apis = config.get("apis", [])

        if api_name.lower() != "all":
            apis = [a for a in apis if api_name.lower() in a["name"].lower()]
            if not apis:
                return f"No configured API matching '{api_name}'"

        results = []
        for api in apis:
            result = self._check_api(api)
            results.append(result)

        return "\n\n".join(results)

    def _check_api(self, api_config: dict) -> str:
        name = api_config["name"]
        status_url = api_config["status_url"]
        current_version = api_config.get("current_version", "unknown")
        api_type = api_config.get("type", "unknown")

        try:
            resp = requests.get(status_url, timeout=15, headers={
                "User-Agent": "Mozilla/5.0 (compatible; DependencyMonitor/1.0)"
            })
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            # Extract meaningful text (limit to avoid token explosion)
            text = soup.get_text(separator="\n", strip=True)[:5000]
        except requests.RequestException as e:
            return (
                f"API: {name}\n"
                f"Current version: {current_version}\n"
                f"Status: ERROR - Could not fetch status page: {e}\n"
                f"URL: {status_url}\n"
                f"ACTION: Manually check {status_url}"
            )

        return (
            f"API: {name}\n"
            f"Type: {api_type}\n"
            f"Current version in use: {current_version}\n"
            f"Status URL: {status_url}\n"
            f"--- Page content (analyze for deprecation/sunset of version {current_version}) ---\n"
            f"{text}\n"
            f"--- End of page content ---\n"
            f"INSTRUCTION: Analyze whether version {current_version} of {name} is deprecated, "
            f"sunset, or will be soon. If so, indicate what version to upgrade to."
        )
