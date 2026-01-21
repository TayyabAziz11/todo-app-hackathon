# Skill: configure-agent-runner

## 1. Skill Name
`configure-agent-runner`

## 2. Purpose
Configure the OpenAI Agents SDK Runner to orchestrate the Todo AI Chatbot agent with MCP tools, conversation history, and structured outputs. The runner must attach MCP tools, process multi-turn conversations, capture tool calls and responses, and return structured outputs while maintaining statelessness and avoiding direct database access.

## 3. Applicable Agents
- **chat-api-orchestrator** (primary)
- todo-ai-agent-designer (design alignment)
- mcp-tool-architect (tool integration)
- mcp-compliance-validator (validation)
- phase3-qa-demo (testing)

## 4. Inputs
- **System Prompt**: From `define-agent-system-prompt` skill
- **MCP Tools**: From `implement-mcp-server` skill
- **Conversation History**: Previous messages from database
- **User Message**: Current user input
- **User ID**: For tool call authentication
- **OpenAI API Key**: For API access

## 5. Outputs
- **Agent Runner Class**: Orchestrates agent execution
- **Run Configuration**: OpenAI SDK parameters
- **Tool Call Handler**: Processes MCP tool invocations
- **Response Formatter**: Structures agent output
- **Error Handler**: Graceful failure management
- **Conversation Tracker**: Message history management

## 6. Scope & Boundaries

### In Scope
- OpenAI Agents SDK integration
- MCP tool attachment and invocation
- Conversation history management
- Tool call capture and logging
- Response formatting and validation
- Error handling and retries
- Streaming response support (optional)

### Out of Scope
- Direct database queries (tools handle this)
- Conversation persistence (chat API handles this)
- Authentication/authorization (API layer handles this)
- Rate limiting (API gateway handles this)
- Model fine-tuning or training
- Custom model deployment

## 7. Reusability Notes
- **Phase 3**: Core agent runner for chatbot
- **Phase 4**: Same runner, different tools
- **Phase 5**: Extend with streaming, multi-agent
- **Cross-Project**: OpenAI SDK patterns reusable

### Reusability Mechanisms
- Runner configurable with different prompts and tools
- Model selection parameterizable
- Tool invocation abstracted
- Response format standardized

## 8. Dependencies

### Upstream Dependencies
- `define-agent-system-prompt` (prompt text)
- `implement-mcp-server` (tool server)
- `map-intents-to-tools` (intent understanding)
- OpenAI API key (external)

### Downstream Dependencies
- `chat-api-orchestrator` (uses runner)
- `conversation-persistence` (stores results)

### Parallel Dependencies
- Database session (for conversation history)

## 9. Quality Expectations

### Statelessness
- No agent-side memory persistence
- Fresh agent run per conversation turn
- Conversation history from database only
- No cached state between requests

### Correctness
- All tool calls routed to MCP server
- Responses validated before returning
- Errors caught and structured
- Tool results properly formatted

### Robustness
- API failures handled gracefully
- Tool call failures don't crash agent
- Timeout handling for long operations
- Retry logic for transient failures

### Testability
- Runner testable with mock OpenAI client
- Tool calls verifiable
- Response format validatable
- Error paths exercisable

## 10. Example Usage (Complete Agent Runner)

---

### Agent Runner Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         ChatAPI Endpoint                             │
│                    POST /api/{user_id}/chat                          │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                │ user_message, conversation_id
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        AgentRunner                                   │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │ 1. Load conversation history from database                      ││
│  │ 2. Build message list: [system, ...history, user]              ││
│  │ 3. Get tools from MCP server                                    ││
│  │ 4. Call OpenAI with tools                                       ││
│  │ 5. Process tool calls if any                                    ││
│  │ 6. Return final response                                        ││
│  └─────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┴───────────────┐
                │                               │
                ▼                               ▼
┌─────────────────────────────┐   ┌─────────────────────────────┐
│     OpenAI API              │   │     MCP Server              │
│  gpt-4 with function calling│   │  Tool invocation            │
└─────────────────────────────┘   └─────────────────────────────┘
```

---

### Implementation: Agent Runner Class

**File**: `backend/app/agent/runner.py`

```python
"""
Agent Runner - Orchestrates OpenAI Agents SDK with MCP tools.

This module runs the Todo AI agent with conversation history,
tool invocation, and structured response handling.
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from uuid import UUID

from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessage
from openai.types.chat.chat_completion_message_tool_call import ChatCompletionMessageToolCall

from app.agent.prompts import get_system_prompt
from app.mcp import get_mcp_server

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
    tool_calls: List[Dict[str, Any]]
    finish_reason: str
    usage: Dict[str, int]
    model: str


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
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: Optional[int] = 1000,
    ):
        """
        Initialize the agent runner.

        Args:
            openai_api_key: OpenAI API key
            model: Model to use (gpt-4, gpt-3.5-turbo, etc.)
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response
        """
        self.client = OpenAI(api_key=openai_api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.mcp_server = get_mcp_server()

        logger.info(f"AgentRunner initialized with model={model}")

    def run(
        self,
        user_id: UUID,
        user_message: str,
        conversation_history: List[Message],
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
            conversation_history: Previous messages
            user_name: Optional user name for personalization

        Returns:
            AgentResponse with message and metadata
        """
        logger.info(f"Running agent for user {user_id}")

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
            raise

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
                "content": msg.content,
            }

            # Add optional fields
            if msg.tool_calls:
                message_dict["tool_calls"] = msg.tool_calls
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
        response: ChatCompletion,
        user_id: UUID,
        messages: List[Dict],
    ) -> AgentResponse:
        """
        Process OpenAI response and handle tool calls.

        If response contains tool calls:
        1. Execute each tool via MCP server
        2. Add tool results to messages
        3. Call OpenAI again for final response

        Args:
            response: OpenAI API response
            user_id: User ID for tool invocation
            messages: Current message list

        Returns:
            AgentResponse with final message
        """
        message = response.choices[0].message
        tool_calls_log = []

        # Check if agent wants to use tools
        if message.tool_calls:
            logger.info(f"Processing {len(message.tool_calls)} tool calls")

            # Add assistant message with tool calls
            messages.append({
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
            })

            # Execute each tool call
            for tool_call in message.tool_calls:
                tool_result = self._execute_tool_call(
                    tool_call,
                    user_id,
                )
                tool_calls_log.append(tool_result)

                # Add tool result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_call.function.name,
                    "content": str(tool_result["result"]),
                })

            # Call OpenAI again with tool results
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            message = response.choices[0].message

        # Return structured response
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
        )

    def _execute_tool_call(
        self,
        tool_call: ChatCompletionMessageToolCall,
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
        import json

        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        # Inject user_id into arguments
        arguments["user_id"] = str(user_id)

        logger.info(f"Executing tool: {tool_name} with args: {arguments}")

        # Call MCP server
        result = self.mcp_server.call_tool(tool_name, arguments)

        return {
            "tool_call_id": tool_call.id,
            "tool_name": tool_name,
            "arguments": arguments,
            "result": result.result,
            "success": result.success,
        }


# Factory function for easy instantiation
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
```

---

### Integration: Chat API Endpoint

**File**: `backend/app/routers/chat.py`

```python
"""
Chat API endpoint using AgentRunner.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from uuid import UUID
from typing import Optional

from app.database import get_session
from app.agent.runner import create_agent_runner, Message
from app.config import settings

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/{user_id}/chat")
async def chat(
    user_id: UUID,
    message: str,
    conversation_id: Optional[str] = None,
    session: Session = Depends(get_session),
):
    """
    Process a chat message for a user.

    Args:
        user_id: The authenticated user's ID
        message: User's input message
        conversation_id: Optional conversation ID for history
        session: Database session

    Returns:
        Agent response with message and metadata
    """
    # Load conversation history (if conversation_id provided)
    conversation_history = []
    if conversation_id:
        conversation_history = load_conversation_history(
            session,
            user_id,
            conversation_id,
        )

    # Create agent runner
    runner = create_agent_runner(
        openai_api_key=settings.OPENAI_API_KEY,
        model="gpt-4",
        temperature=0.7,
    )

    # Run agent
    try:
        response = runner.run(
            user_id=user_id,
            user_message=message,
            conversation_history=conversation_history,
        )

        # Save conversation to database
        save_conversation_turn(
            session,
            user_id,
            conversation_id,
            message,
            response.message,
            response.tool_calls,
        )

        return {
            "conversation_id": conversation_id or "new",
            "message": response.message,
            "tool_calls": response.tool_calls,
            "usage": response.usage,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

### Statelessness Verification

| Requirement | Implementation |
|-------------|----------------|
| No agent memory | Fresh `AgentRunner` per request or configured once |
| Conversation from DB | `load_conversation_history()` reads from database |
| No cached state | Messages built fresh each run |
| MCP tools stateless | Tools create fresh DB sessions |
| OpenAI API stateless | API calls are stateless by design |

---

### Configuration Options

**Model Selection**:
```python
# Development (faster, cheaper)
runner = create_agent_runner(
    openai_api_key=api_key,
    model="gpt-3.5-turbo",
    temperature=0.7,
)

# Production (better quality)
runner = create_agent_runner(
    openai_api_key=api_key,
    model="gpt-4",
    temperature=0.5,
)

# Advanced (best quality, slower)
runner = create_agent_runner(
    openai_api_key=api_key,
    model="gpt-4-turbo",
    temperature=0.3,
    max_tokens=2000,
)
```

---

### Error Handling

```python
try:
    response = runner.run(user_id, message, history)
except OpenAIError as e:
    # OpenAI API failure
    logger.error(f"OpenAI API error: {e}")
    return fallback_response("Sorry, I'm having trouble right now.")
except MCPToolError as e:
    # Tool execution failure
    logger.error(f"Tool execution failed: {e}")
    return fallback_response("I couldn't complete that action.")
except Exception as e:
    # Unexpected error
    logger.error(f"Unexpected error: {e}")
    return fallback_response("An unexpected error occurred.")
```

---

### Testing the Agent Runner

```python
import pytest
from app.agent.runner import AgentRunner, Message
from uuid import uuid4

def test_agent_runner_initialization():
    """Runner initializes with correct parameters."""
    runner = AgentRunner(
        openai_api_key="test-key",
        model="gpt-4",
    )
    assert runner.model == "gpt-4"

def test_message_building():
    """Messages built correctly with history."""
    runner = AgentRunner(openai_api_key="test-key")
    history = [
        Message(role="user", content="Hello"),
        Message(role="assistant", content="Hi there!"),
    ]
    messages = runner._build_messages("How are you?", history, None)

    assert len(messages) == 4  # system + 2 history + current
    assert messages[0]["role"] == "system"
    assert messages[-1]["content"] == "How are you?"

def test_tool_call_execution(mock_mcp_server):
    """Tool calls executed via MCP server."""
    runner = AgentRunner(openai_api_key="test-key")
    tool_call = MockToolCall(
        id="call_123",
        function=MockFunction(
            name="add_task",
            arguments='{"title": "Test"}',
        ),
    )

    result = runner._execute_tool_call(tool_call, uuid4())
    assert result["success"] is True
    assert result["tool_name"] == "add_task"
```

---

### Conversation Flow Example

```
User: "Add a task to buy milk"

AgentRunner:
  1. Load conversation: []
  2. Build messages: [system, user]
  3. Get tools: [add_task, list_tasks, ...]
  4. Call OpenAI → tool_call: add_task(title="buy milk")
  5. Execute via MCP → {success: true, task: {...}}
  6. Call OpenAI again → "I've added 'buy milk' to your task list. (Task #1)"
  7. Return response

Database saves:
  - User message: "Add a task to buy milk"
  - Assistant message: "I've added 'buy milk' to your task list. (Task #1)"
  - Tool calls: [{tool: "add_task", args: {...}, result: {...}}]
```

---

### Environment Configuration

**File**: `backend/app/config.py`

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # OpenAI Configuration
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_TEMPERATURE: float = 0.7
    OPENAI_MAX_TOKENS: int = 1000

    # Other settings...

    class Config:
        env_file = ".env"

settings = Settings()
```

**File**: `backend/.env`

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-...your-key...
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=1000
```

---

## Metadata
- **Version**: 1.0.0
- **Phase Introduced**: Phase 3
- **Last Updated**: 2026-01-19
- **Skill Type**: Implementation
- **Execution Surface**: Agent (chat-api-orchestrator)
- **Prerequisite Skills**: `define-agent-system-prompt`, `implement-mcp-server`
