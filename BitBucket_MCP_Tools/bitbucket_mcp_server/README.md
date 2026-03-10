# Bitbucket MCP Server

A complete Model Context Protocol (MCP) server providing **read-only** access to Bitbucket repositories via the Bitbucket REST API.

This MCP server enables AI agents like Claude and OpenClaw to interact with Bitbucket repositories to retrieve information, explore source code, analyze commits, and inspect pull requests.

## 🔒 Security

**This server is strictly read-only.** It does not expose any operations that can modify repositories, including:
- ❌ No repository creation or deletion
- ❌ No commit pushing or merging
- ❌ No file modifications
- ❌ No branch creation or deletion
- ❌ No pull request modifications

## ✨ Features

### Repository Operations
- List all repositories in a workspace
- Get detailed repository metadata
- List repository contributors with commit counts
- Get repository tags

### Branch & Commit Operations
- List all branches in a repository
- List commit history with optional branch filtering
- Get detailed commit information including changed files

### File Operations
- Browse repository directory structures
- Read source code file contents (with 1MB size limit)
- Retrieve README files automatically
- Search for files by keyword

### Pull Request Operations
- List pull requests (open, merged, declined)
- Get detailed pull request information
- View pull request comments
- See reviewer status and approvals

## 📋 Requirements

- Python 3.10 or higher
- Bitbucket account with App Password
- Access to Bitbucket workspace

## 🚀 Installation

### 1. Clone or create the project structure

```bash
bitbucket_mcp_server/
├── config/
│   └── config.env
├── src/
│   ├── server.py
│   ├── bitbucket_client.py
│   ├── repository_tools.py
│   ├── file_tools.py
│   ├── commit_tools.py
│   ├── branch_tools.py
│   ├── pull_request_tools.py
│   ├── search_tools.py
│   └── utils.py
├── requirements.txt
└── README.md
```

### 2. Install dependencies

```bash
cd bitbucket_mcp_server
pip install -r requirements.txt
```

### 3. Configure Bitbucket credentials

Edit `config/config.env` with your Bitbucket details:

```env
BITBUCKET_BASE_URL=https://api.bitbucket.org/2.0
BITBUCKET_WORKSPACE=your_workspace_name
BITBUCKET_USERNAME=your_bitbucket_username
BITBUCKET_APP_PASSWORD=your_app_password
```

#### Creating a Bitbucket App Password

1. Go to Bitbucket Settings → Personal settings → App passwords
2. Click "Create app password"
3. Give it a name (e.g., "MCP Server")
4. Select permissions:
   - **Repositories**: Read
   - **Pull requests**: Read
   - **Account**: Read
5. Copy the generated password to your `config.env`

## 🎯 Usage

### Starting the Server

```bash
cd bitbucket_mcp_server
python src/server.py
```

The server will:
1. Load configuration from `config/config.env`
2. Validate Bitbucket API connectivity
3. Start the MCP server on stdio
4. Wait for tool requests from MCP clients

### Testing the Server

You can test the server using any MCP client or the MCP Inspector.

## 🛠️ Available Tools

### 1. **list_repositories**
List all repositories in the configured workspace.

**Parameters:**
- `limit` (optional): Maximum number of repositories (default: 50, max: 100)

**Example Response:**
```json
{
  "workspace": "my-workspace",
  "total_repositories": 5,
  "repositories": [
    {
      "slug": "my-repo",
      "name": "My Repository",
      "description": "A sample repository",
      "is_private": true,
      "language": "Python",
      "created_on": "2024-01-01T00:00:00+00:00"
    }
  ]
}
```

### 2. **get_repository_details**
Get detailed information about a specific repository.

**Parameters:**
- `repository_slug` (required): Repository identifier

**Returns:** Repository metadata including project info, owner, size, branches, and clone URLs.

### 3. **list_branches**
List all branches in a repository.

**Parameters:**
- `repository_slug` (required): Repository identifier
- `limit` (optional): Maximum branches to return (default: 100)

### 4. **list_commits**
List commit history for a repository.

**Parameters:**
- `repository_slug` (required): Repository identifier
- `branch_name` (optional): Branch to filter commits
- `limit` (optional): Maximum commits to return (default: 50)

**Returns:** List of commits with hash, message, author, and date.

### 5. **get_commit_details**
Get detailed information about a specific commit.

**Parameters:**
- `repository_slug` (required): Repository identifier
- `commit_hash` (required): Commit SHA/hash

**Returns:** Commit details including changed files, additions, deletions.

### 6. **list_repository_files**
List files and directories in a repository path.

**Parameters:**
- `repository_slug` (required): Repository identifier
- `branch` (optional): Branch name (default: "main")
- `directory_path` (optional): Directory path (default: root)

### 7. **read_file_content**
Read the full content of a source code file.

**Parameters:**
- `repository_slug` (required): Repository identifier
- `file_path` (required): Path to the file
- `branch` (optional): Branch name (default: "main")

**Returns:** File content (truncated to 1MB if necessary)

**Example:**
```json
{
  "repository": "my-repo",
  "branch": "main",
  "file_path": "src/app.py",
  "content": "def hello():\n    print('Hello World')",
  "size_bytes": 45,
  "truncated": false
}
```

### 8. **get_repository_readme**
Retrieve the README file from a repository.

**Parameters:**
- `repository_slug` (required): Repository identifier
- `branch` (optional): Branch name (defaults to main branch)

**Returns:** README content (supports .md, .rst, .txt formats)

### 9. **list_pull_requests**
List pull requests in a repository.

**Parameters:**
- `repository_slug` (required): Repository identifier
- `state` (optional): PR state - OPEN, MERGED, DECLINED, SUPERSEDED (default: "OPEN")
- `limit` (optional): Maximum PRs to return (default: 50)

### 10. **get_pull_request_details**
Get detailed information about a specific pull request.

**Parameters:**
- `repository_slug` (required): Repository identifier
- `pull_request_id` (required): Pull request ID

**Returns:** PR details including commits, reviewers, participants, approvals.

### 11. **get_pull_request_comments**
Get all comments for a pull request.

**Parameters:**
- `repository_slug` (required): Repository identifier
- `pull_request_id` (required): Pull request ID

**Returns:** List of comments including inline code comments.

### 12. **list_repository_contributors**
List contributors to a repository with commit counts.

**Parameters:**
- `repository_slug` (required): Repository identifier

**Returns:** Contributors sorted by number of commits.

### 13. **search_repository_files**
Search for files in a repository matching a keyword.

**Parameters:**
- `repository_slug` (required): Repository identifier
- `search_keyword` (required): Keyword to search in file paths
- `branch` (optional): Branch name (default: "main")

**Returns:** List of matching file paths (limited to 100 results).

### 14. **get_repository_tags**
List all tags in a repository.

**Parameters:**
- `repository_slug` (required): Repository identifier

**Returns:** List of tags with commit information.

## 🔧 Configuration

### Environment Variables

The server reads configuration from `config/config.env`:

| Variable | Description | Required |
|----------|-------------|----------|
| `BITBUCKET_BASE_URL` | Bitbucket API base URL | Yes |
| `BITBUCKET_WORKSPACE` | Your Bitbucket workspace name | Yes |
| `BITBUCKET_USERNAME` | Your Bitbucket username | Yes |
| `BITBUCKET_APP_PASSWORD` | Your Bitbucket app password | Yes |

### Performance Limits

- **File size limit**: 1 MB per file (content truncated if larger)
- **Pagination**: Maximum 100 items per page
- **Search results**: Maximum 100 files per search
- **API timeout**: 30 seconds per request

## 🐛 Error Handling

The server handles common errors gracefully:

- **Invalid repository**: Returns structured error with message
- **Missing files**: Returns "File not found" error
- **API rate limits**: Returns rate limit error with retry message
- **Authentication failures**: Returns authentication error
- **Network failures**: Returns connection error with details

All errors are returned as JSON:
```json
{
  "error": "ErrorType",
  "message": "Detailed error message"
}
```

## 📝 Logging

The server uses Python's logging module to log:
- INFO: Server startup, connection validation, successful operations
- ERROR: API failures, tool execution errors
- DEBUG: Detailed operation information

Logs are written to stdout with timestamps.

## 🔐 Authentication

The server uses **HTTP Basic Authentication** with Bitbucket:
- Username + App Password encoded as Base64
- Included in `Authorization` header for all requests
- App Password provides scoped access (read-only repositories)

## 🌐 Bitbucket API

This server uses the official Bitbucket REST API v2.0:
- Base URL: `https://api.bitbucket.org/2.0`
- Documentation: https://developer.atlassian.com/cloud/bitbucket/rest/

## 🤝 Integration with AI Agents

This MCP server is designed to work with AI agents like:
- **Claude Desktop** (via MCP protocol)
- **OpenClaw** (custom AI agent)
- Any MCP-compatible client

### Example Use Cases

1. **Code Review Assistant**: AI agent analyzes pull requests and provides feedback
2. **Documentation Generator**: AI reads repository files and generates documentation
3. **Code Search**: AI searches across repositories to find specific implementations
4. **Commit Analysis**: AI analyzes commit patterns and code changes
5. **Repository Explorer**: AI helps navigate large codebases

## 📦 Project Structure

```
bitbucket_mcp_server/
├── config/
│   └── config.env              # Configuration file
├── src/
│   ├── server.py               # Main MCP server
│   ├── bitbucket_client.py     # Bitbucket API client
│   ├── repository_tools.py     # Repository operations
│   ├── file_tools.py           # File operations
│   ├── commit_tools.py         # Commit operations
│   ├── branch_tools.py         # Branch operations
│   ├── pull_request_tools.py   # Pull request operations
│   ├── search_tools.py         # Search operations
│   └── utils.py                # Helper functions
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🧪 Development

### Adding New Tools

1. Create or modify the appropriate tool module (e.g., `repository_tools.py`)
2. Add the tool method to the tool class
3. Register the tool in `server.py` in `handle_list_tools()`
4. Add the tool handler in `handle_call_tool()`

### Testing

Test individual tools by invoking them through an MCP client or using the MCP Inspector.

## ⚠️ Limitations

- Read-only access (by design)
- File content limited to 1MB
- Search limited to 100 results
- Recursive directory search limited by depth
- API rate limits apply (Bitbucket API restrictions)

## 📄 License

This project is provided as-is for use with Bitbucket repositories.

## 🤝 Contributing

Contributions are welcome! Please ensure:
- All new tools are read-only
- Error handling is comprehensive
- Code follows existing patterns
- Documentation is updated

## 🙏 Support

For issues or questions:
1. Check Bitbucket API documentation
2. Verify your App Password permissions
3. Check server logs for detailed error messages
4. Ensure MCP SDK is properly installed

## 📚 Additional Resources

- [Bitbucket REST API Documentation](https://developer.atlassian.com/cloud/bitbucket/rest/)
- [MCP Protocol Specification](https://modelcontextprotocol.io)
- [Bitbucket App Passwords Guide](https://support.atlassian.com/bitbucket-cloud/docs/app-passwords/)

---

**Note**: This server is designed for read-only operations and does not support any write, update, or delete operations on Bitbucket repositories.
