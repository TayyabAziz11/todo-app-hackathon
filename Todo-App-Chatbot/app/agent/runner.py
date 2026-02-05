"""
Agent Runner - Orchestrates OpenAI Agents SDK with MCP tools.

This module runs the Todo AI agent with conversation history,
tool invocation, and structured response handling.
"""

import json
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from uuid import UUID

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """Represents a conversation message."""
    role: str  # "system", "user", "assistant", "tool"
    content: str
    tool_calls: Optional[List[Dict]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None


@dataclass
class AgentResponse:
    """Structured response from agent runner."""
    message: str
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    finish_reason: str = "stop"
    usage: Dict[str, int] = field(default_factory=dict)
    model: str = "unknown"
    intermediate_messages: List[Dict[str, Any]] = field(default_factory=list)  # NEW: All messages created during execution


class AgentRunner:
    """
    Orchestrates OpenAI agent execution with MCP tools.

    This runner:
    - Loads conversation history
    - Attaches MCP tools
    - Executes agent with OpenAI API
    - Processes tool calls via MCP server
    - Returns structured response

    All state is ephemeral - no persistence in runner.
    """

    def __init__(
        self,
        openai_api_key: str,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: Optional[int] = 1000,
    ):
        """
        Initialize the agent runner.

        Args:
            openai_api_key: OpenAI API key
            model: Model to use (gpt-4o-mini, gpt-4o, gpt-4, etc.)
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response
        """
        # Validate API key before attempting to create client
        if not openai_api_key or openai_api_key == "None" or openai_api_key.strip() == "":
            logger.error(
                "OPENAI_API_KEY is not set or invalid. "
                "Please set OPENAI_API_KEY in your backend/.env file. "
                "Get your key from: https://platform.openai.com/api-keys"
            )
            self.client = None
        else:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=openai_api_key)
                logger.info(f"OpenAI client initialized successfully with model: {model}")
            except ImportError:
                logger.error("OpenAI package not installed. Install with: pip install openai")
                self.client = None
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.client = None

        from app.mcp import get_mcp_server

        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.mcp_server = get_mcp_server()

        logger.info(f"AgentRunner initialized with model={model}")

    def run(
        self,
        user_id: UUID,
        user_message: str,
        conversation_history: Optional[List[Message]] = None,
        user_name: Optional[str] = None,
    ) -> AgentResponse:
        """
        Run the agent with a user message and conversation history.

        This is the main entry point. It:
        1. Builds message list with system prompt and history
        2. Gets MCP tools
        3. Calls OpenAI API
        4. Processes any tool calls
        5. Returns structured response

        Args:
            user_id: User ID for tool calls
            user_message: Current user input
            conversation_history: Previous messages (optional)
            user_name: Optional user name for personalization

        Returns:
            AgentResponse with message and metadata
        """
        if not self.client:
            return AgentResponse(
                message=(
                    "⚠️ AI chatbot is not configured. The OPENAI_API_KEY is missing.\n\n"
                    "Please ask your administrator to:\n"
                    "1. Get an API key from https://platform.openai.com/api-keys\n"
                    "2. Add it to the backend/.env file as OPENAI_API_KEY=sk-...\n"
                    "3. Restart the backend server"
                ),
                finish_reason="error",
            )

        logger.info(f"Running agent for user {user_id}")

        if conversation_history is None:
            conversation_history = []

        # Build message list
        messages = self._build_messages(
            user_message,
            conversation_history,
            user_name,
        )

        # Get tools from MCP server
        tools = self.mcp_server.get_tools_for_ai()
        logger.info(f"Loaded {len(tools)} MCP tools")

        # Call OpenAI API
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

            # Process response
            return self._process_response(response, user_id, messages)

        except Exception as e:
            logger.error(f"Agent run failed: {e}")
            return AgentResponse(
                message=f"I encountered an error: {str(e)}",
                finish_reason="error",
            )

    def _normalize_tool_calls(self, tool_calls: Any) -> List[Dict[str, Any]]:
        """
        Normalize tool_calls to OpenAI expected format.

        Handles two formats:
        1. Database format (from conversation history):
           [{"tool_call_id": "...", "tool_name": "...", "arguments": {...}, "result": {...}}]

        2. OpenAI format (from live responses):
           [{"id": "...", "type": "function", "function": {"name": "...", "arguments": "{...}"}}]

        Args:
            tool_calls: Tool calls in either format (list or dict)

        Returns:
            List of tool calls in OpenAI format
        """
        if not tool_calls:
            return []

        # Handle dict format (single tool_calls object from database)
        if isinstance(tool_calls, dict):
            tool_calls = [tool_calls]

        # Handle list format
        if not isinstance(tool_calls, list):
            logger.warning(f"Unexpected tool_calls type: {type(tool_calls)}")
            return []

        normalized = []
        for tc in tool_calls:
            # Skip invalid entries
            if not isinstance(tc, dict):
                continue

            # Check if already in OpenAI format
            if "id" in tc and "type" in tc and "function" in tc:
                normalized.append(tc)
                continue

            # Convert from database format to OpenAI format
            if "tool_call_id" in tc and "tool_name" in tc:
                # Database format detected
                arguments = tc.get("arguments", {})

                # Ensure arguments is a JSON string for OpenAI
                if isinstance(arguments, dict):
                    arguments_str = json.dumps(arguments)
                else:
                    arguments_str = str(arguments)

                normalized.append({
                    "id": tc["tool_call_id"],
                    "type": "function",
                    "function": {
                        "name": tc["tool_name"],
                        "arguments": arguments_str,
                    }
                })
                logger.debug(f"Normalized tool_call: {tc['tool_name']}")
            else:
                logger.warning(f"Malformed tool_call entry, skipping: {tc}")

        return normalized

    def _build_messages(
        self,
        user_message: str,
        conversation_history: List[Message],
        user_name: Optional[str],
    ) -> List[Dict[str, Any]]:
        """
        Build the message list for OpenAI API.

        Structure:
        1. System prompt (always first)
        2. Conversation history (if any)
        3. Current user message

        Args:
            user_message: Current input
            conversation_history: Previous messages
            user_name: Optional name for personalization

        Returns:
            List of message dictionaries
        """
        from app.agent.prompts import get_system_prompt

        messages = []

        # System message (always first)
        system_prompt = get_system_prompt(user_name)
        messages.append({
            "role": "system",
            "content": system_prompt,
        })

        # Add conversation history
        for msg in conversation_history:
            message_dict = {
                "role": msg.role,
                "content": msg.content or "",
            }

            # Add optional fields
            if msg.tool_calls:
                # Normalize tool_calls to OpenAI expected format
                normalized_tool_calls = self._normalize_tool_calls(msg.tool_calls)
                # Only add if normalization produced valid tool calls
                if normalized_tool_calls:
                    message_dict["tool_calls"] = normalized_tool_calls
            if msg.tool_call_id:
                message_dict["tool_call_id"] = msg.tool_call_id
            if msg.name:
                message_dict["name"] = msg.name

            messages.append(message_dict)

        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message,
        })

        logger.debug(f"Built message list with {len(messages)} messages")
        return messages

    def _process_response(
        self,
        response: Any,  # ChatCompletion type
        user_id: UUID,
        messages: List[Dict],
    ) -> AgentResponse:
        """
        Process OpenAI response and handle tool calls.

        CRITICAL PROTOCOL REQUIREMENT:
        Every assistant message with tool_calls MUST be followed by
        tool response messages (role="tool") before the next assistant message.

        This method:
        1. Checks if response contains tool_calls
        2. For each tool call:
           - Executes tool via MCP server (with error handling)
           - Appends role="tool" message with exact tool_call_id
        3. Loops until finish_reason="stop" (supports multi-step chains)
        4. Tracks ALL intermediate messages for persistence
        5. Returns final assistant response

        Args:
            response: OpenAI API response
            user_id: User ID for tool invocation
            messages: Current message list (modified in-place)

        Returns:
            AgentResponse with final message and intermediate messages
        """
        intermediate_messages = []  # Track all messages created during execution
        tool_calls_log = []
        max_iterations = 10  # Safety limit for tool chains
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            message = response.choices[0].message

            # Check if agent wants to use tools
            if hasattr(message, 'tool_calls') and message.tool_calls:
                logger.info(f"Iteration {iteration}: Processing {len(message.tool_calls)} tool calls")

                # CRITICAL: Add assistant message with tool_calls
                assistant_message = {
                    "role": "assistant",
                    "content": message.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            }
                        }
                        for tc in message.tool_calls
                    ],
                }
                messages.append(assistant_message)
                intermediate_messages.append(assistant_message)

                # CRITICAL: Execute each tool and append tool response message
                for tool_call in message.tool_calls:
                    # Execute tool with error handling
                    try:
                        tool_result = self._execute_tool_call(
                            tool_call,
                            user_id,
                        )
                        tool_calls_log.append(tool_result)

                        # Success: serialize result
                        content = json.dumps(tool_result["result"], default=str)

                    except Exception as e:
                        # ERROR: Tool execution failed - return structured error
                        logger.error(f"Tool {tool_call.function.name} failed: {e}", exc_info=True)
                        error_result = {
                            "success": False,
                            "error": "TOOL_EXECUTION_ERROR",
                            "message": str(e),
                            "tool": tool_call.function.name
                        }
                        tool_calls_log.append({
                            "tool_call_id": tool_call.id,
                            "tool_name": tool_call.function.name,
                            "arguments": json.loads(tool_call.function.arguments) if tool_call.function.arguments else {},
                            "result": error_result,
                            "success": False,
                        })
                        content = json.dumps(error_result, default=str)

                    # CRITICAL: Add tool response message
                    tool_message = {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": content,
                    }
                    messages.append(tool_message)
                    intermediate_messages.append(tool_message)

                # Call OpenAI again with tool results (supports multi-step chains)
                try:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        tools=self.mcp_server.get_tools_for_ai(),  # Include tools for potential chaining
                        tool_choice="auto",
                        temperature=self.temperature,
                        max_tokens=self.max_tokens,
                    )
                except Exception as e:
                    logger.error(f"OpenAI API call failed: {e}")
                    return AgentResponse(
                        message=f"I encountered an error calling the AI service: {str(e)}",
                        tool_calls=tool_calls_log,
                        finish_reason="error",
                        intermediate_messages=intermediate_messages,
                    )

                # Continue loop to check if more tool calls are needed
                continue

            else:
                # No tool calls - we have the final response
                logger.info(f"Final response after {iteration} iteration(s), finish_reason={response.choices[0].finish_reason}")
                break

        if iteration >= max_iterations:
            logger.warning(f"Reached max iterations ({max_iterations}) for tool chains")

        # Return structured response with ALL intermediate messages
        return AgentResponse(
            message=message.content or "",
            tool_calls=tool_calls_log,
            finish_reason=response.choices[0].finish_reason,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            model=response.model,
            intermediate_messages=intermediate_messages,  # Include for persistence
        )

    def _execute_tool_call(
        self,
        tool_call: Any,  # ChatCompletionMessageToolCall type
        user_id: UUID,
    ) -> Dict[str, Any]:
        """
        Execute a single tool call via MCP server.

        Args:
            tool_call: OpenAI tool call object
            user_id: User ID to inject into arguments

        Returns:
            Dictionary with tool call details and result
        """
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        # Inject user_id into arguments
        arguments["user_id"] = str(user_id)

        logger.info(f"Executing tool: {tool_name} with args keys: {list(arguments.keys())}")

        # Call MCP server
        result = self.mcp_server.call_tool(tool_name, arguments)

        return {
            "tool_call_id": tool_call.id,
            "tool_name": tool_name,
            "arguments": arguments,
            "result": result.result,
            "success": result.success,
        }


def create_agent_runner(
    openai_api_key: str,
    model: str = "gpt-4",
    temperature: float = 0.7,
    max_tokens: Optional[int] = 1000,
) -> AgentRunner:
    """
    Factory function to create an AgentRunner.

    Args:
        openai_api_key: OpenAI API key
        model: Model name
        temperature: Sampling temperature
        max_tokens: Max response tokens

    Returns:
        Configured AgentRunner instance
    """
    return AgentRunner(
        openai_api_key=openai_api_key,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )
