from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from mcp_manager.mcp_runner import MCPRunner


MESSAGE_COOKIE_KEY = "mcp_manager_message"


def create_app(root_dir: Path) -> FastAPI:
    root_dir = root_dir.resolve()

    app = FastAPI(title="MCP Server Control Panel", version="1.0.0")
    templates = Jinja2Templates(directory=str(root_dir / "ui" / "templates"))
    runner = MCPRunner(root_dir)

    app.state.runner = runner

    app.mount("/static", StaticFiles(directory=str(root_dir / "ui" / "static")), name="static")

    @app.on_event("startup")
    async def on_startup() -> None:
        runner.refresh_servers()

    @app.on_event("shutdown")
    async def on_shutdown() -> None:
        runner.shutdown()

    @app.get("/")
    async def dashboard(request: Request) -> object:
        # Refresh each load so newly added MCP folders appear without restart.
        runner.refresh_servers()
        rows = runner.get_dashboard_rows()
        config_map = {
            row["server_id"]: (runner.get_server_config(row["server_id"]) or {"fields": []})["fields"]
            for row in rows
        }

        message = request.cookies.get(MESSAGE_COOKIE_KEY)
        response = templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "servers": rows,
                "config_map": config_map,
                "message": message,
            },
        )
        if message:
            response.delete_cookie(MESSAGE_COOKIE_KEY)
        return response

    @app.get("/config/{server_id}")
    async def config_page(request: Request, server_id: str) -> object:
        payload = runner.get_server_config(server_id)
        if not payload:
            return RedirectResponse("/", status_code=303)

        return templates.TemplateResponse(
            "config.html",
            {
                "request": request,
                "payload": payload,
            },
        )

    @app.post("/config/{server_id}")
    async def save_config(request: Request, server_id: str) -> object:
        form_data = await request.form()
        values = {k: str(v) for k, v in form_data.items()}
        success, message = runner.save_server_config(server_id, values)

        target = f"/config/{server_id}" if success else "/"
        response = RedirectResponse(target, status_code=303)
        response.set_cookie(MESSAGE_COOKIE_KEY, message, max_age=8, httponly=True)
        return response

    @app.post("/dashboard/config/{server_id}")
    async def save_dashboard_config(request: Request, server_id: str) -> object:
        form_data = await request.form()
        values = {k: str(v) for k, v in form_data.items()}
        _, message = runner.save_server_config(server_id, values)
        response = RedirectResponse("/", status_code=303)
        response.set_cookie(MESSAGE_COOKIE_KEY, message, max_age=8, httponly=True)
        return response

    @app.post("/servers/{server_id}/start")
    async def start_server(server_id: str) -> object:
        _, message = runner.start_server(server_id)
        response = RedirectResponse("/", status_code=303)
        response.set_cookie(MESSAGE_COOKIE_KEY, message, max_age=8, httponly=True)
        return response

    @app.post("/servers/{server_id}/stop")
    async def stop_server(server_id: str) -> object:
        _, message = runner.stop_server(server_id)
        response = RedirectResponse("/", status_code=303)
        response.set_cookie(MESSAGE_COOKIE_KEY, message, max_age=8, httponly=True)
        return response

    @app.post("/servers/{server_id}/restart")
    async def restart_server(server_id: str) -> object:
        _, message = runner.restart_server(server_id)
        response = RedirectResponse("/", status_code=303)
        response.set_cookie(MESSAGE_COOKIE_KEY, message, max_age=8, httponly=True)
        return response

    @app.get("/api/servers")
    async def api_servers() -> dict:
        runner.refresh_servers()
        return {"servers": runner.get_dashboard_rows()}

    @app.get("/api/servers/{server_id}/log")
    async def api_server_log(server_id: str, lines: int = 80) -> dict:
        log_text = runner.get_server_log(server_id, last_lines=min(lines, 500))
        return {"server_id": server_id, "log": log_text}

    return app
