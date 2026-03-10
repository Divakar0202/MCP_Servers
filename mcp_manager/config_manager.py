from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List

from mcp_manager.server_registry import MCPServer


SENSITIVE_TOKENS = {"password", "token", "secret", "key", "passphrase"}

DEFAULT_CONFIG_KEYS = {
    "jira.env": [
        "JIRA_BASE_URL",
        "JIRA_EMAIL",
        "JIRA_API_TOKEN",
    ],
    "bitbucket.env": [
        "BITBUCKET_BASE_URL",
        "BITBUCKET_WORKSPACE",
        "BITBUCKET_USERNAME",
        "BITBUCKET_APP_PASSWORD",
    ],
    "database.env": [
        "POSTGRES_HOST",
        "POSTGRES_PORT",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "DEFAULT_DATABASE",
    ],
}


class ConfigManager:
    def __init__(self, configs_dir: Path) -> None:
        self.configs_dir = configs_dir.resolve()
        self.configs_dir.mkdir(parents=True, exist_ok=True)

    def config_path(self, server: MCPServer) -> Path:
        return self.configs_dir / server.config_filename

    def ensure_config_file(self, server: MCPServer) -> Path:
        cfg_path = self.config_path(server)
        if cfg_path.exists():
            return cfg_path

        if server.env_template_path and server.env_template_path.exists():
            cfg_path.write_text(server.env_template_path.read_text(encoding="utf-8"), encoding="utf-8")
        else:
            lines = [f"{key}=" for key in self.list_config_keys(server)]
            cfg_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
        return cfg_path

    def load_config(self, server: MCPServer) -> Dict[str, str]:
        cfg_path = self.ensure_config_file(server)
        return self._parse_env_text(cfg_path.read_text(encoding="utf-8"))

    def save_config(self, server: MCPServer, values: Dict[str, str]) -> Path:
        cfg_path = self.ensure_config_file(server)
        existing = self.load_config(server)

        for key, value in values.items():
            if not key or key == "_csrf":
                continue
            # Do not clear existing secrets when a dashboard password field is left empty.
            if self.is_sensitive_key(key) and value == "":
                continue
            existing[key] = value

        ordered_keys = self._merge_ordered_keys(self.list_config_keys(server), existing.keys())
        lines = [f"{key}={existing.get(key, '')}" for key in ordered_keys]
        cfg_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return cfg_path

    def list_config_keys(self, server: MCPServer) -> List[str]:
        keys: List[str] = []

        if server.env_template_path and server.env_template_path.exists():
            parsed = self._parse_env_text(server.env_template_path.read_text(encoding="utf-8"))
            keys.extend(parsed.keys())

        cfg_path = self.config_path(server)
        if cfg_path.exists():
            parsed = self._parse_env_text(cfg_path.read_text(encoding="utf-8"))
            keys.extend(parsed.keys())

        keys.extend(DEFAULT_CONFIG_KEYS.get(server.config_filename, []))
        return self._merge_ordered_keys(keys)

    @staticmethod
    def is_sensitive_key(key: str) -> bool:
        lowered = key.lower()
        return any(token in lowered for token in SENSITIVE_TOKENS)

    @classmethod
    def mask_value(cls, key: str, value: str) -> str:
        if not value:
            return ""
        if not cls.is_sensitive_key(key):
            return value
        if len(value) <= 4:
            return "*" * len(value)
        return f"{'*' * (len(value) - 4)}{value[-4:]}"

    @staticmethod
    def _parse_env_text(content: str) -> Dict[str, str]:
        parsed: Dict[str, str] = {}
        for raw_line in content.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            if key:
                parsed[key] = value
        return parsed

    @staticmethod
    def _merge_ordered_keys(primary: Iterable[str], secondary: Iterable[str] = ()) -> List[str]:
        seen = set()
        merged: List[str] = []
        for key in list(primary) + list(secondary):
            clean = key.strip()
            if not clean or clean in seen:
                continue
            seen.add(clean)
            merged.append(clean)
        return merged
