"""
Comment-related tools for Jira MCP Server
"""
from typing import Any, Dict
from jira_client import JiraClient
from utils import format_comment, build_error_response
import logging


logger = logging.getLogger("jira_mcp_server.comment_tools")


def get_issue_comments(client: JiraClient, jira_key: str) -> Dict[str, Any]:
    """
    Get all comments for a Jira issue
    
    Args:
        client: Authenticated Jira client
        jira_key: Issue key (e.g., PROJ-123)
        
    Returns:
        List of comments or error response
    """
    try:
        logger.info(f"Fetching comments for issue: {jira_key}")
        comments_data = client.get_issue_comments(jira_key)
        
        comments = []
        for comment in comments_data.get("comments", []):
            formatted_comment = format_comment(comment)
            comments.append(formatted_comment)
        
        return {
            "jira_key": jira_key,
            "total": comments_data.get("total", 0),
            "comments": comments
        }
        
    except Exception as e:
        logger.error(f"Error fetching comments for {jira_key}: {str(e)}")
        return build_error_response(e, f"Failed to fetch comments for issue {jira_key}")
