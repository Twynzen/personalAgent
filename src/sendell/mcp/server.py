"""
Sendell MCP Server.

Exposes system monitoring and control tools via Model Context Protocol.

The server runs on stdio transport for local communication with the LangGraph agent.
"""

import asyncio
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from sendell.config import get_settings
from sendell.mcp.tools.conversation import respond_to_user
from sendell.mcp.tools.monitoring import get_active_window, get_system_health
from sendell.mcp.tools.process import list_top_processes, open_application
from sendell.utils.logger import get_logger

logger = get_logger(__name__)


class SendellMCPServer:
    """
    Sendell MCP Server.

    Exposes 5 core tools:
    1. get_system_health - System metrics
    2. get_active_window - Active window info
    3. list_top_processes - Top processes by resource
    4. open_application - Open apps
    5. respond_to_user - Agent communication
    """

    def __init__(self):
        """Initialize MCP server"""
        self.settings = get_settings()
        self.server = Server("sendell")

        # Register tools
        self._register_tools()

        logger.info("Sendell MCP Server initialized")

    def _register_tools(self):
        """Register all MCP tools"""

        # Tool 1: get_system_health
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools"""
            return [
                Tool(
                    name="get_system_health",
                    description=(
                        "Get current system health metrics including CPU, RAM, and disk usage. "
                        "Returns percentages and detects if any thresholds are exceeded. "
                        "Read-only operation, safe to call frequently."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                ),
                Tool(
                    name="get_active_window",
                    description=(
                        "Get information about the currently active window. "
                        "Returns window title, process name, and PID. "
                        "Useful for understanding user context. "
                        "Respects privacy settings (blocked apps)."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                ),
                Tool(
                    name="list_top_processes",
                    description=(
                        "List top N processes by resource usage (CPU or memory). "
                        "Useful for identifying resource hogs and potential issues. "
                        "Returns process name, PID, CPU%, memory usage."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "n": {
                                "type": "integer",
                                "description": "Number of processes to return (1-100)",
                                "default": 10,
                            },
                            "sort_by": {
                                "type": "string",
                                "description": "Sort by 'memory' or 'cpu'",
                                "enum": ["memory", "cpu"],
                                "default": "memory",
                            },
                        },
                        "required": [],
                    },
                ),
                Tool(
                    name="open_application",
                    description=(
                        "Open an application by name or path. "
                        "Supports common apps like 'notepad', 'chrome', 'vscode', etc. "
                        "Requires L3+ autonomy level. "
                        "Respects blocked apps from privacy settings."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "app_name": {
                                "type": "string",
                                "description": "Application name or path to open",
                            },
                            "args": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Optional command-line arguments",
                                "default": None,
                            },
                        },
                        "required": ["app_name"],
                    },
                ),
                Tool(
                    name="respond_to_user",
                    description=(
                        "Send a message to the user. "
                        "Use this to communicate proactively about findings, suggestions, or requests. "
                        "Set requires_approval=true if you need user confirmation for an action."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "Message to send to user",
                            },
                            "requires_approval": {
                                "type": "boolean",
                                "description": "If true, message requests user action/approval",
                                "default": False,
                            },
                        },
                        "required": ["message"],
                    },
                ),
                Tool(
                    name="show_brain",
                    description=(
                        "Open the Sendell Brain GUI interface. "
                        "This allows Daniel to view and manage memory, prompts, and available tools. "
                        "Use when Daniel asks to see memory, brain, or configure settings."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
            """Handle tool calls"""
            logger.info(f"Tool called: {name} with args: {arguments}")

            try:
                # Route to appropriate tool
                if name == "get_system_health":
                    result = get_system_health()
                elif name == "get_active_window":
                    result = get_active_window()
                elif name == "list_top_processes":
                    n = arguments.get("n", 10)
                    sort_by = arguments.get("sort_by", "memory")
                    result = list_top_processes(n=n, sort_by=sort_by)
                elif name == "open_application":
                    app_name = arguments.get("app_name")
                    args = arguments.get("args")
                    result = open_application(app_name=app_name, args=args)
                elif name == "respond_to_user":
                    message = arguments.get("message")
                    requires_approval = arguments.get("requires_approval", False)
                    result = respond_to_user(message=message, requires_approval=requires_approval)
                elif name == "show_brain":
                    # Import here to avoid circular dependency
                    import threading
                    from sendell.agent.brain_gui import show_brain as show_brain_gui

                    # Run GUI in thread
                    gui_thread = threading.Thread(target=show_brain_gui)
                    gui_thread.daemon = True
                    gui_thread.start()

                    result = {
                        "success": True,
                        "message": "Brain GUI opened"
                    }
                else:
                    raise ValueError(f"Unknown tool: {name}")

                # Return result as TextContent
                import json

                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            except Exception as e:
                logger.error(f"Tool execution failed: {e}")
                error_result = {"error": str(e), "tool": name, "arguments": arguments}
                import json

                return [TextContent(type="text", text=json.dumps(error_result, indent=2))]

    async def run(self):
        """Run the MCP server on stdio"""
        logger.info("Starting Sendell MCP Server on stdio transport")

        async with stdio_server() as (read_stream, write_stream):
            logger.info("MCP Server connected via stdio")
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options(),
            )


def run_server():
    """
    Run the Sendell MCP server.

    This is the entry point for running the MCP server standalone.
    """
    try:
        server = SendellMCPServer()
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("MCP Server shutting down")
    except Exception as e:
        logger.error(f"MCP Server error: {e}")
        raise


if __name__ == "__main__":
    run_server()
