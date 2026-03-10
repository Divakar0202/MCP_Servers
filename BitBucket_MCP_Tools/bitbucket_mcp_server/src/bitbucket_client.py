"""
Bitbucket API Client for read-only operations.
Handles authentication and API communication with Bitbucket REST API.
"""
import base64
import os
from typing import Any, Dict, Optional
import requests
from dotenv import load_dotenv
import logging
from utils import extract_error_from_response

logger = logging.getLogger(__name__)


class BitbucketClient:
    """
    Client for interacting with Bitbucket REST API.
    Strictly read-only operations.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize Bitbucket client with configuration.
        
        Args:
            config_path: Path to configuration file (default: ../config/config.env)
        """
        # Load configuration
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), 
                "config", 
                "config.env"
            )
        
        load_dotenv(config_path)
        
        self.base_url = os.getenv("BITBUCKET_BASE_URL", "https://api.bitbucket.org/2.0")
        self.workspace = os.getenv("BITBUCKET_WORKSPACE")
        self.username = os.getenv("BITBUCKET_USERNAME")
        self.app_password = os.getenv("BITBUCKET_APP_PASSWORD")
        
        # Validate configuration
        if not all([self.workspace, self.username, self.app_password]):
            raise ValueError(
                "Missing required configuration. Please set BITBUCKET_WORKSPACE, "
                "BITBUCKET_USERNAME, and BITBUCKET_APP_PASSWORD in config.env"
            )
        
        # Setup authentication
        self.auth_header = self._create_auth_header()
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": self.auth_header,
            "Accept": "application/json"
        })
        
        logger.info(f"Bitbucket client initialized for workspace: {self.workspace}")
    
    def _create_auth_header(self) -> str:
        """
        Create Basic Auth header using username and app password.
        
        Returns:
            Authorization header value
        """
        credentials = f"{self.username}:{self.app_password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Make HTTP request to Bitbucket API.
        
        Args:
            method: HTTP method (GET only for read-only server)
            endpoint: API endpoint
            params: Query parameters
            timeout: Request timeout in seconds
            
        Returns:
            Response data as dictionary
            
        Raises:
            Exception: If request fails
        """
        # Enforce read-only: Only allow GET requests
        if method.upper() != "GET":
            raise ValueError("Only GET requests are allowed in read-only mode")
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                timeout=timeout
            )
            
            # Handle rate limiting
            if response.status_code == 429:
                raise Exception("API rate limit exceeded. Please try again later.")
            
            # Handle authentication errors
            if response.status_code == 401:
                raise Exception("Authentication failed. Please check your credentials.")
            
            # Handle not found
            if response.status_code == 404:
                raise Exception("Resource not found.")
            
            # Handle other errors
            if response.status_code >= 400:
                error_msg = extract_error_from_response(response.text, response.status_code)
                raise Exception(f"API request failed: {error_msg}")
            
            return response.json()
        
        except requests.exceptions.Timeout:
            raise Exception(f"Request timeout after {timeout} seconds")
        except requests.exceptions.ConnectionError:
            raise Exception("Connection error. Please check your network.")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make GET request to Bitbucket API.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            Response data
        """
        return self._make_request("GET", endpoint, params)
    
    def get_paginated(
        self, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        max_pages: int = 10
    ) -> list[Dict[str, Any]]:
        """
        Get paginated results from Bitbucket API.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            max_pages: Maximum number of pages to fetch
            
        Returns:
            List of all items from paginated response
        """
        all_items = []
        current_page = 1
        params = params or {}
        
        while current_page <= max_pages:
            params['page'] = current_page
            response = self.get(endpoint, params)
            
            # Extract values from response
            values = response.get('values', [])
            if not values:
                break
            
            all_items.extend(values)
            
            # Check if there are more pages
            if 'next' not in response:
                break
            
            current_page += 1
        
        return all_items
    
    def get_raw_content(self, url: str) -> str:
        """
        Get raw content from a URL (for file content).
        
        Args:
            url: Full URL to fetch
            
        Returns:
            Raw content as string
        """
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            raise Exception(f"Failed to fetch raw content: {str(e)}")
    
    def validate_connection(self) -> bool:
        """
        Validate connection to Bitbucket API.
        
        Returns:
            True if connection is valid
        """
        try:
            # Try to get user info
            self.get("user")
            logger.info("Bitbucket API connection validated successfully")
            return True
        except Exception as e:
            logger.error(f"Bitbucket API connection validation failed: {e}")
            raise Exception(f"Failed to connect to Bitbucket API: {str(e)}")
