"""
Utility functions for the Bitbucket MCP Server.
"""
import json
from typing import Any, Dict, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def format_success_response(data: Any) -> str:
    """
    Format a successful response as JSON string.
    
    Args:
        data: The data to return
        
    Returns:
        JSON formatted string
    """
    try:
        return json.dumps(data, indent=2, default=str)
    except Exception as e:
        logger.error(f"Error formatting response: {e}")
        return json.dumps({"error": f"Error formatting response: {str(e)}"}, indent=2)


def format_error_response(error_message: str, error_type: str = "Error") -> str:
    """
    Format an error response as JSON string.
    
    Args:
        error_message: The error message
        error_type: The type of error
        
    Returns:
        JSON formatted error string
    """
    return json.dumps({
        "error": error_type,
        "message": error_message
    }, indent=2)


def validate_repository_slug(repo_slug: str) -> bool:
    """
    Validate repository slug format.
    
    Args:
        repo_slug: Repository slug to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not repo_slug or not isinstance(repo_slug, str):
        return False
    # Basic validation - repository slugs are typically lowercase with hyphens
    return len(repo_slug) > 0 and len(repo_slug) <= 255


def truncate_content(content: str, max_size_bytes: int = 1048576) -> tuple[str, bool]:
    """
    Truncate content if it exceeds maximum size.
    
    Args:
        content: Content to potentially truncate
        max_size_bytes: Maximum size in bytes (default 1MB)
        
    Returns:
        Tuple of (content, was_truncated)
    """
    content_bytes = content.encode('utf-8')
    if len(content_bytes) > max_size_bytes:
        # Truncate to max size
        truncated = content_bytes[:max_size_bytes].decode('utf-8', errors='ignore')
        return truncated, True
    return content, False


def parse_pagination_params(limit: Optional[int] = None, page: Optional[int] = None) -> Dict[str, int]:
    """
    Parse and validate pagination parameters.
    
    Args:
        limit: Number of items per page
        page: Page number
        
    Returns:
        Dictionary with validated pagination parameters
    """
    validated_limit = min(limit or 50, 100)  # Default 50, max 100
    validated_page = max(page or 1, 1)  # Default 1, min 1
    
    return {
        "pagelen": validated_limit,
        "page": validated_page
    }


def extract_error_from_response(response_text: str, status_code: int) -> str:
    """
    Extract meaningful error message from API response.
    
    Args:
        response_text: Response text from API
        status_code: HTTP status code
        
    Returns:
        Formatted error message
    """
    try:
        error_data = json.loads(response_text)
        if "error" in error_data:
            return error_data["error"].get("message", response_text)
        return response_text
    except:
        return f"HTTP {status_code}: {response_text}"


def safe_get(dictionary: Dict, *keys, default=None) -> Any:
    """
    Safely get nested dictionary values.
    
    Args:
        dictionary: Dictionary to search
        *keys: Keys to traverse
        default: Default value if key not found
        
    Returns:
        Value at nested key or default
    """
    result = dictionary
    for key in keys:
        if isinstance(result, dict):
            result = result.get(key)
            if result is None:
                return default
        else:
            return default
    return result if result is not None else default
