# MCP Server Installation & Management Guide

## What is MCP?

**Model Context Protocol (MCP)** allows Claude Code to connect to external servers that provide:
- **Tools** - Functions Claude can call during conversations
- **Resources** - Data sources Claude can access with @ mentions
- **Prompts** - Pre-configured prompt templates

---

## Installation & Setup

### Step 1: Find an MCP Server

MCP servers can be:
- **HTTP/SSE servers** - Web-based servers with a URL
- **stdio servers** - npm packages that run locally

Examples:
- LangChain Docs: `https://docs.langchain.com/mcp`
- GitHub MCP: `npx -y @modelcontextprotocol/server-github`
- Filesystem: `npx -y @modelcontextprotocol/server-filesystem`

### Step 2: Add the MCP Server

Use the `claude mcp add` command with the appropriate transport type:

#### For HTTP Servers
```bash
claude mcp add --transport http <server-name> <url>
```

**Example:**
```bash
claude mcp add --transport http langchain https://docs.langchain.com/mcp
```

#### For SSE Servers
```bash
claude mcp add --transport sse <server-name> <url>
```

**Example:**
```bash
claude mcp add --transport sse asana https://mcp.asana.com/sse
```

#### For stdio (npm) Servers
```bash
claude mcp add --transport stdio <server-name> -- <command> <args...>
```

**Example:**
```bash
claude mcp add --transport stdio github -- npx -y @modelcontextprotocol/server-github
```

**With environment variables:**
```bash
claude mcp add --transport stdio github \
  --env GITHUB_TOKEN=your_token_here \
  -- npx -y @modelcontextprotocol/server-github
```

### Step 3: Verify Installation

Check that the server is connected:
```bash
/mcp
```

You should see your server listed with a ✔ connected status.

### Step 4: Restart Conversation

**Important:** After adding a new MCP server, you must start a new Claude Code conversation for the tools to become available.

Exit and restart:
```bash
# Exit current conversation
exit

# Start new conversation
claude
```

---

## Configuration Scopes

MCP servers can be configured at three levels:

### 1. User Config (Global)
**Location:** `~/.claude.json`

Available in **all your projects**. Good for:
- Personal API keys
- Commonly used tools across all projects

**How to add:**
```bash
# This adds to user config by default if not in a git repo
claude mcp add --transport http myserver https://example.com/mcp
```

### 2. Project Config (Shared)
**Location:** `<project-root>/.mcp.json`

Shared with your **team via git**. Good for:
- Project-specific tools
- Team-wide integrations

**How to add:**
```bash
# Create .mcp.json in project root
# Add to .mcp.json manually or via:
claude mcp add --scope project --transport http myserver https://example.com/mcp
```

### 3. Local Config (Private)
**Location:** `~/.claude.json` (project-specific section)

Private to **you in this project**. Good for:
- Personal API keys for project tools
- Testing servers

**How to add:**
```bash
# When in a project directory, this adds to local scope
claude mcp add --transport http myserver https://example.com/mcp
```

---

## Managing MCP Servers

### List All MCP Servers

```bash
/mcp
```

Or from terminal:
```bash
claude mcp list
```

### View Server Details

In the `/mcp` interface:
1. Navigate to the server
2. Press `Enter` to view details (tools, status, logs)

### Remove an MCP Server

```bash
claude mcp remove <server-name>
```

**Example:**
```bash
claude mcp remove langchain
```

### Enable/Disable MCP Servers

#### Temporary Disable (Current Session)
In the `/mcp` interface, you can toggle servers on/off for the current conversation.

#### Permanent Disable
Remove the server completely:
```bash
claude mcp remove <server-name>
```

Or manually edit the config file and remove the server entry:
- `~/.claude.json` (for user/local config)
- `.mcp.json` (for project config)

### View MCP Logs

If a server is failing, check the logs:
```bash
# Location shown in /mcp interface
~/Library/Caches/claude-cli-nodejs/<project-hash>/mcp-logs-<server-name>/
```

Or run Claude Code with debug mode:
```bash
claude --debug
```

---

## Using MCP Tools in Conversations

Once an MCP server is connected and you've restarted your conversation:

### 1. Tools (Automatic)
Claude automatically calls MCP tools when relevant to your questions.

**Example:**
```
You: How do I use Qdrant with LangChain?
Claude: [Automatically calls SearchDocsByLangChain tool]
```

### 2. Resources (@ Mentions)
Reference MCP resources using @ syntax.

**Example:**
```
@github-repo/README.md
```

### 3. Slash Commands
Some MCP servers provide custom slash commands.

**Example:**
```
/mcp__github__list_prs
```

---

## Common MCP Servers

### LangChain Documentation
```bash
claude mcp add --transport http langchain https://docs.langchain.com/mcp
```

**Provides:** Documentation search tool

### GitHub
```bash
claude mcp add --transport stdio github \
  --env GITHUB_TOKEN=ghp_your_token_here \
  -- npx -y @modelcontextprotocol/server-github
```

**Provides:** Repository management, PR/issue tools

### Filesystem
```bash
claude mcp add --transport stdio filesystem \
  -- npx -y @modelcontextprotocol/server-filesystem /path/to/directory
```

**Provides:** File system access to specified directory

### Brave Search
```bash
claude mcp add --transport stdio brave-search \
  --env BRAVE_API_KEY=your_key_here \
  -- npx -y @modelcontextprotocol/server-brave-search
```

**Provides:** Web search capabilities

---

## Troubleshooting

### Server Shows "Failed" Status

1. **Check logs:**
   ```bash
   ls ~/Library/Caches/claude-cli-nodejs/*/mcp-logs-<server-name>/
   ```

2. **Common issues:**
   - Wrong package name (check npm registry)
   - Missing environment variables (API keys)
   - Network issues (for HTTP/SSE servers)

3. **Run with debug mode:**
   ```bash
   claude --debug
   ```

### Tools Not Available

1. **Verify server is connected:**
   ```bash
   /mcp
   ```
   Look for ✔ connected status

2. **Restart conversation:**
   MCP tools load at conversation start. Exit and restart Claude Code.

3. **Check config file:**
   ```bash
   cat ~/.claude.json | grep -A 10 "mcpServers"
   ```

### Wrong Package Name

If you get "404 Not Found" errors:
1. Search npm for the correct package:
   ```bash
   npm search <package-name>
   ```

2. Remove and re-add with correct name:
   ```bash
   claude mcp remove <server-name>
   claude mcp add --transport stdio <server-name> -- npx -y <correct-package-name>
   ```

---

## Best Practices

1. **Use appropriate scopes:**
   - User config for personal tools
   - Project config for team tools
   - Local config for sensitive credentials

2. **Secure API keys:**
   - Never commit API keys to `.mcp.json`
   - Use environment variables or local config for credentials

3. **Test before sharing:**
   - Test MCP servers in local config first
   - Move to project config once stable

4. **Document project MCP servers:**
   - Add setup instructions to project README
   - List required environment variables

5. **Regular cleanup:**
   - Remove unused MCP servers
   - Keep configuration files organized

---

## Additional Resources

- **Official Documentation:** https://docs.claude.com/en/docs/claude-code/mcp
- **MCP Specification:** https://spec.modelcontextprotocol.io/
- **MCP Server Registry:** Check npm for `@modelcontextprotocol/server-*` packages

---

## Quick Reference

```bash
# Add MCP server
claude mcp add --transport <http|sse|stdio> <name> <url-or-command>

# List servers
claude mcp list
# or
/mcp

# Remove server
claude mcp remove <name>

# View in conversation
/mcp

# Check status
claude --debug
```

---

**Note:** Always restart your Claude Code conversation after adding, removing, or modifying MCP servers for changes to take effect.
