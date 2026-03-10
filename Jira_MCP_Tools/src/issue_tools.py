"""
Issue-related tools for Jira MCP Server
"""
from typing import Any, Dict
from jira_client import JiraClient
from utils import format_issue, build_error_response
import logging


logger = logging.getLogger("jira_mcp_server.issue_tools")


def get_issue_by_key(client: JiraClient, jira_key: str) -> Dict[str, Any]:
    """
    Get complete details of a Jira issue by its key
    
    Args:
        client: Authenticated Jira client
        jira_key: Issue key (e.g., PROJ-123)
        
    Returns:
        Formatted issue details or error response
    """
    try:
        logger.info(f"Fetching issue: {jira_key}")
        issue_data = client.get_issue(jira_key)
        formatted_issue = format_issue(issue_data)
        
        # Add additional metadata
        fields = issue_data.get("fields", {})
        formatted_issue["resolution"] = fields.get("resolution", {}).get("name") if fields.get("resolution") else None
        formatted_issue["story_points"] = fields.get("customfield_10016")  # Common story points field
        formatted_issue["sprint"] = fields.get("customfield_10020")  # Common sprint field
        formatted_issue["url"] = f"{client.base_url}/browse/{jira_key}"
        
        return formatted_issue
        
    except Exception as e:
        logger.error(f"Error fetching issue {jira_key}: {str(e)}")
        return build_error_response(e, f"Failed to fetch issue {jira_key}")


def get_issue_by_id(client: JiraClient, jira_id: str) -> Dict[str, Any]:
    """
    Get complete details of a Jira issue by its ID
    
    Args:
        client: Authenticated Jira client
        jira_id: Issue ID
        
    Returns:
        Formatted issue details or error response
    """
    try:
        logger.info(f"Fetching issue by ID: {jira_id}")
        issue_data = client.get_issue(jira_id)
        formatted_issue = format_issue(issue_data)
        formatted_issue["url"] = f"{client.base_url}/browse/{formatted_issue['key']}"
        
        return formatted_issue
        
    except Exception as e:
        logger.error(f"Error fetching issue by ID {jira_id}: {str(e)}")
        return build_error_response(e, f"Failed to fetch issue with ID {jira_id}")


def get_issue_history(client: JiraClient, jira_key: str, max_results: int = 50) -> Dict[str, Any]:
    """
    Get change history for a Jira issue
    
    Args:
        client: Authenticated Jira client
        jira_key: Issue key
        max_results: Maximum number of history entries to return
        
    Returns:
        Issue change history or error response
    """
    try:
        logger.info(f"Fetching history for issue: {jira_key}")
        changelog_data = client.get_issue_changelog(jira_key, max_results=max_results)
        
        histories = []
        for history in changelog_data.get("values", []):
            items = []
            for item in history.get("items", []):
                items.append({
                    "field": item.get("field"),
                    "field_type": item.get("fieldtype"),
                    "from": item.get("fromString"),
                    "to": item.get("toString")
                })
            
            histories.append({
                "id": history.get("id"),
                "author": {
                    "display_name": history.get("author", {}).get("displayName"),
                    "account_id": history.get("author", {}).get("accountId")
                },
                "created": history.get("created"),
                "changes": items
            })
        
        return {
            "jira_key": jira_key,
            "total": changelog_data.get("total", 0),
            "histories": histories
        }
        
    except Exception as e:
        logger.error(f"Error fetching history for {jira_key}: {str(e)}")
        return build_error_response(e, f"Failed to fetch history for issue {jira_key}")


def get_issue_types(client: JiraClient) -> Dict[str, Any]:
    """
    Get all issue types available in Jira
    
    Args:
        client: Authenticated Jira client
        
    Returns:
        List of issue types or error response
    """
    try:
        logger.info("Fetching issue types")
        issue_types_data = client.get_issue_types()
        
        issue_types = []
        for issue_type in issue_types_data:
            issue_types.append({
                "id": issue_type.get("id"),
                "name": issue_type.get("name"),
                "description": issue_type.get("description"),
                "subtask": issue_type.get("subtask", False),
                "icon_url": issue_type.get("iconUrl")
            })
        
        return {
            "total": len(issue_types),
            "issue_types": issue_types
        }
        
    except Exception as e:
        logger.error(f"Error fetching issue types: {str(e)}")
        return build_error_response(e, "Failed to fetch issue types")


def get_assignee_details(client: JiraClient, account_id: str) -> Dict[str, Any]:
    """
    Get details about a Jira user (assignee)
    
    Args:
        client: Authenticated Jira client
        account_id: Jira account ID
        
    Returns:
        User details or error response
    """
    try:
        logger.info(f"Fetching user details: {account_id}")
        user_data = client.get_user(account_id)
        
        return {
            "account_id": user_data.get("accountId"),
            "display_name": user_data.get("displayName"),
            "email": user_data.get("emailAddress"),
            "active": user_data.get("active"),
            "time_zone": user_data.get("timeZone"),
            "avatar_urls": user_data.get("avatarUrls")
        }
        
    except Exception as e:
        logger.error(f"Error fetching user {account_id}: {str(e)}")
        return build_error_response(e, f"Failed to fetch user with account ID {account_id}")


def get_reporter_details(client: JiraClient, account_id: str) -> Dict[str, Any]:
    """
    Get details about a Jira user (reporter)
    This is an alias for get_assignee_details
    
    Args:
        client: Authenticated Jira client
        account_id: Jira account ID
        
    Returns:
        User details or error response
    """
    return get_assignee_details(client, account_id)
