# Changelog

All notable changes to the Bitbucket MCP Server project will be documented in this file.

## [1.0.0] - 2026-03-10

### Added
- Initial release of Bitbucket MCP Server
- Complete read-only access to Bitbucket repositories via REST API
- 14 comprehensive tools for repository interaction:
  - `list_repositories` - List workspace repositories
  - `get_repository_details` - Get repository metadata
  - `list_branches` - List repository branches
  - `list_commits` - List commit history
  - `get_commit_details` - Get commit details with diff
  - `list_repository_files` - Browse repository files
  - `read_file_content` - Read file content
  - `get_repository_readme` - Get README file
  - `list_pull_requests` - List pull requests
  - `get_pull_request_details` - Get PR details
  - `get_pull_request_comments` - Get PR comments
  - `list_repository_contributors` - List contributors
  - `search_repository_files` - Search for files
  - `get_repository_tags` - List repository tags

### Features
- Bitbucket App Password authentication
- Comprehensive error handling
- Pagination support for large datasets
- File size limits (1MB) with truncation
- Structured JSON responses
- Detailed logging
- Configuration via environment variables
- Support for public and private repositories

### Security
- Strictly read-only operations (no write/modify/delete)
- Secure credential handling via configuration file
- HTTP Basic Authentication with Bitbucket API

### Documentation
- Complete README with all tool descriptions
- Quick Start Guide for easy setup
- Example usage patterns
- MCP client configuration examples
- Troubleshooting guide

### Technical Details
- Python 3.10+ support
- MCP SDK integration
- Requests library for HTTP
- Async/await support
- Modular architecture with separate tool modules
