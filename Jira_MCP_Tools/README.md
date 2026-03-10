# Jira MCP Server

A production-ready Model Context Protocol (MCP) server that provides **read-only** access to Jira using the Jira REST API v3.

This MCP server enables AI agents (such as OpenClaw, Claude Desktop, or other MCP clients) to retrieve Jira issues, comments, attachments, project data, and other metadata without the ability to modify any data.

## 🔒 Security

**This server enforces strict read-only access.** It does not expose any Jira API endpoints that allow:
- Creating issues
- Updating issues
- Deleting issues
- Transitioning issues
- Adding or modifying comments
- Modifying attachments

## 🎯 Features

### Available Tools

The MCP server exposes 12 read-only tools:

1. **list_projects** - Get all accessible Jira projects
2. **search_issues** - Search issues using JQL (Jira Query Language)
3. **get_issue_by_key** - Fetch issue details by key (e.g., PROJ-123)
4. **get_issue_by_id** - Fetch issue details by ID
5. **get_issue_comments** - Get all comments for an issue
6. **get_issue_attachments** - Get attachments with metadata (including images)
7. **download_attachment** - Get attachment download URL and metadata
8. **get_issue_types** - List all issue types (Story, Bug, Task, Epic, etc.)
9. **get_assignee_details** - Get user details by account ID
10. **get_reporter_details** - Get reporter information
11. **get_closed_stories** - Get closed/done issues from a project
12. **get_issue_history** - Get issue change history

## 📋 Requirements

- Python 3.8 or higher
- Jira Cloud instance with API access
- Jira API token

## 🚀 Installation

### 1. Clone or download this repository

```bash
cd Jira_MCP_Tools
```

### 2. Create a virtual environment (recommended)

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

### 1. Get your Jira API Token

1. Log in to your Atlassian account
2. Go to: https://id.atlassian.com/manage-profile/security/api-tokens
3. Click "Create API token"
4. Give it a name (e.g., "MCP Server")
5. Copy the generated token

### 2. Configure the server

Edit `config/config.env` with your credentials:

```env
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token-here
```

**Important:** Never commit your `config.env` file to version control!

## 🏃 Running the Server

### Direct execution

```bash
cd src
python server.py
```

### As an MCP server

The server uses stdio transport and can be configured in MCP clients.

Example configuration for Claude Desktop (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "jira": {
      "command": "python",
      "args": ["d:/Jira_MCP_Tools/src/server.py"],
      "env": {}
    }
  }
}
```

## 📚 Usage Examples

### Example 1: Search for open bugs

```json
{
  "tool": "search_issues",
  "arguments": {
    "jql_query": "project = MYPROJECT AND type = Bug AND status = Open",
    "max_results": 20
  }
}
```

### Example 2: Get issue details

```json
{
  "tool": "get_issue_by_key",
  "arguments": {
    "jira_key": "PROJ-123"
  }
}
```

### Example 3: Get comments for an issue

```json
{
  "tool": "get_issue_comments",
  "arguments": {
    "jira_key": "PROJ-123"
  }
}
```

### Example 4: Get closed stories

```json
{
  "tool": "get_closed_stories",
  "arguments": {
    "project_key": "MYPROJECT",
    "limit": 50
  }
}
```

## 🔧 Project Structure

```
jira_mcp_server/
├── config/
│   └── config.env              # Jira credentials (DO NOT COMMIT)
├── src/
│   ├── server.py               # Main MCP server entry point
│   ├── jira_client.py          # Jira API client with authentication
│   ├── issue_tools.py          # Issue-related tools
│   ├── comment_tools.py        # Comment-related tools
│   ├── attachment_tools.py     # Attachment-related tools
│   ├── search_tools.py         # Search-related tools
│   ├── project_tools.py        # Project-related tools
│   └── utils.py                # Utility functions
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore file
└── README.md                   # This file
```

## 📊 Response Format

All tools return structured JSON responses:

```json
{
  "jira_key": "PROJ-123",
  "summary": "Fix login bug",
  "status": "Done",
  "assignee": {
    "display_name": "John Doe",
    "email": "john@example.com",
    "account_id": "5d..."
  },
  "reporter": {
    "display_name": "Jane Smith",
    "email": "jane@example.com",
    "account_id": "5e..."
  },
  "created": "2024-03-10 10:00:00 UTC",
  "updated": "2024-03-10 15:30:00 UTC"
}
```

## ⚠️ Error Handling

The server handles various error scenarios:

- Invalid Jira keys
- Network failures
- API rate limits
- Authentication errors
- Permission errors

Error responses follow this format:

```json
{
  "error": true,
  "error_type": "HTTPError",
  "message": "404 Client Error: Not Found",
  "context": "Failed to fetch issue PROJ-999"
}
```

## 🔍 JQL Query Examples

Here are some useful JQL queries for the `search_issues` tool:

```jql
# All open issues in a project
project = MYPROJECT AND status = Open

# High priority bugs
project = MYPROJECT AND type = Bug AND priority = High

# Issues assigned to me
assignee = currentUser()

# Recently updated issues
project = MYPROJECT AND updated >= -7d

# Epic with all its stories
"Epic Link" = PROJ-123

# Issues with attachments
project = MYPROJECT AND attachments is not EMPTY
```

## 🛡️ Security Best Practices

1. **Never commit** your `config.env` file to version control
2. **Use API tokens** instead of passwords
3. **Rotate tokens** periodically
4. **Limit permissions** - use a service account with read-only access
5. **Monitor usage** - keep track of API calls in Jira's audit log

## 🧪 Testing Connection

When the server starts, it automatically tests the Jira connection:

```
2024-03-10 10:00:00 - jira_mcp_server - INFO - Jira client initialized for https://your-domain.atlassian.net
2024-03-10 10:00:01 - jira_mcp_server - INFO - Testing Jira connection...
2024-03-10 10:00:02 - jira_mcp_server - INFO - ✓ Connected to Jira as John Doe
2024-03-10 10:00:02 - jira_mcp_server - INFO - Starting MCP server on stdio...
```

## 📈 Performance

- Default issue search limit: 50 results
- Maximum search limit: 100 results
- Pagination supported via `start_at` parameter
- Request timeout: 30 seconds

## 🤝 Integration with AI Agents

This MCP server is designed to work with:

- **Claude Desktop** - Anthropic's desktop app
- **OpenClaw** - AI coding assistant
- Any MCP-compatible client

The server provides structured data that AI agents can use to:
- Answer questions about Jira issues
- Generate reports
- Analyze project status
- Track issue history
- Retrieve attachments and documentation

## 🐛 Troubleshooting

### Connection failed

```
✗ Failed to connect to Jira: 401 Unauthorized
```

**Solution:** Check your email and API token in `config/config.env`

### Module not found

```
ModuleNotFoundError: No module named 'mcp'
```

**Solution:** Install dependencies: `pip install -r requirements.txt`

### Permission denied

```
403 Client Error: Forbidden
```

**Solution:** Ensure your Jira account has access to the requested resources

## 📝 License

This project is provided as-is for educational and professional use.

## 🔗 Resources

- [Jira REST API Documentation](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [MCP Protocol](https://modelcontextprotocol.io/)
- [JQL Reference](https://support.atlassian.com/jira-service-management-cloud/docs/use-advanced-search-with-jira-query-language-jql/)

## 💡 Support

For issues or questions:
1. Check the troubleshooting section
2. Review Jira API logs
3. Verify your credentials
4. Check network connectivity

---

**Built with ❤️ for safe, read-only Jira integration with AI agents**
