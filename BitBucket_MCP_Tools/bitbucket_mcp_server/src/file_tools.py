"""
File-related tools for the Bitbucket MCP Server.
"""
from typing import Optional
from bitbucket_client import BitbucketClient
from utils import format_success_response, format_error_response, truncate_content, safe_get
import logging

logger = logging.getLogger(__name__)


class FileTools:
    """Tools for file operations."""
    
    def __init__(self, client: BitbucketClient):
        """
        Initialize file tools.
        
        Args:
            client: Bitbucket API client
        """
        self.client = client
    
    def list_repository_files(
        self, 
        repository_slug: str, 
        branch: str = "main",
        directory_path: str = ""
    ) -> str:
        """
        List files and directories in a repository path.
        
        Args:
            repository_slug: Repository slug/identifier
            branch: Branch name (default: main)
            directory_path: Path to directory (default: root)
            
        Returns:
            JSON string with file/directory list
        """
        try:
            # Clean directory path
            path = directory_path.strip("/")
            endpoint = f"repositories/{self.client.workspace}/{repository_slug}/src/{branch}/{path}"
            
            response = self.client.get(endpoint)
            
            files = []
            directories = []
            
            for item in response.get("values", []):
                item_type = item.get("type")
                item_data = {
                    "path": item.get("path"),
                    "type": item_type,
                    "size": item.get("size"),
                    "commit": {
                        "hash": safe_get(item, "commit", "hash"),
                        "date": safe_get(item, "commit", "date")
                    }
                }
                
                if item_type == "commit_file":
                    files.append(item_data)
                elif item_type == "commit_directory":
                    directories.append(item_data)
            
            result = {
                "repository": repository_slug,
                "branch": branch,
                "path": path or "/",
                "total_files": len(files),
                "total_directories": len(directories),
                "files": files,
                "directories": directories
            }
            
            return format_success_response(result)
        
        except Exception as e:
            logger.error(f"Error listing repository files: {e}")
            return format_error_response(str(e), "FileListError")
    
    def read_file_content(
        self, 
        repository_slug: str, 
        file_path: str,
        branch: str = "main"
    ) -> str:
        """
        Read the content of a file from the repository.
        
        Args:
            repository_slug: Repository slug/identifier
            file_path: Path to the file
            branch: Branch name (default: main)
            
        Returns:
            JSON string with file content
        """
        try:
            # Clean file path
            path = file_path.strip("/")
            endpoint = f"repositories/{self.client.workspace}/{repository_slug}/src/{branch}/{path}"
            
            # Get raw file content
            content = self.client.get_raw_content(f"{self.client.base_url}/{endpoint}")
            
            # Truncate if too large
            original_size = len(content.encode('utf-8'))
            content, was_truncated = truncate_content(content)
            
            result = {
                "repository": repository_slug,
                "branch": branch,
                "file_path": path,
                "content": content,
                "size_bytes": original_size,
                "truncated": was_truncated
            }
            
            if was_truncated:
                result["warning"] = "File content was truncated to 1MB"
            
            return format_success_response(result)
        
        except Exception as e:
            logger.error(f"Error reading file content: {e}")
            return format_error_response(str(e), "FileReadError")
    
    def get_repository_readme(
        self, 
        repository_slug: str,
        branch: Optional[str] = None
    ) -> str:
        """
        Get the README file from a repository.
        
        Args:
            repository_slug: Repository slug/identifier
            branch: Branch name (default: repository main branch)
            
        Returns:
            JSON string with README content
        """
        try:
            # If branch not specified, get repository details to find main branch
            if branch is None:
                repo_endpoint = f"repositories/{self.client.workspace}/{repository_slug}"
                repo = self.client.get(repo_endpoint)
                branch = safe_get(repo, "mainbranch", "name", default="main")
            
            # Try common README filenames
            readme_names = ["README.md", "README.rst", "README.txt", "README", "readme.md", "Readme.md"]
            
            for readme_name in readme_names:
                try:
                    endpoint = f"repositories/{self.client.workspace}/{repository_slug}/src/{branch}/{readme_name}"
                    content = self.client.get_raw_content(f"{self.client.base_url}/{endpoint}")
                    
                    # Found README
                    content, was_truncated = truncate_content(content)
                    
                    result = {
                        "repository": repository_slug,
                        "branch": branch,
                        "readme_file": readme_name,
                        "content": content,
                        "truncated": was_truncated
                    }
                    
                    return format_success_response(result)
                
                except:
                    continue
            
            # No README found
            return format_error_response(
                f"No README file found in repository {repository_slug}",
                "READMENotFound"
            )
        
        except Exception as e:
            logger.error(f"Error getting repository README: {e}")
            return format_error_response(str(e), "READMEError")
