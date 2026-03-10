"""
Example usage of Jira MCP Server tools
This demonstrates direct usage of the tools (not through MCP protocol)
"""
import sys
import os
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from jira_client import JiraClient
from utils import setup_logging
import issue_tools
import comment_tools
import attachment_tools
import project_tools
import search_tools


def example_1_list_projects(client):
    """
    Example 1: List all projects
    """
    print("\n" + "="*70)
    print("EXAMPLE 1: List all projects")
    print("="*70)
    
    result = project_tools.list_projects(client)
    print(json.dumps(result, indent=2))


def example_2_search_recent_issues(client):
    """
    Example 2: Search for recently created issues
    """
    print("\n" + "="*70)
    print("EXAMPLE 2: Search for recently created issues")
    print("="*70)
    
    jql = "ORDER BY created DESC"
    result = search_tools.search_issues(client, jql, max_results=5)
    print(json.dumps(result, indent=2))


def example_3_get_issue_details(client, issue_key):
    """
    Example 3: Get detailed information about a specific issue
    """
    print("\n" + "="*70)
    print(f"EXAMPLE 3: Get issue details for {issue_key}")
    print("="*70)
    
    result = issue_tools.get_issue_by_key(client, issue_key)
    print(json.dumps(result, indent=2))


def example_4_get_comments(client, issue_key):
    """
    Example 4: Get all comments for an issue
    """
    print("\n" + "="*70)
    print(f"EXAMPLE 4: Get comments for {issue_key}")
    print("="*70)
    
    result = comment_tools.get_issue_comments(client, issue_key)
    print(json.dumps(result, indent=2))


def example_5_get_attachments(client, issue_key):
    """
    Example 5: Get attachments for an issue
    """
    print("\n" + "="*70)
    print(f"EXAMPLE 5: Get attachments for {issue_key}")
    print("="*70)
    
    result = attachment_tools.get_issue_attachments(client, issue_key)
    print(json.dumps(result, indent=2))


def example_6_search_bugs(client, project_key):
    """
    Example 6: Search for open bugs in a project
    """
    print("\n" + "="*70)
    print(f"EXAMPLE 6: Search for open bugs in {project_key}")
    print("="*70)
    
    jql = f"project = {project_key} AND type = Bug AND status != Done"
    result = search_tools.search_issues(client, jql, max_results=10)
    print(json.dumps(result, indent=2))


def example_7_get_closed_stories(client, project_key):
    """
    Example 7: Get closed stories from a project
    """
    print("\n" + "="*70)
    print(f"EXAMPLE 7: Get closed stories from {project_key}")
    print("="*70)
    
    result = search_tools.get_closed_stories(client, project_key, limit=10)
    print(json.dumps(result, indent=2))


def example_8_get_issue_history(client, issue_key):
    """
    Example 8: Get change history for an issue
    """
    print("\n" + "="*70)
    print(f"EXAMPLE 8: Get change history for {issue_key}")
    print("="*70)
    
    result = issue_tools.get_issue_history(client, issue_key, max_results=10)
    print(json.dumps(result, indent=2))


def example_9_get_issue_types(client):
    """
    Example 9: Get all available issue types
    """
    print("\n" + "="*70)
    print("EXAMPLE 9: Get all issue types")
    print("="*70)
    
    result = issue_tools.get_issue_types(client)
    print(json.dumps(result, indent=2))


def main():
    """
    Run example demonstrations
    
    Customize the examples below with your actual project keys and issue keys
    """
    print("="*70)
    print("JIRA MCP SERVER - USAGE EXAMPLES")
    print("="*70)
    
    # Setup logging
    logger = setup_logging("INFO")
    
    # Initialize client
    try:
        client = JiraClient()
        print(f"\n✓ Connected to Jira: {client.base_url}")
    except Exception as e:
        print(f"\n✗ Failed to initialize client: {str(e)}")
        return
    
    # Run examples
    # Note: Update these with your actual project keys and issue keys
    
    # Example 1: List projects (always works)
    example_1_list_projects(client)
    
    # Example 2: Search recent issues (always works)
    example_2_search_recent_issues(client)
    
    # Example 9: Get issue types (always works)
    example_9_get_issue_types(client)
    
    # The following examples require valid issue keys
    # Uncomment and update with your actual keys
    
    # ISSUE_KEY = "PROJ-123"  # Update with your issue key
    # example_3_get_issue_details(client, ISSUE_KEY)
    # example_4_get_comments(client, ISSUE_KEY)
    # example_5_get_attachments(client, ISSUE_KEY)
    # example_8_get_issue_history(client, ISSUE_KEY)
    
    # PROJECT_KEY = "PROJ"  # Update with your project key
    # example_6_search_bugs(client, PROJECT_KEY)
    # example_7_get_closed_stories(client, PROJECT_KEY)
    
    print("\n" + "="*70)
    print("EXAMPLES COMPLETED")
    print("="*70)
    print("\nTo run more examples:")
    print("1. Update the ISSUE_KEY and PROJECT_KEY variables in this script")
    print("2. Uncomment the example function calls")
    print("3. Run the script again")


if __name__ == "__main__":
    main()
