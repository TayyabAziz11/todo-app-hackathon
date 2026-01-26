"""
MCP Server - Model Context Protocol server for Todo AI Chatbot.

This module implements the MCP server that exposes task management tools
to AI agents. The server is stateless and uses PostgreSQL for persistence.

Usage:
    from app.mcp.server import MCPToolServer

    server = MCPToolServer()
    tools = server.list_tools()
    result = server.call_tool("add_task", {"user_id": "...", "title": "..."})
"""

import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ValidationError

from app.mcp.schemas import get_tool_definitions, MCPToolDefinition
from app.mcp.tools import invoke_tool, TOOL_HANDLERS

logger = logging.getLogger(__name__)


# =============================================================================
# MCP Protocol Types
# =============================================================================

class MCPToolCall(BaseModel):
    """Represents a tool call request from an AI agent."""

    name: str
    arguments: Dict[str, Any]


class MCPToolResult(BaseModel):
    """Represents the result of a tool call."""

    tool_name: str
    success: bool
    result: Dict[str, Any]
    error: Optional[str] = None


class MCPError(BaseModel):
    """Represents an MCP protocol error."""

    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


# =============================================================================
# MCP Tool Server
# =============================================================================

class MCPToolServer:
    """
    MCP Server for Todo AI Chatbot task management.

    This server exposes five stateless tools:
    - add_task: Create a new task
    - list_tasks: List tasks with filtering
    - update_task: Modify task properties
    - complete_task: Mark task complete/incomplete
    - delete_task: Remove a task

    All tools are stateless and persist data via SQLModel + PostgreSQL.

    Example:
        server = MCPToolServer()

        # List available tools
        tools = server.list_tools()

        # Call a tool
        result = server.call_tool("add_task", {
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "title": "Buy groceries"
        })
    """

    def __init__(self):
        """Initialize the MCP server."""
        self._tool_definitions = {t.name: t for t in get_tool_definitions()}
        logger.info(f"MCPToolServer initialized with {len(self._tool_definitions)} tools")

    # -------------------------------------------------------------------------
    # Tool Discovery
    # -------------------------------------------------------------------------

    def list_tools(self) -> List[MCPToolDefinition]:
        """
        List all available tools with their schemas.

        Returns:
            List of MCPToolDefinition objects describing available tools
        """
        return list(self._tool_definitions.values())

    def get_tool(self, name: str) -> Optional[MCPToolDefinition]:
        """
        Get a specific tool definition by name.

        Args:
            name: Tool name (e.g., "add_task")

        Returns:
            MCPToolDefinition if found, None otherwise
        """
        return self._tool_definitions.get(name)

    def get_tools_for_ai(self) -> List[Dict[str, Any]]:
        """
        Get tool definitions formatted for AI model consumption.

        Returns a list of tools in the format expected by most AI SDKs
        (OpenAI, Anthropic, etc.)

        Returns:
            List of tool definitions as dictionaries
        """
        tools = []
        for tool_def in self._tool_definitions.values():
            # Use exclude_none=True to remove null values from the schema
            # OpenAI API rejects schemas with null values (e.g., "minimum": null)
            tools.append({
                "type": "function",
                "function": {
                    "name": tool_def.name,
                    "description": tool_def.description,
                    "parameters": tool_def.inputSchema.model_dump(exclude_none=True),
                }
            })
        return tools

    # -------------------------------------------------------------------------
    # Tool Invocation
    # -------------------------------------------------------------------------

    def call_tool(
        self,
        name: str,
        arguments: Dict[str, Any]
    ) -> MCPToolResult:
        """
        Call a tool with the given arguments.

        This is the main entry point for tool invocation. It validates
        the tool name and arguments, then dispatches to the appropriate
        tool handler.

        Args:
            name: Tool name (e.g., "add_task")
            arguments: Dictionary of arguments for the tool

        Returns:
            MCPToolResult with success status and result data
        """
        logger.info(f"Tool call: {name} with {len(arguments)} arguments")

        # Check if tool exists
        if name not in TOOL_HANDLERS:
            logger.warning(f"Unknown tool requested: {name}")
            return MCPToolResult(
                tool_name=name,
                success=False,
                result={},
                error=f"UNKNOWN_TOOL: Tool '{name}' does not exist. Available tools: {list(TOOL_HANDLERS.keys())}",
            )

        try:
            # Invoke the tool
            result = invoke_tool(name, arguments)

            logger.info(f"Tool {name} completed successfully")
            return MCPToolResult(
                tool_name=name,
                success=result.get("success", True),
                result=result,
                error=result.get("error"),
            )

        except ValidationError as e:
            logger.warning(f"Validation error for tool {name}: {e}")
            return MCPToolResult(
                tool_name=name,
                success=False,
                result={},
                error=f"VALIDATION_ERROR: {str(e)}",
            )

        except Exception as e:
            logger.error(f"Tool {name} failed with error: {e}")
            return MCPToolResult(
                tool_name=name,
                success=False,
                result={},
                error=f"INTERNAL_ERROR: {str(e)}",
            )

    def call_tool_raw(
        self,
        name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call a tool and return the raw result dictionary.

        This is a convenience method for cases where you just want
        the result data without the MCPToolResult wrapper.

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            Dictionary result from the tool

        Raises:
            ValueError: If tool doesn't exist
            ValidationError: If arguments are invalid
        """
        return invoke_tool(name, arguments)

    # -------------------------------------------------------------------------
    # Batch Operations
    # -------------------------------------------------------------------------

    def call_tools_batch(
        self,
        tool_calls: List[MCPToolCall]
    ) -> List[MCPToolResult]:
        """
        Call multiple tools in sequence.

        Note: Tools are called sequentially, not in parallel.
        For parallel execution, implement at a higher level.

        Args:
            tool_calls: List of MCPToolCall objects

        Returns:
            List of MCPToolResult objects in the same order
        """
        results = []
        for call in tool_calls:
            result = self.call_tool(call.name, call.arguments)
            results.append(result)
        return results

    # -------------------------------------------------------------------------
    # Utility Methods
    # -------------------------------------------------------------------------

    def validate_user_id(self, user_id: str) -> bool:
        """
        Validate that a user_id is a valid UUID string.

        Args:
            user_id: String to validate

        Returns:
            True if valid UUID, False otherwise
        """
        try:
            UUID(user_id)
            return True
        except (ValueError, TypeError):
            return False

    def get_server_info(self) -> Dict[str, Any]:
        """
        Get server metadata.

        Returns:
            Dictionary with server information
        """
        return {
            "name": "todo-mcp-server",
            "version": "1.0.0",
            "protocol_version": "2024-11-05",
            "capabilities": {
                "tools": True,
                "resources": False,
                "prompts": False,
            },
            "tools_count": len(self._tool_definitions),
            "tool_names": list(self._tool_definitions.keys()),
        }


# =============================================================================
# Singleton Instance
# =============================================================================

# Global server instance (lazy initialization)
_server_instance: Optional[MCPToolServer] = None


def get_mcp_server() -> MCPToolServer:
    """
    Get the singleton MCP server instance.

    Returns:
        MCPToolServer instance
    """
    global _server_instance
    if _server_instance is None:
        _server_instance = MCPToolServer()
    return _server_instance


# =============================================================================
# FastAPI Integration
# =============================================================================

def mcp_tool_endpoint(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Endpoint handler for MCP tool calls.

    This can be used to create FastAPI endpoints for each tool.

    Args:
        tool_name: Name of the tool
        arguments: Tool arguments

    Returns:
        Tool result as dictionary
    """
    server = get_mcp_server()
    result = server.call_tool(tool_name, arguments)
    return result.model_dump()
