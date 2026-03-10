# Changelog

All notable changes to the Jira MCP Server will be documented in this file.

## [1.0.0] - 2026-03-10

### Added
- Initial release of Jira MCP Server
- Read-only MCP server implementation
- 12 tools for Jira interaction:
  - `list_projects` - List all projects
  - `search_issues` - Search issues with JQL
  - `get_issue_by_key` - Get issue by key
  - `get_issue_by_id` - Get issue by ID
  - `get_issue_comments` - Get issue comments
  - `get_issue_attachments` - Get issue attachments
  - `download_attachment` - Get attachment metadata
  - `get_issue_types` - List issue types
  - `get_assignee_details` - Get user details
  - `get_reporter_details` - Get reporter info
  - `get_closed_stories` - Get closed issues
  - `get_issue_history` - Get issue changelog
- Jira REST API v3 client with authentication
- Comprehensive error handling
- Structured JSON responses
- Configuration via environment file
- Connection testing utility
- Example usage scripts
- Comprehensive documentation

### Security
- Strict read-only access enforcement
- API token authentication
- No write operations exposed
- Secure credential management

### Documentation
- README.md with complete usage guide
- SETUP.md with quick start instructions
- Example scripts and test utilities
- Claude Desktop integration example

## Future Considerations

Potential enhancements (maintaining read-only constraint):
- Advanced filtering options
- Caching for improved performance
- Batch operations for multiple issues
- Export to various formats (CSV, JSON)
- Dashboard and analytics queries
- Custom field support
- Webhook integration for notifications (read-only)
