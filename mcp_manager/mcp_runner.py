from __future__ import annotations

from pathlib import Path
from threading import Lock
from typing import Dict, List, Optional, Tuple

from mcp_manager.config_manager import ConfigManager
from mcp_manager.process_manager import ProcessManager
from mcp_manager.server_registry import MCPServer, discover_servers


class MCPRunner:
    def __init__(self, root_dir: Path) -> None:
        self.root_dir = root_dir.resolve()
        self.config_manager = ConfigManager(self.root_dir / "configs")
        self.process_manager = ProcessManager()
        self._lock = Lock()
        self._servers: Dict[str, MCPServer] = {}

    def refresh_servers(self) -> Dict[str, MCPServer]:
        discovered = discover_servers(self.root_dir)
        with self._lock:
            self._servers = discovered
            for index, server in enumerate(self._servers.values(), start=1):
                self.config_manager.ensure_config_file(server)
                self._ensure_runtime_defaults(server, index)
        return discovered

    def get_servers(self) -> Dict[str, MCPServer]:
        with self._lock:
            if not self._servers:
                self._servers = discover_servers(self.root_dir)
            return dict(self._servers)

    def get_server(self, server_id: str) -> Optional[MCPServer]:
        return self.get_servers().get(server_id)

    def get_dashboard_rows(self) -> List[dict]:
        rows: List[dict] = []
        for server in self.get_servers().values():
            status = self.process_manager.status(server.server_id)
            cfg = self.config_manager.load_config(server)
            transport = cfg.get("MCP_TRANSPORT", "stdio")
            port = cfg.get("MCP_PORT", "")
            host = cfg.get("MCP_HOST", "")
            rows.append(
                {
                    "server_id": server.server_id,
                    "display_name": server.display_name,
                    "status": status,
                    "server_script": str(server.server_script),
                    "config_file": server.config_filename,
                    "uptime_seconds": self.process_manager.uptime_seconds(server.server_id),
                    "transport": transport,
                    "host": host,
                    "port": port,
                }
            )
        return rows

    def get_server_config(self, server_id: str) -> Optional[dict]:
        server = self.get_server(server_id)
        if not server:
            return None

        config = self.config_manager.load_config(server)
        ordered_keys = self.config_manager.list_config_keys(server)
        fields = []
        for key in ordered_keys:
            raw = config.get(key, "")
            sensitive = self.config_manager.is_sensitive_key(key)
            fields.append(
                {
                    "key": key,
                    "value": "" if sensitive else raw,
                    "masked": self.config_manager.mask_value(key, raw),
                    "sensitive": sensitive,
                }
            )

        return {
            "server": server,
            "fields": fields,
            "config_file": str(self.config_manager.config_path(server)),
        }

    def save_server_config(self, server_id: str, values: Dict[str, str]) -> Tuple[bool, str]:
        server = self.get_server(server_id)
        if not server:
            return False, "Server not found"

        self.config_manager.save_config(server, values)
        return True, "Configuration saved"

    def start_server(self, server_id: str) -> Tuple[bool, str]:
        server = self.get_server(server_id)
        if not server:
            return False, "Server not found"

        config = self.config_manager.load_config(server)
        started = self.process_manager.start(server, config)
        if not started:
            return False, "Server is already running"
        return True, "Server started"

    def stop_server(self, server_id: str) -> Tuple[bool, str]:
        stopped = self.process_manager.stop(server_id)
        if not stopped:
            return False, "Server is not running"
        return True, "Server stopped"

    def restart_server(self, server_id: str) -> Tuple[bool, str]:
        server = self.get_server(server_id)
        if not server:
            return False, "Server not found"

        config = self.config_manager.load_config(server)
        self.process_manager.restart(server, config)
        return True, "Server restarted"

    def shutdown(self) -> None:
        self.process_manager.stop_all()

    def get_server_log(self, server_id: str, last_lines: int = 80) -> str:
        return self.process_manager.get_log(server_id, last_lines)

    def _ensure_runtime_defaults(self, server: MCPServer, index: int) -> None:
        current = self.config_manager.load_config(server)
        updates: Dict[str, str] = {}

        if "MCP_TRANSPORT" not in current:
            updates["MCP_TRANSPORT"] = "sse"
        if "MCP_HOST" not in current:
            updates["MCP_HOST"] = "127.0.0.1"
        if "MCP_PORT" not in current:
            updates["MCP_PORT"] = str(8610 + index)

        if updates:
            self.config_manager.save_config(server, updates)
