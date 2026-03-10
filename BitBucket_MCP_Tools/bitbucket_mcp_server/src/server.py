"""
Bitbucket MCP Server - Read-Only Access to Bitbucket Repositories
Main server implementation using MCP SDK.
"""
import asyncio
import logging
import os
from typing import Any

import uvicorn
from mcp import types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.server.sse import SseServerTransport
from mcp.server.stdio import stdio_server
from starlette.applications import Starlette
from starlette.responses import Response
from starlette.routing import Mount, Route

from bitbucket_client import BitbucketClient
from repository_tools import RepositoryTools
from file_tools import FileTools
from commit_tools import CommitTools
from branch_tools import BranchTools
from pull_request_tools import PullRequestTools
from search_tools import SearchTools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize MCP server
server = Server("bitbucket-readonly-server")

# Global client and tools instances
bitbucket_client: BitbucketClient = None
repo_tools: RepositoryTools = None
file_tools: FileTools = None
commit_tools: CommitTools = None
branch_tools: BranchTools = None
pr_tools: PullRequestTools = None
search_tools: SearchTools = None


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List all available tools.
    """
    return [
        # Repository tools
        types.Tool(
            name="list_repositories",
            description="List all repositories in the configured Bitbucket workspace",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of repositories to return (default: 50, max: 100)",
                        "default": 50
                    }
                }
            }
        ),
        types.Tool(
            name="get_repository_details",
            description="Get detailed information about a specific repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "repository_slug": {
                        "type": "string",
                        "description": "Repository slug/identifier"
                    }
                },
                "required": ["repository_slug"]
            }
        ),
        types.Tool(
            name="list_repository_contributors",
            description="List contributors to a repository with commit counts",
            inputSchema={
                "type": "object",
                "properties": {
                    "repository_slug": {
                        "type": "string",
                        "description": "Repository slug/identifier"
                    }
                },
                "required": ["repository_slug"]
            }
        ),
        types.Tool(
            name="get_repository_tags",
            description="List all tags in a repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "repository_slug": {
                        "type": "string",
                        "description": "Repository slug/identifier"
                    }
                },
                "required": ["repository_slug"]
            }
        ),
        
        # Branch tools
        types.Tool(
            name="list_branches",
            description="List all branches in a repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "repository_slug": {
                        "type": "string",
                        "description": "Repository slug/identifier"
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of branches to return (default: 100)",
                        "default": 100
                    }
                },
                "required": ["repository_slug"]
            }
        ),
        
        # Commit tools
        types.Tool(
            name="list_commits",
            description="List commits in a repository with optional branch filter",
            inputSchema={
                "type": "object",
                "properties": {
                    "repository_slug": {
                        "type": "string",
                        "description": "Repository slug/identifier"
                    },
                    "branch_name": {
                        "type": "string",
                        "description": "Branch name (optional, defaults to main branch)"
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of commits to return (default: 50)",
                        "default": 50
                    }
                },
                "required": ["repository_slug"]
            }
        ),
        types.Tool(
            name="get_commit_details",
            description="Get detailed information about a specific commit including changed files",
            inputSchema={
                "type": "object",
                "properties": {
                    "repository_slug": {
                        "type": "string",
                        "description": "Repository slug/identifier"
                    },
                    "commit_hash": {
                        "type": "string",
                        "description": "Commit hash/SHA"
                    }
                },
                "required": ["repository_slug", "commit_hash"]
            }
        ),
        
        # File tools
        types.Tool(
            name="list_repository_files",
            description="List files and directories in a repository path",
            inputSchema={
                "type": "object",
                "properties": {
                    "repository_slug": {
                        "type": "string",
                        "description": "Repository slug/identifier"
                    },
                    "branch": {
                        "type": "string",
                        "description": "Branch name (default: main)",
                        "default": "main"
                    },
                    "directory_path": {
                        "type": "string",
                        "description": "Path to directory (default: root)",
                        "default": ""
                    }
                },
                "required": ["repository_slug"]
            }
        ),
        types.Tool(
            name="read_file_content",
            description="Read the full source code content of a file from the repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "repository_slug": {
                        "type": "string",
                        "description": "Repository slug/identifier"
                    },
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file"
                    },
                    "branch": {
                        "type": "string",
                        "description": "Branch name (default: main)",
                        "default": "main"
                    }
                },
                "required": ["repository_slug", "file_path"]
            }
        ),
        types.Tool(
            name="get_repository_readme",
            description="Get the README file content from a repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "repository_slug": {
                        "type": "string",
                        "description": "Repository slug/identifier"
                    },
                    "branch": {
                        "type": "string",
                        "description": "Branch name (optional, defaults to repository main branch)"
                    }
                },
                "required": ["repository_slug"]
            }
        ),
        
        # Pull request tools
        types.Tool(
            name="list_pull_requests",
            description="List pull requests in a repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "repository_slug": {
                        "type": "string",
                        "description": "Repository slug/identifier"
                    },
                    "state": {
                        "type": "string",
                        "description": "PR state: OPEN, MERGED, DECLINED, SUPERSEDED (default: OPEN)",
                        "default": "OPEN",
                        "enum": ["OPEN", "MERGED", "DECLINED", "SUPERSEDED"]
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of PRs to return (default: 50)",
                        "default": 50
                    }
                },
                "required": ["repository_slug"]
            }
        ),
        types.Tool(
            name="get_pull_request_details",
            description="Get detailed information about a specific pull request including commits and reviewers",
            inputSchema={
                "type": "object",
                "properties": {
                    "repository_slug": {
                        "type": "string",
                        "description": "Repository slug/identifier"
                    },
                    "pull_request_id": {
                        "type": "number",
                        "description": "Pull request ID"
                    }
                },
                "required": ["repository_slug", "pull_request_id"]
            }
        ),
        types.Tool(
            name="get_pull_request_comments",
            description="Get all comments for a specific pull request",
            inputSchema={
                "type": "object",
                "properties": {
                    "repository_slug": {
                        "type": "string",
                        "description": "Repository slug/identifier"
                    },
                    "pull_request_id": {
                        "type": "number",
                        "description": "Pull request ID"
                    }
                },
                "required": ["repository_slug", "pull_request_id"]
            }
        ),
        
        # Search tools
        types.Tool(
            name="search_repository_files",
            description="Search for files in a repository matching a keyword in the file path",
            inputSchema={
                "type": "object",
                "properties": {
                    "repository_slug": {
                        "type": "string",
                        "description": "Repository slug/identifier"
                    },
                    "search_keyword": {
                        "type": "string",
                        "description": "Keyword to search for in file paths"
                    },
                    "branch": {
                        "type": "string",
                        "description": "Branch name (default: main)",
                        "default": "main"
                    }
                },
                "required": ["repository_slug", "search_keyword"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, 
    arguments: dict[str, Any]
) -> list[types.TextContent]:
    """
    Handle tool execution.
    """
    try:
        result = ""
        
        # Repository tools
        if name == "list_repositories":
            limit = arguments.get("limit", 50)
            result = repo_tools.list_repositories(limit)
        
        elif name == "get_repository_details":
            result = repo_tools.get_repository_details(arguments["repository_slug"])
        
        elif name == "list_repository_contributors":
            result = repo_tools.list_repository_contributors(arguments["repository_slug"])
        
        elif name == "get_repository_tags":
            result = repo_tools.get_repository_tags(arguments["repository_slug"])
        
        # Branch tools
        elif name == "list_branches":
            limit = arguments.get("limit", 100)
            result = branch_tools.list_branches(arguments["repository_slug"], limit)
        
        # Commit tools
        elif name == "list_commits":
            branch_name = arguments.get("branch_name")
            limit = arguments.get("limit", 50)
            result = commit_tools.list_commits(
                arguments["repository_slug"], 
                branch_name, 
                limit
            )
        
        elif name == "get_commit_details":
            result = commit_tools.get_commit_details(
                arguments["repository_slug"], 
                arguments["commit_hash"]
            )
        
        # File tools
        elif name == "list_repository_files":
            branch = arguments.get("branch", "main")
            directory_path = arguments.get("directory_path", "")
            result = file_tools.list_repository_files(
                arguments["repository_slug"], 
                branch, 
                directory_path
            )
        
        elif name == "read_file_content":
            branch = arguments.get("branch", "main")
            result = file_tools.read_file_content(
                arguments["repository_slug"], 
                arguments["file_path"], 
                branch
            )
        
        elif name == "get_repository_readme":
            branch = arguments.get("branch")
            result = file_tools.get_repository_readme(
                arguments["repository_slug"], 
                branch
            )
        
        # Pull request tools
        elif name == "list_pull_requests":
            state = arguments.get("state", "OPEN")
            limit = arguments.get("limit", 50)
            result = pr_tools.list_pull_requests(
                arguments["repository_slug"], 
                state, 
                limit
            )
        
        elif name == "get_pull_request_details":
            result = pr_tools.get_pull_request_details(
                arguments["repository_slug"], 
                arguments["pull_request_id"]
            )
        
        elif name == "get_pull_request_comments":
            result = pr_tools.get_pull_request_comments(
                arguments["repository_slug"], 
                arguments["pull_request_id"]
            )
        
        # Search tools
        elif name == "search_repository_files":
            branch = arguments.get("branch", "main")
            result = search_tools.search_repository_files(
                arguments["repository_slug"], 
                arguments["search_keyword"], 
                branch
            )
        
        else:
            result = f'{{"error": "Unknown tool: {name}"}}'
        
        return [types.TextContent(type="text", text=result)]
    
    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}")
        error_result = f'{{"error": "Tool execution failed", "message": "{str(e)}"}}'
        return [types.TextContent(type="text", text=error_result)]


def _init_options() -> InitializationOptions:
    return InitializationOptions(
        server_name="bitbucket-readonly-server",
        server_version="1.0.0",
        capabilities=server.get_capabilities(
            notification_options=NotificationOptions(),
            experimental_capabilities={},
        ),
    )


async def _run_sse(host: str, port: int) -> None:
    sse = SseServerTransport("/messages/")

    async def handle_sse(request):
        async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
            await server.run(streams[0], streams[1], _init_options())
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
    """Main entry point for the MCP server."""
    global bitbucket_client, repo_tools, file_tools, commit_tools, branch_tools, pr_tools, search_tools

    # Try to initialise the Bitbucket client.  If credentials are missing / wrong
    # we log a warning but still start the SSE listener so the process stays alive
    # and the user can fix config via the control panel without restarting.
    try:
        logger.info("Initializing Bitbucket MCP Server...")
        bitbucket_client = BitbucketClient()

        logger.info("Validating Bitbucket API connection...")
        bitbucket_client.validate_connection()

        repo_tools = RepositoryTools(bitbucket_client)
        file_tools = FileTools(bitbucket_client)
        commit_tools = CommitTools(bitbucket_client)
        branch_tools = BranchTools(bitbucket_client)
        pr_tools = PullRequestTools(bitbucket_client)
        search_tools = SearchTools(bitbucket_client)

        logger.info("Bitbucket MCP Server initialized successfully")
        logger.info(f"Workspace: {bitbucket_client.workspace}")
    except Exception as e:
        logger.warning(
            f"Could not initialise Bitbucket client: {e} "
            "— server starting without credentials; configure via the control panel."
        )
        bitbucket_client = None

    transport = os.getenv("MCP_TRANSPORT", "stdio").strip().lower()
    host = os.getenv("MCP_HOST", "127.0.0.1")
    port = int(os.getenv("MCP_PORT", "8612"))

    try:
        if transport == "sse":
            logger.info(f"Starting MCP server on SSE http://{host}:{port}/sse")
            await _run_sse(host, port)
        else:
            logger.info("Starting MCP server on stdio")
            async with stdio_server() as (read_stream, write_stream):
                await server.run(read_stream, write_stream, _init_options())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
