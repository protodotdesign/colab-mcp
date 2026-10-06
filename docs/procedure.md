# Codex compatibility procedure

Keep the patch small against upstream commit
`b9ab3899e0f1fa493390b1fd6d54aa2e464ecdf1`. Preserve upstream browser authentication,
origin checks, single-notebook selection, and dynamic tools for other clients.

Run `uv run --locked pytest` and Ruff checks. Tests must cover repeated UI
timeouts followed by a late connection, permanent discovery before and after
connection, and notebook calls that preserve large payloads, content, metadata,
and errors. Test large requests and responses through the actual stdio transport.

Verify startup against the clone before changing Codex configuration. Configure
Codex to run the clone directly; do not include `colab-codex-adapter/adapter.py`
or the compatibility launcher. Reuse a registered dependency environment and
log directory. Keep generated files outside Git.

Connect the notebook selected by the user. Read a bounded cell range through
`colab_call_tool`. Do not run training cells as a connection test. After updating
the configured command, restart the MCP server to load it. An existing process
keeps its previous code.

## Verified October 6, 2026

All 29 tests passed. Ruff lint and formatting passed. A separate live stdio
session listed all 7 notebook tools and read cells 0–1 from the selected
notebook. No notebook cells were changed or run. The local configuration points
to this clone; restarting the MCP process is required to load it.
