"""
Jira API Client for MCP Server
Handles authentication and HTTP requests to Jira REST API
"""
import os
import base64
import requests
from typing import Any, Dict, Optional
from dotenv import load_dotenv
import logging


class JiraClient:
    """
    Client for interacting with Jira REST API v3
    Provides read-only access to Jira resources
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize Jira client with credentials from config file
        
        Args:
            config_path: Path to configuration file (defaults to ../config/config.env)
        """
        self.logger = logging.getLogger("jira_mcp_server.client")
        
        # Load configuration
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "config",
                "config.env"
            )
        
        load_dotenv(config_path)
        
        self.base_url = os.getenv("JIRA_BASE_URL")
        self.email = os.getenv("JIRA_EMAIL")
        self.api_token = os.getenv("JIRA_API_TOKEN")
        
        if not all([self.base_url, self.email, self.api_token]):
            raise ValueError(
                "Missing required configuration. Please set JIRA_BASE_URL, "
                "JIRA_EMAIL, and JIRA_API_TOKEN in config.env"
            )
        
        # Remove trailing slash from base URL
        self.base_url = self.base_url.rstrip("/")
        
        # Setup authentication
        self.auth_string = f"{self.email}:{self.api_token}"
        self.auth_header = base64.b64encode(self.auth_string.encode()).decode()
        
        self.headers = {
            "Authorization": f"Basic {self.auth_header}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        self.logger.info(f"Jira client initialized for {self.base_url}")
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test connection to Jira API
        
        Returns:
            Dict with connection status
        """
        try:
            response = self.get("/rest/api/3/myself")
            return {
                "success": True,
                "user": response.get("displayName"),
                "email": response.get("emailAddress")
            }
        except Exception as e:
            self.logger.error(f"Connection test failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a GET request to Jira API
        
        Args:
            endpoint: API endpoint (e.g., /rest/api/3/issue/PROJ-123)
            params: Query parameters
            
        Returns:
            JSON response from Jira
            
        Raises:
            requests.HTTPError: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        
        self.logger.debug(f"GET {url} with params: {params}")
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"HTTP Error: {e.response.status_code} - {e.response.text}")
            raise
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request Error: {str(e)}")
            raise
    
    def get_raw(self, url: str) -> bytes:
        """
        Make a GET request and return raw bytes (for attachments)
        
        Args:
            url: Full URL to fetch
            
        Returns:
            Raw bytes content
            
        Raises:
            requests.HTTPError: If request fails
        """
        self.logger.debug(f"GET (raw) {url}")
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request Error: {str(e)}")
            raise
    
    def search_issues(
        self,
        jql: str,
        start_at: int = 0,
        max_results: int = 50,
        fields: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for issues using JQL
        
        Args:
            jql: JQL query string
            start_at: Starting index for pagination
            max_results: Maximum number of results to return
            fields: Comma-separated list of fields to return
            
        Returns:
            Search results from Jira
        """
        params = {
            "jql": jql,
            "startAt": start_at,
            "maxResults": max_results
        }
        
        if fields:
            params["fields"] = fields
        
        return self.get("/rest/api/3/search", params=params)
    
    def get_issue(self, issue_id_or_key: str, expand: Optional[str] = None) -> Dict[str, Any]:
        """
        Get issue details by ID or key
        
        Args:
            issue_id_or_key: Issue ID or key (e.g., PROJ-123)
            expand: Comma-separated list of fields to expand
            
        Returns:
            Issue data from Jira
        """
        params = {}
        if expand:
            params["expand"] = expand
        
        return self.get(f"/rest/api/3/issue/{issue_id_or_key}", params=params)
    
    def get_issue_comments(self, issue_id_or_key: str) -> Dict[str, Any]:
        """
        Get comments for an issue
        
        Args:
            issue_id_or_key: Issue ID or key
            
        Returns:
            Comments data from Jira
        """
        return self.get(f"/rest/api/3/issue/{issue_id_or_key}/comment")
    
    def get_issue_changelog(
        self,
        issue_id_or_key: str,
        start_at: int = 0,
        max_results: int = 100
    ) -> Dict[str, Any]:
        """
        Get changelog/history for an issue
        
        Args:
            issue_id_or_key: Issue ID or key
            start_at: Starting index for pagination
            max_results: Maximum number of results
            
        Returns:
            Changelog data from Jira
        """
        params = {
            "startAt": start_at,
            "maxResults": max_results
        }
        return self.get(f"/rest/api/3/issue/{issue_id_or_key}/changelog", params=params)
    
    def get_projects(self) -> list:
        """
        Get all projects accessible to the user
        
        Returns:
            List of project data from Jira
        """
        return self.get("/rest/api/3/project")
    
    def get_issue_types(self) -> list:
        """
        Get all issue types
        
        Returns:
            List of issue types from Jira
        """
        return self.get("/rest/api/3/issuetype")
    
    def get_user(self, account_id: str) -> Dict[str, Any]:
        """
        Get user details by account ID
        
        Args:
            account_id: Jira account ID
            
        Returns:
            User data from Jira
        """
        params = {"accountId": account_id}
        return self.get("/rest/api/3/user", params=params)
