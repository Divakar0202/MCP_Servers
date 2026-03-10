from __future__ import annotations

import os
from pathlib import Path

from ui.app import create_app


ROOT_DIR = Path(__file__).resolve().parent
app = create_app(ROOT_DIR)


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("MCP_MANAGER_HOST", "127.0.0.1")
    port = int(os.getenv("MCP_MANAGER_PORT", "8000"))
    uvicorn.run("main:app", host=host, port=port, reload=False)
