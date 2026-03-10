"""
Test script to verify Jira MCP Server functionality
Run this after setting up your configuration to test the connection
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from jira_client import JiraClient
from utils import setup_logging
import issue_tools
import project_tools
import search_tools


def test_connection():
    """Test Jira connection"""
    print("\n" + "="*60)
    print("TESTING JIRA CONNECTION")
    print("="*60)
    
    try:
        client = JiraClient()
        result = client.test_connection()
        
        if result.get("success"):
            print(f"✓ Connected successfully")
            print(f"  User: {result.get('user')}")
            print(f"  Email: {result.get('email')}")
            return client
        else:
            print(f"✗ Connection failed: {result.get('error')}")
            return None
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return None


def test_list_projects(client):
    """Test listing projects"""
    print("\n" + "="*60)
    print("TESTING: list_projects")
    print("="*60)
    
    try:
        result = project_tools.list_projects(client)
        
        if result.get("error"):
            print(f"✗ Error: {result.get('message')}")
        else:
            print(f"✓ Found {result.get('total')} projects")
            for project in result.get("projects", [])[:5]:
                print(f"  - {project.get('key')}: {project.get('name')}")
            if result.get('total', 0) > 5:
                print(f"  ... and {result.get('total') - 5} more")
                
    except Exception as e:
        print(f"✗ Exception: {str(e)}")


def test_search_issues(client):
    """Test searching issues"""
    print("\n" + "="*60)
    print("TESTING: search_issues")
    print("="*60)
    
    # Try to search for any issues (limit to 5)
    jql = "ORDER BY created DESC"
    
    try:
        result = search_tools.search_issues(client, jql, max_results=5)
        
        if result.get("error"):
            print(f"✗ Error: {result.get('message')}")
        else:
            print(f"✓ Found {result.get('total')} total issues")
            print(f"  Returned: {result.get('returned')} issues")
            for issue in result.get("issues", []):
                print(f"  - {issue.get('key')}: {issue.get('summary')[:50]}...")
                
    except Exception as e:
        print(f"✗ Exception: {str(e)}")


def test_get_issue_types(client):
    """Test getting issue types"""
    print("\n" + "="*60)
    print("TESTING: get_issue_types")
    print("="*60)
    
    try:
        result = issue_tools.get_issue_types(client)
        
        if result.get("error"):
            print(f"✗ Error: {result.get('message')}")
        else:
            print(f"✓ Found {result.get('total')} issue types")
            for issue_type in result.get("issue_types", []):
                subtask_label = " (subtask)" if issue_type.get("subtask") else ""
                print(f"  - {issue_type.get('name')}{subtask_label}")
                
    except Exception as e:
        print(f"✗ Exception: {str(e)}")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("JIRA MCP SERVER - TEST SUITE")
    print("="*60)
    
    # Setup logging
    logger = setup_logging("INFO")
    
    # Test connection
    client = test_connection()
    
    if not client:
        print("\n✗ Cannot proceed without a valid connection")
        print("\nPlease check your config/config.env file:")
        print("  - JIRA_BASE_URL")
        print("  - JIRA_EMAIL")
        print("  - JIRA_API_TOKEN")
        return
    
    # Run tests
    test_list_projects(client)
    test_search_issues(client)
    test_get_issue_types(client)
    
    print("\n" + "="*60)
    print("TESTS COMPLETED")
    print("="*60)
    print("\nIf all tests passed, your Jira MCP Server is ready to use!")
    print("Run the server with: python src/server.py")


if __name__ == "__main__":
    main()
