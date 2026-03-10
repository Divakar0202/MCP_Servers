"""
Project-related tools for Jira MCP Server
"""
from typing import Any, Dict
from jira_client import JiraClient
from utils import build_error_response
import logging


logger = logging.getLogger("jira_mcp_server.project_tools")


def list_projects(client: JiraClient) -> Dict[str, Any]:
    """
    Get all Jira projects accessible to the authenticated user
    
    Args:
        client: Authenticated Jira client
        
    Returns:
        List of projects or error response
    """
    try:
        logger.info("Fetching all projects")
        projects_data = client.get_projects()
        
        projects = []
        for project in projects_data:
            projects.append({
                "id": project.get("id"),
                "key": project.get("key"),
                "name": project.get("name"),
                "description": project.get("description"),
                "project_type": project.get("projectTypeKey"),
                "lead": {
                    "display_name": project.get("lead", {}).get("displayName"),
                    "account_id": project.get("lead", {}).get("accountId")
                } if project.get("lead") else None,
                "avatar_url": project.get("avatarUrls", {}).get("48x48"),
                "url": project.get("self")
            })
        
        return {
            "total": len(projects),
            "projects": projects
        }
        
    except Exception as e:
        logger.error(f"Error fetching projects: {str(e)}")
        return build_error_response(e, "Failed to fetch projects")
