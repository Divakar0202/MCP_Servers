"""
Pull Request-related tools for the Bitbucket MCP Server.
"""
from bitbucket_client import BitbucketClient
from utils import format_success_response, format_error_response, safe_get
import logging

logger = logging.getLogger(__name__)


class PullRequestTools:
    """Tools for pull request operations."""
    
    def __init__(self, client: BitbucketClient):
        """
        Initialize pull request tools.
        
        Args:
            client: Bitbucket API client
        """
        self.client = client
    
    def list_pull_requests(
        self, 
        repository_slug: str,
        state: str = "OPEN",
        limit: int = 50
    ) -> str:
        """
        List pull requests in a repository.
        
        Args:
            repository_slug: Repository slug/identifier
            state: PR state (OPEN, MERGED, DECLINED, SUPERSEDED)
            limit: Maximum number of PRs to return
            
        Returns:
            JSON string with pull request list
        """
        try:
            endpoint = f"repositories/{self.client.workspace}/{repository_slug}/pullrequests"
            params = {
                "pagelen": min(limit, 100),
                "state": state
            }
            
            response = self.client.get(endpoint, params)
            pull_requests = []
            
            for pr in response.get("values", []):
                pull_requests.append({
                    "id": pr.get("id"),
                    "title": pr.get("title"),
                    "description": pr.get("description"),
                    "state": pr.get("state"),
                    "author": {
                        "username": safe_get(pr, "author", "username"),
                        "display_name": safe_get(pr, "author", "display_name")
                    },
                    "source": {
                        "branch": safe_get(pr, "source", "branch", "name"),
                        "commit": safe_get(pr, "source", "commit", "hash")
                    },
                    "destination": {
                        "branch": safe_get(pr, "destination", "branch", "name"),
                        "commit": safe_get(pr, "destination", "commit", "hash")
                    },
                    "created_on": pr.get("created_on"),
                    "updated_on": pr.get("updated_on"),
                    "comment_count": pr.get("comment_count", 0),
                    "task_count": pr.get("task_count", 0)
                })
            
            result = {
                "repository": repository_slug,
                "state": state,
                "total_pull_requests": len(pull_requests),
                "pull_requests": pull_requests
            }
            
            return format_success_response(result)
        
        except Exception as e:
            logger.error(f"Error listing pull requests: {e}")
            return format_error_response(str(e), "PullRequestListError")
    
    def get_pull_request_details(
        self, 
        repository_slug: str,
        pull_request_id: int
    ) -> str:
        """
        Get detailed information about a specific pull request.
        
        Args:
            repository_slug: Repository slug/identifier
            pull_request_id: Pull request ID
            
        Returns:
            JSON string with pull request details
        """
        try:
            endpoint = f"repositories/{self.client.workspace}/{repository_slug}/pullrequests/{pull_request_id}"
            pr = self.client.get(endpoint)
            
            # Get commits in PR
            commits_endpoint = f"{endpoint}/commits"
            try:
                commits_response = self.client.get(commits_endpoint, {"pagelen": 50})
                commits = [
                    {
                        "hash": commit.get("hash"),
                        "message": commit.get("message")
                    }
                    for commit in commits_response.get("values", [])
                ]
            except:
                commits = []
            
            # Get reviewers
            reviewers = []
            for reviewer in pr.get("reviewers", []):
                reviewers.append({
                    "username": reviewer.get("username"),
                    "display_name": reviewer.get("display_name")
                })
            
            # Get participants
            participants = []
            for participant in pr.get("participants", []):
                participants.append({
                    "username": safe_get(participant, "user", "username"),
                    "display_name": safe_get(participant, "user", "display_name"),
                    "role": participant.get("role"),
                    "approved": participant.get("approved", False)
                })
            
            result = {
                "repository": repository_slug,
                "id": pr.get("id"),
                "title": pr.get("title"),
                "description": pr.get("description"),
                "state": pr.get("state"),
                "author": {
                    "username": safe_get(pr, "author", "username"),
                    "display_name": safe_get(pr, "author", "display_name")
                },
                "source": {
                    "branch": safe_get(pr, "source", "branch", "name"),
                    "commit": safe_get(pr, "source", "commit", "hash"),
                    "repository": safe_get(pr, "source", "repository", "full_name")
                },
                "destination": {
                    "branch": safe_get(pr, "destination", "branch", "name"),
                    "commit": safe_get(pr, "destination", "commit", "hash")
                },
                "merge_commit": safe_get(pr, "merge_commit", "hash"),
                "close_source_branch": pr.get("close_source_branch", False),
                "created_on": pr.get("created_on"),
                "updated_on": pr.get("updated_on"),
                "comment_count": pr.get("comment_count", 0),
                "task_count": pr.get("task_count", 0),
                "reviewers": reviewers,
                "participants": participants,
                "commits": commits,
                "total_commits": len(commits)
            }
            
            return format_success_response(result)
        
        except Exception as e:
            logger.error(f"Error getting pull request details: {e}")
            return format_error_response(str(e), "PullRequestDetailsError")
    
    def get_pull_request_comments(
        self, 
        repository_slug: str,
        pull_request_id: int
    ) -> str:
        """
        Get comments for a specific pull request.
        
        Args:
            repository_slug: Repository slug/identifier
            pull_request_id: Pull request ID
            
        Returns:
            JSON string with pull request comments
        """
        try:
            endpoint = f"repositories/{self.client.workspace}/{repository_slug}/pullrequests/{pull_request_id}/comments"
            params = {"pagelen": 100}
            
            response = self.client.get(endpoint, params)
            comments = []
            
            for comment in response.get("values", []):
                comments.append({
                    "id": comment.get("id"),
                    "content": safe_get(comment, "content", "raw"),
                    "user": {
                        "username": safe_get(comment, "user", "username"),
                        "display_name": safe_get(comment, "user", "display_name")
                    },
                    "created_on": comment.get("created_on"),
                    "updated_on": comment.get("updated_on"),
                    "inline": {
                        "path": safe_get(comment, "inline", "path"),
                        "from_line": safe_get(comment, "inline", "from"),
                        "to_line": safe_get(comment, "inline", "to")
                    } if comment.get("inline") else None,
                    "parent_id": safe_get(comment, "parent", "id")
                })
            
            result = {
                "repository": repository_slug,
                "pull_request_id": pull_request_id,
                "total_comments": len(comments),
                "comments": comments
            }
            
            return format_success_response(result)
        
        except Exception as e:
            logger.error(f"Error getting pull request comments: {e}")
            return format_error_response(str(e), "PullRequestCommentsError")
