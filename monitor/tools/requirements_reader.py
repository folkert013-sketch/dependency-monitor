import re
from pathlib import Path

from crewai.tools import BaseTool
from pydantic import Field


class RequirementsReaderTool(BaseTool):
    name: str = "Requirements Reader"
    description: str = (
        "Reads and parses a requirements.txt file. Returns a list of packages with their "
        "pinned or constrained versions. Input: path to requirements.txt file."
    )
    requirements_path: str = Field(default="")

    def _run(self, file_path: str = "") -> str:
        path = Path(file_path or self.requirements_path)
        if not path.exists():
            return f"ERROR: requirements.txt not found at {path}"

        packages = []
        content = path.read_text(encoding="utf-8")

        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-"):
                continue

            # Parse package name and version spec
            match = re.match(r"^([a-zA-Z0-9_.-]+(?:\[[a-zA-Z0-9_,.-]+\])?)\s*(.*)", line)
            if match:
                name = match.group(1)
                # Strip extras bracket from name for clean lookup
                clean_name = re.sub(r"\[.*?\]", "", name)
                version_spec = match.group(2).strip()
                packages.append(f"{clean_name} {version_spec}" if version_spec else clean_name)

        result = f"Found {len(packages)} packages in {path.name}:\n"
        for pkg in packages:
            result += f"  - {pkg}\n"
        return result
