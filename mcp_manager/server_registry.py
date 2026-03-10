from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional


DEFAULT_EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "mcp_manager",
    "ui",
    "configs",
}


@dataclass(frozen=True)
class MCPServer:
    server_id: str
    display_name: str
    project_dir: Path
    server_script: Path
    working_dir: Path
    config_filename: str
    env_template_path: Optional[Path]

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["project_dir"] = str(self.project_dir)
        payload["server_script"] = str(self.server_script)
        payload["working_dir"] = str(self.working_dir)
        payload["env_template_path"] = (
            str(self.env_template_path) if self.env_template_path else None
        )
        return payload


def _normalize_server_id(name: str) -> str:
    cleaned = name.lower().replace("-", "_").replace(" ", "_")
    for token in ["_mcp_tools", "_mcp_tool", "_mcp_server", "_tools"]:
        cleaned = cleaned.replace(token, "")
    cleaned = "_".join(part for part in cleaned.split("_") if part)
    return cleaned or "mcp_server"


def _display_name_from_folder(name: str) -> str:
    parts = [chunk for chunk in name.replace("-", " ").replace("_", " ").split(" ") if chunk]
    return " ".join(part.capitalize() for part in parts)


def _suggest_config_filename(server_id: str, display_name: str) -> str:
    lowered = f"{server_id} {display_name}".lower()
    if "jira" in lowered:
        return "jira.env"
    if "bitbucket" in lowered:
        return "bitbucket.env"
    if "postgres" in lowered or "database" in lowered or server_id.startswith("db"):
        return "database.env"
    return f"{server_id}.env"


def _find_nearest_env_template(server_script: Path, project_dir: Path) -> Optional[Path]:
    search_roots = [server_script.parent, project_dir]
    seen = set()
    for root in search_roots:
        if root in seen:
            continue
        seen.add(root)
        env_candidates = [
            root / "config" / "config.env",
            root / "config.env",
            root / ".env.example",
            root / ".env",
        ]
        for candidate in env_candidates:
            if candidate.exists():
                return candidate

    for candidate in project_dir.rglob("config.env"):
        if candidate.is_file():
            return candidate
    return None


def _is_ignored_path(path: Path) -> bool:
    return any(part in DEFAULT_EXCLUDED_DIRS or part.startswith(".") for part in path.parts)


def _project_dir_from_server_script(root_dir: Path, server_script: Path) -> Path:
    # If server is under src/server.py, treat src parent as project folder.
    if server_script.parent.name.lower() == "src" and server_script.parent.parent != root_dir:
        return server_script.parent.parent
    return server_script.parent


def discover_servers(root_dir: Path) -> Dict[str, MCPServer]:
    root_dir = root_dir.resolve()
    servers: Dict[str, MCPServer] = {}

    for server_script in root_dir.rglob("server.py"):
        if not server_script.is_file():
            continue
        if _is_ignored_path(server_script.relative_to(root_dir)):
            continue
        if server_script.parent == root_dir:
            continue

        project_dir = _project_dir_from_server_script(root_dir, server_script)
        if project_dir == root_dir:
            continue

        relative_parts = project_dir.relative_to(root_dir).parts
        folder_hint = "_".join(relative_parts)
        server_id = _normalize_server_id(folder_hint)
        display_name = _display_name_from_folder(project_dir.name)

        # Ensure IDs are unique even if folders normalize to the same value.
        dedupe_counter = 2
        unique_server_id = server_id
        while unique_server_id in servers:
            unique_server_id = f"{server_id}_{dedupe_counter}"
            dedupe_counter += 1

        servers[unique_server_id] = MCPServer(
            server_id=unique_server_id,
            display_name=display_name,
            project_dir=project_dir,
            server_script=server_script,
            working_dir=server_script.parent,
            config_filename=_suggest_config_filename(unique_server_id, display_name),
            env_template_path=_find_nearest_env_template(server_script, project_dir),
        )

    return dict(sorted(servers.items(), key=lambda item: item[1].display_name.lower()))


def discover_servers_list(root_dir: Path) -> List[MCPServer]:
    return list(discover_servers(root_dir).values())
