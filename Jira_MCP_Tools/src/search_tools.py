"""
Search-related tools for Jira MCP Server
"""
from typing import Any, Dict, Optional
from jira_client import JiraClient
from utils import format_issue, build_error_response
import logging


logger = logging.getLogger("jira_mcp_server.search_tools")


def search_issues(
    client: JiraClient,
    jql_query: str,
    max_results: int = 50,
    start_at: int = 0
) -> Dict[str, Any]:
    """
    Search for Jira issues using JQL (Jira Query Language)
    
    Args:
        client: Authenticated Jira client
        jql_query: JQL query string
        max_results: Maximum number of results to return (default: 50)
        start_at: Starting index for pagination (default: 0)
        
    Returns:
        Search results with issues or error response
    """
    try:
        logger.info(f"Searching issues with JQL: {jql_query}")
        
        # Limit max_results to prevent excessive data
        max_results = min(max_results, 100)
        
        search_results = client.search_issues(
            jql=jql_query,
            start_at=start_at,
            max_results=max_results
        )
        
        issues = []
        for issue_data in search_results.get("issues", []):
            formatted_issue = format_issue(issue_data)
            formatted_issue["url"] = f"{client.base_url}/browse/{formatted_issue['key']}"
            issues.append(formatted_issue)
        
        return {
            "jql": jql_query,
            "total": search_results.get("total", 0),
            "start_at": search_results.get("startAt", 0),
            "max_results": search_results.get("maxResults", 0),
            "returned": len(issues),
            "issues": issues
        }
        
    except Exception as e:
        logger.error(f"Error searching issues: {str(e)}")
        return build_error_response(e, f"Failed to search issues with JQL: {jql_query}")


def get_closed_stories(
    client: JiraClient,
    project_key: str,
    limit: int = 50
) -> Dict[str, Any]:
    """
    Get closed/done stories from a specific project
    
    Args:
        client: Authenticated Jira client
        project_key: Project key (e.g., PROJ)
        limit: Maximum number of stories to return
        
    Returns:
        List of closed stories or error response
    """
    try:
        logger.info(f"Fetching closed stories for project: {project_key}")
        
        # Build JQL query for closed stories
        jql = f'project = {project_key} AND status = Done ORDER BY updated DESC'
        
        return search_issues(client, jql, max_results=limit)
        
    except Exception as e:
        logger.error(f"Error fetching closed stories for {project_key}: {str(e)}")
        return build_error_response(
            e,
            f"Failed to fetch closed stories for project {project_key}"
        )
