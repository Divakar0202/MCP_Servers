"""
Commit-related tools for the Bitbucket MCP Server.
"""
from typing import Optional
from bitbucket_client import BitbucketClient
from utils import format_success_response, format_error_response, safe_get
import logging

logger = logging.getLogger(__name__)


class CommitTools:
    """Tools for commit operations."""
    
    def __init__(self, client: BitbucketClient):
        """
        Initialize commit tools.
        
        Args:
            client: Bitbucket API client
        """
        self.client = client
    
    def list_commits(
        self, 
        repository_slug: str,
        branch_name: Optional[str] = None,
        limit: int = 50
    ) -> str:
        """
        List commits in a repository.
        
        Args:
            repository_slug: Repository slug/identifier
            branch_name: Branch name (optional, defaults to main branch)
            limit: Maximum number of commits to return
            
        Returns:
            JSON string with commit list
        """
        try:
            endpoint = f"repositories/{self.client.workspace}/{repository_slug}/commits"
            
            # Add branch to endpoint if specified
            if branch_name:
                endpoint = f"{endpoint}/{branch_name}"
            
            params = {"pagelen": min(limit, 100)}
            response = self.client.get(endpoint, params)
            
            commits = []
            for commit in response.get("values", []):
                commits.append({
                    "hash": commit.get("hash"),
                    "message": commit.get("message"),
                    "author": {
                        "raw": safe_get(commit, "author", "raw"),
                        "username": safe_get(commit, "author", "user", "username"),
                        "display_name": safe_get(commit, "author", "user", "display_name")
                    },
                    "date": commit.get("date"),
                    "parents": [
                        {"hash": parent.get("hash")}
                        for parent in commit.get("parents", [])
                    ]
                })
            
            result = {
                "repository": repository_slug,
                "branch": branch_name or "default",
                "total_commits": len(commits),
                "commits": commits
            }
            
            return format_success_response(result)
        
        except Exception as e:
            logger.error(f"Error listing commits: {e}")
            return format_error_response(str(e), "CommitListError")
    
    def get_commit_details(
        self, 
        repository_slug: str,
        commit_hash: str
    ) -> str:
        """
        Get detailed information about a specific commit.
        
        Args:
            repository_slug: Repository slug/identifier
            commit_hash: Commit hash/SHA
            
        Returns:
            JSON string with commit details
        """
        try:
            endpoint = f"repositories/{self.client.workspace}/{repository_slug}/commit/{commit_hash}"
            commit = self.client.get(endpoint)
            
            # Get diff stats
            diff_endpoint = f"repositories/{self.client.workspace}/{repository_slug}/diffstat/{commit_hash}"
            try:
                diff_response = self.client.get(diff_endpoint)
                files_changed = []
                
                for file_stat in diff_response.get("values", []):
                    files_changed.append({
                        "path": safe_get(file_stat, "new", "path") or safe_get(file_stat, "old", "path"),
                        "type": file_stat.get("type"),
                        "lines_added": file_stat.get("lines_added", 0),
                        "lines_removed": file_stat.get("lines_removed", 0),
                        "status": file_stat.get("status")
                    })
            except:
                files_changed = []
            
            result = {
                "repository": repository_slug,
                "hash": commit.get("hash"),
                "message": commit.get("message"),
                "author": {
                    "raw": safe_get(commit, "author", "raw"),
                    "username": safe_get(commit, "author", "user", "username"),
                    "display_name": safe_get(commit, "author", "user", "display_name")
                },
                "date": commit.get("date"),
                "parents": [
                    {"hash": parent.get("hash")}
                    for parent in commit.get("parents", [])
                ],
                "files_changed": files_changed,
                "total_files_changed": len(files_changed)
            }
            
            return format_success_response(result)
        
        except Exception as e:
            logger.error(f"Error getting commit details: {e}")
            return format_error_response(str(e), "CommitDetailsError")
