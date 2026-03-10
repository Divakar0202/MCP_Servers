"""
Jira MCP Server - Main Entry Point
Provides read-only tools for interacting with Jira via the MCP protocol
"""
import asyncio
import json
import os
from typing import Any

import uvicorn
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from starlette.applications import Starlette
from starlette.responses import Response
from starlette.routing import Mount, Route

from jira_client import JiraClient
from utils import setup_logging, build_error_response
import issue_tools
import comment_tools
import attachment_tools
import search_tools
import project_tools


# Initialize logging
logger = setup_logging("INFO")

# Initialize Jira client (will be set in main)
jira_client: JiraClient = None

# Create MCP server instance
server = Server("jira-readonly-server")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """
    List all available tools in the MCP server
    """
    return [
        Tool(
            name="list_projects",
            description="Get all Jira projects accessible to the user",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="search_issues",
            description="Search Jira issues using JQL (Jira Query Language)",
            inputSchema={
                "type": "object",
                "properties": {
                    "jql_query": {
                        "type": "string",
                        "description": "JQL query string (e.g., 'project = PROJ AND status = Open')"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 50, max: 100)",
                        "default": 50
                    },
                    "start_at": {
                        "type": "integer",
                        "description": "Starting index for pagination (default: 0)",
                        "default": 0
                    }
                },
                "required": ["jql_query"]
            }
        ),
        Tool(
            name="get_issue_by_key",
            description="Get complete details of a Jira issue by its key (e.g., PROJ-123)",
            inputSchema={
                "type": "object",
                "properties": {
                    "jira_key": {
                        "type": "string",
                        "description": "Jira issue key (e.g., PROJ-123)"
                    }
                },
                "required": ["jira_key"]
            }
        ),
        Tool(
            name="get_issue_by_id",
            description="Get complete details of a Jira issue by its ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "jira_id": {
                        "type": "string",
                        "description": "Jira issue ID"
                    }
                },
                "required": ["jira_id"]
            }
        ),
        Tool(
            name="get_issue_comments",
            description="Get all comments for a Jira issue",
            inputSchema={
                "type": "object",
                "properties": {
                    "jira_key": {
                        "type": "string",
                        "description": "Jira issue key (e.g., PROJ-123)"
                    }
                },
                "required": ["jira_key"]
            }
        ),
        Tool(
            name="get_issue_attachments",
            description="Get all attachments for a Jira issue including images and files",
            inputSchema={
                "type": "object",
                "properties": {
                    "jira_key": {
                        "type": "string",
                        "description": "Jira issue key (e.g., PROJ-123)"
                    }
                },
                "required": ["jira_key"]
            }
        ),
        Tool(
            name="download_attachment",
            description="Get attachment download URL and metadata",
            inputSchema={
                "type": "object",
                "properties": {
                    "attachment_url": {
                        "type": "string",
                        "description": "URL of the attachment to download"
                    }
                },
                "required": ["attachment_url"]
            }
        ),
        Tool(
            name="get_issue_types",
            description="Get all issue types available in Jira (Story, Bug, Task, Epic, etc.)",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_assignee_details",
            description="Get details about a Jira user (assignee) by account ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "account_id": {
                        "type": "string",
                        "description": "Jira account ID"
                    }
                },
                "required": ["account_id"]
            }
        ),
        Tool(
            name="get_reporter_details",
            description="Get details about a Jira user (reporter) by account ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "account_id": {
                        "type": "string",
                        "description": "Jira account ID"
                    }
                },
                "required": ["account_id"]
            }
        ),
        Tool(
            name="get_closed_stories",
            description="Get closed/done issues from a specific project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_key": {
                        "type": "string",
                        "description": "Project key (e.g., PROJ)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of stories to return (default: 50)",
                        "default": 50
                    }
                },
                "required": ["project_key"]
            }
        ),
        Tool(
            name="get_issue_history",
            description="Get change history for a Jira issue including status changes and field updates",
            inputSchema={
                "type": "object",
                "properties": {
                    "jira_key": {
                        "type": "string",
                        "description": "Jira issue key (e.g., PROJ-123)"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of history entries to return (default: 50)",
                        "default": 50
                    }
                },
                "required": ["jira_key"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """
    Handle tool execution requests
    """
    try:
        logger.info(f"Executing tool: {name} with arguments: {arguments}")
        
        # Route to appropriate tool handler
        result = None
        
        if name == "list_projects":
            result = project_tools.list_projects(jira_client)
            
        elif name == "search_issues":
            result = search_tools.search_issues(
                jira_client,
                arguments["jql_query"],
                arguments.get("max_results", 50),
                arguments.get("start_at", 0)
            )
            
        elif name == "get_issue_by_key":
            result = issue_tools.get_issue_by_key(
                jira_client,
                arguments["jira_key"]
            )
            
        elif name == "get_issue_by_id":
            result = issue_tools.get_issue_by_id(
                jira_client,
                arguments["jira_id"]
            )
            
        elif name == "get_issue_comments":
            result = comment_tools.get_issue_comments(
                jira_client,
                arguments["jira_key"]
            )
            
        elif name == "get_issue_attachments":
            result = attachment_tools.get_issue_attachments(
                jira_client,
                arguments["jira_key"]
            )
            
        elif name == "download_attachment":
            result = attachment_tools.download_attachment(
                jira_client,
                arguments["attachment_url"]
            )
            
        elif name == "get_issue_types":
            result = issue_tools.get_issue_types(jira_client)
            
        elif name == "get_assignee_details":
            result = issue_tools.get_assignee_details(
                jira_client,
                arguments["account_id"]
            )
            
        elif name == "get_reporter_details":
            result = issue_tools.get_reporter_details(
                jira_client,
                arguments["account_id"]
            )
            
        elif name == "get_closed_stories":
            result = search_tools.get_closed_stories(
                jira_client,
                arguments["project_key"],
                arguments.get("limit", 50)
            )
            
        elif name == "get_issue_history":
            result = issue_tools.get_issue_history(
                jira_client,
                arguments["jira_key"],
                arguments.get("max_results", 50)
            )
            
        else:
            result = build_error_response(
                ValueError(f"Unknown tool: {name}"),
                "Tool not found"
            )
        
        # Format response as JSON
        response_text = json.dumps(result, indent=2, ensure_ascii=False)
        
        return [TextContent(type="text", text=response_text)]
        
    except Exception as e:
        logger.error(f"Error executing tool {name}: {str(e)}")
        error_response = build_error_response(e, f"Error executing tool {name}")
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]


async def _run_sse(host: str, port: int) -> None:
    sse = SseServerTransport("/messages/")

    async def handle_sse(request):
        async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
            await server.run(
                streams[0],
                streams[1],
                server.create_initialization_options(),
            )
        return Response()

    starlette_app = Starlette(
        routes=[
            Route("/sse", endpoint=handle_sse, methods=["GET"]),
            Mount("/messages/", app=sse.handle_post_message),
        ]
    )

    config = uvicorn.Config(starlette_app, host=host, port=port, log_level="info")
    uv_server = uvicorn.Server(config)
    await uv_server.serve()


async def main():
    """
    Main entry point for the MCP server
    """
    global jira_client

    logger.info("Starting Jira MCP Server...")

    # Try to initialise the Jira client.  If credentials are missing / wrong
    # we log a warning but still start the SSE listener so the process stays
    # alive and the user can fix config via the control panel without restarting.
    try:
        jira_client = JiraClient()
        logger.info("Testing Jira connection...")
        connection_test = jira_client.test_connection()
        if connection_test.get("success"):
            logger.info(f"Connected to Jira as {connection_test.get('user')}")
        else:
            logger.warning(
                f"Jira connection test failed: {connection_test.get('error')} "
                "— server starting in degraded mode; tool calls will return errors."
            )
            jira_client = None
    except Exception as e:
        logger.warning(
            f"Could not initialise Jira client: {e} "
            "— server starting without credentials; configure via the control panel."
        )
        jira_client = None

    transport = os.getenv("MCP_TRANSPORT", "stdio").strip().lower()
    host = os.getenv("MCP_HOST", "127.0.0.1")
    port = int(os.getenv("MCP_PORT", "8611"))

    try:
        if transport == "sse":
            logger.info(f"Starting MCP server on SSE http://{host}:{port}/sse")
            await _run_sse(host, port)
        else:
            logger.info("Starting MCP server on stdio")
            async with stdio_server() as (read_stream, write_stream):
                await server.run(
                    read_stream,
                    write_stream,
                    server.create_initialization_options(),
                )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
