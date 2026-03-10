"""
Search-related tools for the Bitbucket MCP Server.
"""
from bitbucket_client import BitbucketClient
from utils import format_success_response, format_error_response, safe_get
import logging

logger = logging.getLogger(__name__)


class SearchTools:
    """Tools for search operations."""
    
    def __init__(self, client: BitbucketClient):
        """
        Initialize search tools.
        
        Args:
            client: Bitbucket API client
        """
        self.client = client
    
    def search_repository_files(
        self, 
        repository_slug: str,
        search_keyword: str,
        branch: str = "main"
    ) -> str:
        """
        Search for files in a repository matching a keyword.
        This performs a recursive file tree search.
        
        Args:
            repository_slug: Repository slug/identifier
            search_keyword: Keyword to search for in file paths
            branch: Branch name (default: main)
            
        Returns:
            JSON string with matching files
        """
        try:
            # Get all files recursively
            matching_files = []
            search_keyword_lower = search_keyword.lower()
            
            def search_directory(path: str = ""):
                """Recursively search directory tree."""
                try:
                    endpoint = f"repositories/{self.client.workspace}/{repository_slug}/src/{branch}/{path}"
                    response = self.client.get(endpoint)
                    
                    for item in response.get("values", []):
                        item_path = item.get("path", "")
                        item_type = item.get("type")
                        
                        # Check if filename matches search keyword
                        if search_keyword_lower in item_path.lower():
                            matching_files.append({
                                "path": item_path,
                                "type": item_type,
                                "size": item.get("size")
                            })
                        
                        # Recursively search subdirectories (limit depth)
                        if item_type == "commit_directory" and len(matching_files) < 100:
                            search_directory(item_path)
                
                except Exception as e:
                    logger.debug(f"Error searching directory {path}: {e}")
            
            # Start search from root
            search_directory()
            
            result = {
                "repository": repository_slug,
                "branch": branch,
                "search_keyword": search_keyword,
                "total_matches": len(matching_files),
                "matching_files": matching_files[:100]  # Limit results
            }
            
            if len(matching_files) >= 100:
                result["warning"] = "Results limited to 100 files"
            
            return format_success_response(result)
        
        except Exception as e:
            logger.error(f"Error searching repository files: {e}")
            return format_error_response(str(e), "FileSearchError")
