"""
Branch-related tools for the Bitbucket MCP Server.
"""
from bitbucket_client import BitbucketClient
from utils import format_success_response, format_error_response, safe_get
import logging

logger = logging.getLogger(__name__)


class BranchTools:
    """Tools for branch operations."""
    
    def __init__(self, client: BitbucketClient):
        """
        Initialize branch tools.
        
        Args:
            client: Bitbucket API client
        """
        self.client = client
    
    def list_branches(self, repository_slug: str, limit: int = 100) -> str:
        """
        List all branches in a repository.
        
        Args:
            repository_slug: Repository slug/identifier
            limit: Maximum number of branches to return
            
        Returns:
            JSON string with branch list
        """
        try:
            endpoint = f"repositories/{self.client.workspace}/{repository_slug}/refs/branches"
            params = {"pagelen": min(limit, 100)}
            
            response = self.client.get(endpoint, params)
            branches = []
            
            for branch in response.get("values", []):
                branches.append({
                    "name": branch.get("name"),
                    "type": branch.get("type"),
                    "target": {
                        "hash": safe_get(branch, "target", "hash"),
                        "date": safe_get(branch, "target", "date"),
                        "message": safe_get(branch, "target", "message"),
                        "author": safe_get(branch, "target", "author", "raw")
                    }
                })
            
            result = {
                "repository": repository_slug,
                "total_branches": len(branches),
                "branches": branches
            }
            
            return format_success_response(result)
        
        except Exception as e:
            logger.error(f"Error listing branches: {e}")
            return format_error_response(str(e), "BranchListError")
