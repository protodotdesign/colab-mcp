"""Exercise the permanent tools through MCP, including the stdio transport."""

import asyncio
from pathlib import Path
import sys
from types import SimpleNamespace

from colab_mcp.session import ColabProxyClient, notebook_tools
from fastmcp import Client, FastMCP
from fastmcp.client.transports import PythonStdioTransport
from fastmcp.dependencies import CurrentContext
from fastmcp.exceptions import ToolError
from fastmcp.server.context import Context
from fastmcp.server.middleware.tool_injection import ToolInjectionMiddleware
from fastmcp.tools.tool import ToolResult
from mcp.types import ImageContent, TextContent
import pytest


def build_test_server():
    notebook = FastMCP("SyntheticNotebook")

    @notebook.tool
    async def echo(payload: str, ctx: Context = CurrentContext()) -> ToolResult:
        await ctx.report_progress(1, 1, "echo complete")
        return ToolResult(
            content=[
                TextContent(type="text", text=payload),
                ImageContent(
                    type="image",
                    mimeType="image/png",
                    data="iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jG1kAAAAASUVORK5CYII=",
                ),
            ],
            structured_content={"echo": payload},
            meta={"source": "synthetic"},
        )

    @notebook.tool
    def fail():
        raise ToolError("synthetic failure")

    proxy = ColabProxyClient(SimpleNamespace(connection_live=asyncio.Event()))
    proxy.proxy_mcp_client = Client(notebook)
    server = FastMCP("NotebookToolTest")
    server.add_middleware(ToolInjectionMiddleware(notebook_tools(proxy)))

    @server.tool
    def connect_test_notebook():
        proxy.wss.connection_live.set()
        return True

    return server


@pytest.mark.asyncio
@pytest.mark.parametrize("stdio", [False, True])
async def test_discovery_and_forwarding(stdio):
    transport = (
        PythonStdioTransport(str(Path(__file__).resolve()), python_cmd=sys.executable)
        if stdio
        else build_test_server()
    )
    progress = []

    async def collect_progress(value, total, message):
        progress.append((value, total, message))

    async with Client(transport, progress_handler=collect_progress) as client:
        initial = await client.list_tools()
        assert {"colab_list_tools", "colab_call_tool"} <= {t.name for t in initial}
        before = await client.call_tool_mcp("colab_list_tools", {})
        assert before.structuredContent == {"tools": []}
        disconnected = await client.call_tool_mcp(
            "colab_call_tool", {"name": "echo", "arguments": {"payload": "x"}}
        )
        assert disconnected.isError
        await client.call_tool("connect_test_notebook")
        after = await client.call_tool_mcp("colab_list_tools", {})
        tools = after.structuredContent["tools"]
        assert {t["name"] for t in tools} == {"echo", "fail"}
        assert tools[0]["inputSchema"]["properties"]["payload"]["type"] == "string"

        payload = "x" * (256 * 1024)
        result = await client.call_tool_mcp(
            "colab_call_tool", {"name": "echo", "arguments": {"payload": payload}}
        )
        assert not result.isError
        assert result.content[0].text == payload
        assert result.content[1].type == "image"
        assert result.structuredContent == {"echo": payload}
        assert result.meta == {"source": "synthetic"}
        assert progress == [(1.0, 1.0, "echo complete")]

        error = await client.call_tool_mcp("colab_call_tool", {"name": "fail"})
        assert error.isError
        assert "synthetic failure" in error.content[0].text
        assert (
            await client.call_tool_mcp("colab_list_tools", {})
        ).structuredContent == after.structuredContent


if __name__ == "__main__":
    build_test_server().run()
