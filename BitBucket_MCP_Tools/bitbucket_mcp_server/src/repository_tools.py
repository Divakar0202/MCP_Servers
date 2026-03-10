"""
Repository-related tools for the Bitbucket MCP Server.
"""
from typing import Dict, Any, Optional
from bitbucket_client import BitbucketClient
from utils import format_success_response, format_error_response, safe_get
import logging

logger = logging.getLogger(__name__)


class RepositoryTools:
    """Tools for repository operations."""
    
    def __init__(self, client: BitbucketClient):
        """
        Initialize repository tools.
        
        Args:
            client: Bitbucket API client
        """
        self.client = client
    
    def list_repositories(self, limit: int = 50) -> str:
        """
        List all repositories in the configured workspace.
        
        Args:
            limit: Maximum number of repositories to return
            
        Returns:
            JSON string with repository list
        """
        try:
            endpoint = f"repositories/{self.client.workspace}"
            params = {"pagelen": min(limit, 100)}
            
            response = self.client.get(endpoint, params)
            repositories = []
            
            for repo in response.get("values", []):
                repositories.append({
                    "slug": repo.get("slug"),
                    "name": repo.get("name"),
                    "description": repo.get("description"),
                    "is_private": repo.get("is_private"),
                    "language": repo.get("language"),
                    "size": repo.get("size"),
                    "created_on": repo.get("created_on"),
                    "updated_on": repo.get("updated_on"),
                    "full_name": repo.get("full_name")
                })
            
            result = {
                "workspace": self.client.workspace,
                "total_repositories": len(repositories),
                "repositories": repositories
            }
            
            return format_success_response(result)
        
        except Exception as e:
            logger.error(f"Error listing repositories: {e}")
            return format_error_response(str(e), "RepositoryListError")
    
    def get_repository_details(self, repository_slug: str) -> str:
        """
        Get detailed information about a specific repository.
        
        Args:
            repository_slug: Repository slug/identifier
            
        Returns:
            JSON string with repository details
        """
        try:
            endpoint = f"repositories/{self.client.workspace}/{repository_slug}"
            repo = self.client.get(endpoint)
            
            result = {
                "slug": repo.get("slug"),
                "name": repo.get("name"),
                "full_name": repo.get("full_name"),
                "description": repo.get("description"),
                "is_private": repo.get("is_private"),
                "project": {
                    "key": safe_get(repo, "project", "key"),
                    "name": safe_get(repo, "project", "name")
                },
                "language": repo.get("language"),
                "size": repo.get("size"),
                "created_on": repo.get("created_on"),
                "updated_on": repo.get("updated_on"),
                "has_issues": repo.get("has_issues"),
                "has_wiki": repo.get("has_wiki"),
                "fork_policy": repo.get("fork_policy"),
                "mainbranch": safe_get(repo, "mainbranch", "name"),
                "owner": {
                    "username": safe_get(repo, "owner", "username"),
                    "display_name": safe_get(repo, "owner", "display_name")
                },
                "links": {
                    "html": safe_get(repo, "links", "html", "href"),
                    "clone": [
                        {"name": link.get("name"), "href": link.get("href")}
                        for link in safe_get(repo, "links", "clone", default=[])
                    ]
                }
            }
            
            return format_success_response(result)
        
        except Exception as e:
            logger.error(f"Error getting repository details: {e}")
            return format_error_response(str(e), "RepositoryDetailsError")
    
    def list_repository_contributors(self, repository_slug: str) -> str:
        """
        List contributors to a repository.
        
        Args:
            repository_slug: Repository slug/identifier
            
        Returns:
            JSON string with contributors list
        """
        try:
            # Get commits to extract contributors
            endpoint = f"repositories/{self.client.workspace}/{repository_slug}/commits"
            params = {"pagelen": 100}
            
            commits = self.client.get_paginated(endpoint, params, max_pages=5)
            
            # Count contributions by author
            contributors_dict = {}
            for commit in commits:
                author = safe_get(commit, "author", "user", "username") or safe_get(commit, "author", "raw", default="Unknown")
                
                if author not in contributors_dict:
                    contributors_dict[author] = {
                        "username": author,
                        "display_name": safe_get(commit, "author", "user", "display_name", default=author),
                        "commit_count": 0
                    }
                contributors_dict[author]["commit_count"] += 1
            
            # Sort by commit count
            contributors = sorted(
                contributors_dict.values(), 
                key=lambda x: x["commit_count"], 
                reverse=True
            )
            
            result = {
                "repository": repository_slug,
                "total_contributors": len(contributors),
                "contributors": contributors
            }
            
            return format_success_response(result)
        
        except Exception as e:
            logger.error(f"Error listing contributors: {e}")
            return format_error_response(str(e), "ContributorsListError")
    
    def get_repository_tags(self, repository_slug: str) -> str:
        """
        List all tags in a repository.
        
        Args:
            repository_slug: Repository slug/identifier
            
        Returns:
            JSON string with tags list
        """
        try:
            endpoint = f"repositories/{self.client.workspace}/{repository_slug}/refs/tags"
            params = {"pagelen": 100}
            
            response = self.client.get(endpoint, params)
            tags = []
            
            for tag in response.get("values", []):
                tags.append({
                    "name": tag.get("name"),
                    "type": tag.get("type"),
                    "target": {
                        "hash": safe_get(tag, "target", "hash"),
                        "date": safe_get(tag, "target", "date"),
                        "message": safe_get(tag, "target", "message")
                    },
                    "date": safe_get(tag, "target", "date")
                })
            
            result = {
                "repository": repository_slug,
                "total_tags": len(tags),
                "tags": tags
            }
            
            return format_success_response(result)
        
        except Exception as e:
            logger.error(f"Error getting repository tags: {e}")
            return format_error_response(str(e), "TagsListError")
