# HubSpot MCP Server

An MCP (Model Context Protocol) server that provides access to the HubSpot API, allowing AI assistants to interact with HubSpot data.

## Features

- List and retrieve items from the HubSpot API
- Async HTTP client with error handling
- Typed responses with Pydantic models

## Installation

### Using mpak (Recommended)

```bash
# Configure your API key
mpak config set @JoeCardoso13/hubspot access_token=your_access_token_here

# Run the server
mpak run @JoeCardoso13/hubspot
```

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/JoeCardoso13/mcp-hubspot.git
cd mcp-hubspot

# Install dependencies with uv
uv sync

# Set your access token (from a HubSpot Private App)
export HUBSPOT_ACCESS_TOKEN=your_access_token_here

# Run the server
uv run python -m mcp_hubspot.server
```

## Configuration

### Getting Your Access Token

This server authenticates via a **HubSpot Private App** access token:

1. In HubSpot, go to **Development > Legacy apps > Create legacy app > Private**
2. Name it (e.g. "MCP Server") and go to the **Scopes** tab
3. Add the following scopes:
   - `crm.objects.contacts.read` / `crm.objects.contacts.write`
   - `crm.objects.companies.read` / `crm.objects.companies.write`
   - `crm.objects.deals.read` / `crm.objects.deals.write`
4. Create the app, then go to the **Auth** tab and click **Show token**
5. Copy the token and set it as `HUBSPOT_ACCESS_TOKEN`

### Claude Desktop Configuration

Add to your `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "hubspot": {
      "command": "mpak",
      "args": ["run", "@JoeCardoso13/hubspot"]
    }
  }
}
```

## Available Tools

| Tool | Description |
|------|-------------|
| `list_items` | List items from the API with optional limit |
| `get_item` | Get a single item by its ID |

## Development

```bash
# Install dev dependencies
uv sync --dev

# Run tests
uv run pytest tests/ -v

# Format code
uv run ruff format src/ tests/

# Lint
uv run ruff check src/ tests/

# Type check
uv run ty check src/

# Run all checks
make check
```

## License

MIT
