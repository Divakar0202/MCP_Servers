"""
Attachment-related tools for Jira MCP Server
"""
from typing import Any, Dict
from jira_client import JiraClient
from utils import format_attachment, build_error_response
import logging


logger = logging.getLogger("jira_mcp_server.attachment_tools")


def get_issue_attachments(client: JiraClient, jira_key: str) -> Dict[str, Any]:
    """
    Get all attachments for a Jira issue
    
    Args:
        client: Authenticated Jira client
        jira_key: Issue key (e.g., PROJ-123)
        
    Returns:
        List of attachments with metadata or error response
    """
    try:
        logger.info(f"Fetching attachments for issue: {jira_key}")
        issue_data = client.get_issue(jira_key)
        
        fields = issue_data.get("fields", {})
        attachments_data = fields.get("attachment", [])
        
        attachments = []
        for attachment in attachments_data:
            formatted_attachment = format_attachment(attachment)
            
            # Determine if it's an image
            mime_type = formatted_attachment.get("mime_type", "")
            formatted_attachment["is_image"] = mime_type.startswith("image/")
            
            attachments.append(formatted_attachment)
        
        return {
            "jira_key": jira_key,
            "total": len(attachments),
            "attachments": attachments
        }
        
    except Exception as e:
        logger.error(f"Error fetching attachments for {jira_key}: {str(e)}")
        return build_error_response(e, f"Failed to fetch attachments for issue {jira_key}")


def download_attachment(client: JiraClient, attachment_url: str) -> Dict[str, Any]:
    """
    Download attachment and return metadata
    Note: This returns metadata about the attachment, not the actual file content
    The AI agent can use the content_url to download the file if needed
    
    Args:
        client: Authenticated Jira client
        attachment_url: URL of the attachment to download
        
    Returns:
        Attachment metadata or error response
    """
    try:
        logger.info(f"Processing attachment: {attachment_url}")
        
        # For read-only access, we return the URL and metadata
        # The actual download would be handled by the client if needed
        return {
            "content_url": attachment_url,
            "message": "Use the content_url to download the attachment",
            "instructions": "Make a GET request to content_url with Jira authentication to download the file"
        }
        
    except Exception as e:
        logger.error(f"Error processing attachment {attachment_url}: {str(e)}")
        return build_error_response(e, f"Failed to process attachment {attachment_url}")
