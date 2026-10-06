# Colab-mcp

An MCP server for bridging your local agent to a Colab session in the browser.

# Supported Clients
The client must run locally on your device. Clients that support
`notifications/tools/list_changed` can use notebook tools directly after connection.
Clients such as Codex can use the permanent `colab_list_tools` and
`colab_call_tool` tools to discover and call notebook tools after connection.

Popular clients that fit these criteria include:
- Gemini CLI
- Claude Code
- Windsurf
- Codex (with `colab_list_tools` and `colab_call_tool`)

## Codex local clone

This clone contains 2 changes relative to upstream commit
`b9ab3899e0f1fa493390b1fd6d54aa2e464ecdf1`: permanent notebook discovery/calling
tools and a fix that preserves proxy startup after the 60-second connection wait.
A timeout returns `false`; you can connect later or retry using the same server.
Google's token validation, allowed browser origins, and single-notebook rule remain.

Run this clone with `uv run --project /absolute/path/to/colab-mcp colab-mcp`.
Then:

1. Call `open_colab_browser_connection`.
2. Connect your chosen notebook. Use **Connect separate tabs** to select an existing notebook.
3. Call `colab_list_tools` for current names and input schemas.
4. Call `colab_call_tool` with a tool name and matching arguments.

Notebook results retain content, images, structured output, metadata, and the
`isError` flag. The clone uses the existing MCP stdio transport, so it does not
need the separate Codex adapter or its JSON-line reader. Request bounded cell
ranges when reading output; the existing browser transport still applies its
message limit. Restart the configured MCP server after a source update.


# Setup

- Install `uv` (`pip install uv`)
- Configure for usage (eg for mcp.json style services):

```
...
  "mcpServers": {
    "colab-mcp": {
      "command": "uvx",
      "args": ["git+https://github.com/googlecolab/colab-mcp"],
      "timeout": 30000
    }
  }
...
```

(If you have a non-standard default package index (**Googlers**), you may also need to add `--index https://pypi.org/simple`)

# Issues & Discussions

We are using GitHub [discussions](https://github.com/googlecolab/colab-mcp/discussions) as the
place for issue discussion and feature requests. As discussions mature into action items, we
will add those items as issues. This helps us ensure that issues in the issue tracker are
well-understood, deduplicated, and actionable. For these reasons, **please do <u>NOT</u> open
issues directly.** 

# Contributing 
We unfortunately don't have the bandwidth to support review of external contributions, and we 
don't want user PRs to languish, so we aren't accepting any external contributions right now.

If you have a great idea or pain point, we would love to hear about it on our 
[discussions](https://github.com/googlecolab/colab-mcp/discussions) page - the preferred place 
for issue discussion and feature requests.

# Internal - For Colab Developers

### Prerequisites

- `uv` is required (`pip install uv`)
- Configure git hooks to run repo presubmits

```shell
git config core.hooksPath .githooks
```

### Gemini CLI setup

```
...
  "mcpServers": {
    "colab-mcp": {
      "command": "uv",
      "args": ["run", "colab-mcp"],
      "cwd": "/path/to/github/colab-mcp",
      "timeout": 30000
    }
  }
...
```
