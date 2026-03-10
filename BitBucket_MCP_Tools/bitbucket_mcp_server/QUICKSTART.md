# Bitbucket MCP Server - Quick Start Guide

## Prerequisites
- Python 3.10 or higher installed
- Bitbucket account
- Bitbucket App Password (with Read permissions)

## Step 1: Install Dependencies

```bash
cd bitbucket_mcp_server
pip install -r requirements.txt
```

## Step 2: Configure Bitbucket Access

1. **Create a Bitbucket App Password:**
   - Log in to Bitbucket
   - Go to Personal Settings → App Passwords
   - Click "Create app password"
   - Name: "MCP Server"
   - Permissions: Check "Repositories - Read", "Pull requests - Read", "Account - Read"
   - Click "Create"
   - **Copy the generated password immediately** (you won't see it again)

2. **Edit config/config.env:**
   ```env
   BITBUCKET_BASE_URL=https://api.bitbucket.org/2.0
   BITBUCKET_WORKSPACE=your-workspace-name
   BITBUCKET_USERNAME=your-bitbucket-username
   BITBUCKET_APP_PASSWORD=paste-your-app-password-here
   ```

   Replace:
   - `your-workspace-name` with your Bitbucket workspace slug
   - `your-bitbucket-username` with your Bitbucket username
   - `paste-your-app-password-here` with the app password you just created

## Step 3: Start the Server

### Option A: Using Python directly
```bash
python src/server.py
```

### Option B: Using the start script
```bash
python start_server.py
```

## Step 4: Verify Connection

If everything is configured correctly, you should see:
```
Bitbucket MCP Server - Read-Only Repository Access
============================================================
INFO - Initializing Bitbucket MCP Server...
INFO - Validating Bitbucket API connection...
INFO - Bitbucket API connection validated successfully
INFO - Bitbucket MCP Server initialized successfully
INFO - Workspace: your-workspace-name
INFO - Server is ready to accept requests
```

## Step 5: Test the Server

The server is now ready to receive MCP tool requests from AI agents.

### Using with Claude Desktop

Add to your Claude Desktop MCP configuration:

```json
{
  "mcpServers": {
    "bitbucket-readonly": {
      "command": "python",
      "args": ["path/to/bitbucket_mcp_server/src/server.py"]
    }
  }
}
```

## Common Issues

### Issue: "Authentication failed"
- **Solution**: Verify your username and app password in config.env
- Make sure your app password has "Repositories - Read" permission

### Issue: "Resource not found"
- **Solution**: Check that your workspace name is correct
- Verify you have access to the workspace

### Issue: "Connection error"
- **Solution**: Check your internet connection
- Verify BITBUCKET_BASE_URL is correct

### Issue: Module not found
- **Solution**: Make sure all dependencies are installed
  ```bash
  pip install -r requirements.txt
  ```

## Available Tools

Once running, the server provides 14 read-only tools:

1. `list_repositories` - List all repositories in workspace
2. `get_repository_details` - Get repository info
3. `list_branches` - List repository branches
4. `list_commits` - List commit history
5. `get_commit_details` - Get commit details
6. `list_repository_files` - Browse repository files
7. `read_file_content` - Read file content
8. `get_repository_readme` - Get README file
9. `list_pull_requests` - List pull requests
10. `get_pull_request_details` - Get PR details
11. `get_pull_request_comments` - Get PR comments
12. `list_repository_contributors` - List contributors
13. `search_repository_files` - Search for files
14. `get_repository_tags` - List repository tags

## Next Steps

- Read the full [README.md](README.md) for detailed tool documentation
- Explore the Bitbucket API at https://developer.atlassian.com/cloud/bitbucket/rest/
- Integrate with your AI agent or MCP client

## Security Reminder

This server is **read-only** and cannot modify your repositories. It's safe to use with AI agents.
