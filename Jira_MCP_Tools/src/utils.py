"""
Utility functions for the Jira MCP Server
"""
import logging
from typing import Any, Dict, Optional
from datetime import datetime


def setup_logging(level: str = "INFO") -> logging.Logger:
    """
    Setup logging configuration for the MCP server
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        
    Returns:
        Configured logger instance
    """
    logging.basicConfig(
        level=getattr(logging, level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger("jira_mcp_server")


def format_user(user_data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Format Jira user data into a consistent structure
    
    Args:
        user_data: Raw user data from Jira API
        
    Returns:
        Formatted user dictionary or None
    """
    if not user_data:
        return None
    
    return {
        "account_id": user_data.get("accountId"),
        "display_name": user_data.get("displayName"),
        "email": user_data.get("emailAddress"),
        "active": user_data.get("active"),
        "avatar_url": user_data.get("avatarUrls", {}).get("48x48")
    }


def format_date(date_string: Optional[str]) -> Optional[str]:
    """
    Format ISO date string to a readable format
    
    Args:
        date_string: ISO format date string
        
    Returns:
        Formatted date string or None
    """
    if not date_string:
        return None
    
    try:
        dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S UTC')
    except Exception:
        return date_string


def format_issue(issue_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format Jira issue data into a consistent structure
    
    Args:
        issue_data: Raw issue data from Jira API
        
    Returns:
        Formatted issue dictionary
    """
    fields = issue_data.get("fields", {})
    
    return {
        "key": issue_data.get("key"),
        "id": issue_data.get("id"),
        "summary": fields.get("summary"),
        "description": fields.get("description"),
        "status": fields.get("status", {}).get("name"),
        "status_category": fields.get("status", {}).get("statusCategory", {}).get("name"),
        "issue_type": fields.get("issuetype", {}).get("name"),
        "priority": fields.get("priority", {}).get("name") if fields.get("priority") else None,
        "assignee": format_user(fields.get("assignee")),
        "reporter": format_user(fields.get("reporter")),
        "created": format_date(fields.get("created")),
        "updated": format_date(fields.get("updated")),
        "resolution_date": format_date(fields.get("resolutiondate")),
        "labels": fields.get("labels", []),
        "components": [c.get("name") for c in fields.get("components", [])],
        "project": {
            "key": fields.get("project", {}).get("key"),
            "name": fields.get("project", {}).get("name")
        }
    }


def format_comment(comment_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format Jira comment data into a consistent structure
    
    Args:
        comment_data: Raw comment data from Jira API
        
    Returns:
        Formatted comment dictionary
    """
    return {
        "id": comment_data.get("id"),
        "author": format_user(comment_data.get("author")),
        "body": comment_data.get("body"),
        "created": format_date(comment_data.get("created")),
        "updated": format_date(comment_data.get("updated"))
    }


def format_attachment(attachment_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format Jira attachment data into a consistent structure
    
    Args:
        attachment_data: Raw attachment data from Jira API
        
    Returns:
        Formatted attachment dictionary
    """
    return {
        "id": attachment_data.get("id"),
        "filename": attachment_data.get("filename"),
        "size": attachment_data.get("size"),
        "mime_type": attachment_data.get("mimeType"),
        "content_url": attachment_data.get("content"),
        "thumbnail_url": attachment_data.get("thumbnail"),
        "author": format_user(attachment_data.get("author")),
        "created": format_date(attachment_data.get("created"))
    }


def build_error_response(error: Exception, context: str = "") -> Dict[str, Any]:
    """
    Build a standardized error response
    
    Args:
        error: The exception that occurred
        context: Additional context about where the error occurred
        
    Returns:
        Formatted error dictionary
    """
    return {
        "error": True,
        "error_type": type(error).__name__,
        "message": str(error),
        "context": context
    }


def truncate_text(text: Optional[str], max_length: int = 500) -> Optional[str]:
    """
    Truncate text to a maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text or None
    """
    if not text:
        return None
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length] + "... (truncated)"
