from __future__ import annotations

import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from typing import Dict, Optional

from mcp_manager.server_registry import MCPServer


@dataclass
class ManagedProcess:
    server_id: str
    process: subprocess.Popen
    started_at: float


class ProcessManager:
    def __init__(self) -> None:
        self._processes: Dict[str, ManagedProcess] = {}
        self._lock = Lock()
        self._workspace_root = Path(__file__).resolve().parent.parent
        self._logs_dir = self._workspace_root / "logs"
        self._logs_dir.mkdir(exist_ok=True)
        self._log_handles: Dict[str, object] = {}  # open file handles keyed by server_id

    def _log_path(self, server_id: str) -> Path:
        return self._logs_dir / f"{server_id}.log"

    def start(self, server: MCPServer, config_env: Dict[str, str]) -> bool:
        with self._lock:
            if self._is_running_locked(server.server_id):
                return False

            env = dict(os.environ)
            env.update({k: v for k, v in config_env.items() if v is not None})

            # Open a log file (overwrite on each start so the latest run is visible)
            log_file = open(self._log_path(server.server_id), "w", encoding="utf-8")
            self._log_handles[server.server_id] = log_file

            python_cmd = self._resolve_python_executable()
            process = subprocess.Popen(
                [python_cmd, str(server.server_script)],
                cwd=str(server.working_dir),
                env=env,
                stdout=log_file,
                stderr=log_file,
                stdin=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
            )
            self._processes[server.server_id] = ManagedProcess(
                server_id=server.server_id,
                process=process,
                started_at=time.time(),
            )
            return True

    def stop(self, server_id: str, timeout_seconds: float = 8.0) -> bool:
        with self._lock:
            managed = self._processes.get(server_id)
            if not managed:
                return False

            process = managed.process
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=timeout_seconds)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=timeout_seconds)

            self._processes.pop(server_id, None)

            # Close the log file handle if open
            handle = self._log_handles.pop(server_id, None)
            if handle:
                try:
                    handle.close()
                except OSError:
                    pass

            return True

    def get_log(self, server_id: str, last_lines: int = 80) -> str:
        """Return the last *last_lines* lines of the server's log file."""
        path = self._log_path(server_id)
        if not path.exists():
            return "(no log file yet — start the server first)"
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                lines = fh.readlines()
            return "".join(lines[-last_lines:])
        except OSError as exc:
            return f"(could not read log: {exc})"

    def restart(self, server: MCPServer, config_env: Dict[str, str]) -> bool:
        self.stop(server.server_id)
        return self.start(server, config_env)

    def status(self, server_id: str) -> str:
        with self._lock:
            managed = self._processes.get(server_id)
            if not managed:
                return "stopped"

            rc = managed.process.poll()
            if rc is None:
                return "running"

            self._processes.pop(server_id, None)
            return f"exited ({rc})"

    def uptime_seconds(self, server_id: str) -> Optional[int]:
        with self._lock:
            managed = self._processes.get(server_id)
            if not managed or managed.process.poll() is not None:
                return None
            return int(time.time() - managed.started_at)

    def stop_all(self) -> None:
        with self._lock:
            server_ids = list(self._processes.keys())
        for server_id in server_ids:
            self.stop(server_id)

    def _is_running_locked(self, server_id: str) -> bool:
        managed = self._processes.get(server_id)
        return bool(managed and managed.process.poll() is None)

    def _resolve_python_executable(self) -> str:
        if os.name == "nt":
            venv_python = self._workspace_root / ".venv" / "Scripts" / "python.exe"
        else:
            venv_python = self._workspace_root / ".venv" / "bin" / "python"

        if venv_python.exists():
            return str(venv_python)
        return sys.executable
