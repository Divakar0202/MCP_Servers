"""
Example Tool Usage for Bitbucket MCP Server

This script demonstrates how each tool can be used and what responses to expect.
These are example JSON requests that an MCP client would send to the server.
"""

# Tool 1: List Repositories
list_repositories_request = {
    "name": "list_repositories",
    "arguments": {
        "limit": 10
    }
}
# Expected response: List of repositories with name, slug, description, language, etc.

# Tool 2: Get Repository Details
get_repository_details_request = {
    "name": "get_repository_details",
    "arguments": {
        "repository_slug": "my-repo"
    }
}
# Expected response: Full repository metadata including project, owner, branches, size

# Tool 3: List Branches
list_branches_request = {
    "name": "list_branches",
    "arguments": {
        "repository_slug": "my-repo",
        "limit": 50
    }
}
# Expected response: List of branches with target commit info

# Tool 4: List Commits
list_commits_request = {
    "name": "list_commits",
    "arguments": {
        "repository_slug": "my-repo",
        "branch_name": "main",
        "limit": 20
    }
}
# Expected response: List of commits with hash, message, author, date

# Tool 5: Get Commit Details
get_commit_details_request = {
    "name": "get_commit_details",
    "arguments": {
        "repository_slug": "my-repo",
        "commit_hash": "abc123def456"
    }
}
# Expected response: Commit info with list of changed files and diff stats

# Tool 6: List Repository Files
list_repository_files_request = {
    "name": "list_repository_files",
    "arguments": {
        "repository_slug": "my-repo",
        "branch": "main",
        "directory_path": "src"
    }
}
# Expected response: Files and directories in the specified path

# Tool 7: Read File Content
read_file_content_request = {
    "name": "read_file_content",
    "arguments": {
        "repository_slug": "my-repo",
        "file_path": "src/app.py",
        "branch": "main"
    }
}
# Expected response: Full file content as string (up to 1MB)

# Tool 8: Get Repository README
get_repository_readme_request = {
    "name": "get_repository_readme",
    "arguments": {
        "repository_slug": "my-repo"
    }
}
# Expected response: README file content

# Tool 9: List Pull Requests
list_pull_requests_request = {
    "name": "list_pull_requests",
    "arguments": {
        "repository_slug": "my-repo",
        "state": "OPEN",
        "limit": 25
    }
}
# Expected response: List of pull requests with title, author, status

# Tool 10: Get Pull Request Details
get_pull_request_details_request = {
    "name": "get_pull_request_details",
    "arguments": {
        "repository_slug": "my-repo",
        "pull_request_id": 42
    }
}
# Expected response: Full PR details including reviewers, commits, approval status

# Tool 11: Get Pull Request Comments
get_pull_request_comments_request = {
    "name": "get_pull_request_comments",
    "arguments": {
        "repository_slug": "my-repo",
        "pull_request_id": 42
    }
}
# Expected response: All comments on the PR including inline code comments

# Tool 12: List Repository Contributors
list_repository_contributors_request = {
    "name": "list_repository_contributors",
    "arguments": {
        "repository_slug": "my-repo"
    }
}
# Expected response: Contributors sorted by commit count

# Tool 13: Search Repository Files
search_repository_files_request = {
    "name": "search_repository_files",
    "arguments": {
        "repository_slug": "my-repo",
        "search_keyword": "test",
        "branch": "main"
    }
}
# Expected response: Files matching "test" in their path

# Tool 14: Get Repository Tags
get_repository_tags_request = {
    "name": "get_repository_tags",
    "arguments": {
        "repository_slug": "my-repo"
    }
}
# Expected response: List of tags with commit information

# Usage Examples for AI Agents

# Example 1: Code Review Assistant
# 1. list_pull_requests (state="OPEN")
# 2. For each PR: get_pull_request_details
# 3. For each changed file: read_file_content
# 4. Analyze code and provide feedback

# Example 2: Documentation Generator
# 1. list_repositories
# 2. For each repo: get_repository_readme
# 3. list_repository_files (recursive)
# 4. read_file_content for key files
# 5. Generate comprehensive documentation

# Example 3: Code Search
# 1. search_repository_files (keyword="function_name")
# 2. read_file_content for matching files
# 3. Analyze implementations

# Example 4: Repository Explorer
# 1. get_repository_details
# 2. list_branches
# 3. list_commits (for main branch)
# 4. list_repository_files (root)
# 5. Navigate through directory structure

# Example 5: Commit Analysis
# 1. list_commits (limit=100)
# 2. For each commit: get_commit_details
# 3. Analyze patterns, frequency, file changes
# 4. Generate insights about development activity

print("Example tool usage patterns defined.")
print("These examples show how to interact with the Bitbucket MCP Server.")
print("Replace 'my-repo' with your actual repository slug.")
