# Quick Setup Guide

## Step 1: Install Python Dependencies

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure Jira Credentials

1. Get your Jira API token from: https://id.atlassian.com/manage-profile/security/api-tokens

2. Edit `config/config.env`:
   ```env
   JIRA_BASE_URL=https://your-domain.atlassian.net
   JIRA_EMAIL=your-email@example.com
   JIRA_API_TOKEN=your-api-token-here
   ```

## Step 3: Test Connection

```powershell
python test_connection.py
```

You should see:
```
✓ Connected successfully
  User: Your Name
  Email: your-email@example.com
```

## Step 4: Run the MCP Server

```powershell
cd src
python server.py
```

## Step 5: Configure MCP Client (Optional)

### For Claude Desktop

Edit your Claude Desktop config file:
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`

Add:
```json
{
  "mcpServers": {
    "jira": {
      "command": "python",
      "args": ["d:/Jira_MCP_Tools/src/server.py"]
    }
  }
}
```

Replace `d:/Jira_MCP_Tools/` with your actual path.

## Troubleshooting

### "Module not found: mcp"
```powershell
pip install mcp
```

### "401 Unauthorized"
- Check your API token is correct
- Ensure email matches your Jira account

### "Connection timeout"
- Check JIRA_BASE_URL is correct
- Verify network connectivity

## Next Steps

Once everything works:
1. Try the example queries in README.md
2. Explore JQL queries for your use case
3. Integrate with your AI agent

## Support

Check README.md for detailed documentation and examples.
