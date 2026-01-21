"""
Chat endpoint for AI-Powered Todo Chatbot - Stateless conversation management.

This module implements the POST /api/{user_id}/chat endpoint with:
- Stateless architecture (conversation history from database)
- JWT authentication and user isolation
- Conversation persistence before and after agent execution
- OpenAI Agent integration (placeholder for Phase 3)
"""

import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from sqlmodel import Session

from app.database import get_session
from app.auth.dependencies import get_current_user_id
from app.services.conversation import (
    create_conversation,
    get_conversation,
    save_message,
    get_conversation_history,
)

logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# Request/Response Schemas (T028-T029)
# =============================================================================

class ChatRequest(BaseModel):
    """
    Request schema for chat endpoint.

    Follows OpenAPI specification from contracts/chat-api.yaml
    """
    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="User's natural language message"
    )
    conversation_id: Optional[UUID] = Field(
        None,
        description="Optional conversation ID for continuing existing conversation"
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "message": "Add a task to buy groceries",
                },
                {
                    "message": "What tasks do I have pending?",
                    "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
                }
            ]
        }


class ToolCall(BaseModel):
    """Tool call transparency for debugging and trust building."""
    tool: str = Field(..., description="MCP tool name")
    arguments: Dict[str, Any] = Field(..., description="Arguments passed to tool")
    result: Dict[str, Any] = Field(..., description="Tool execution result")


class ChatResponse(BaseModel):
    """
    Response schema for chat endpoint.

    Follows OpenAPI specification from contracts/chat-api.yaml
    """
    conversation_id: UUID = Field(
        ...,
        description="Conversation identifier (client must persist for resume)"
    )
    message: str = Field(
        ...,
        description="Agent's conversational response"
    )
    tool_calls: List[ToolCall] = Field(
        default_factory=list,
        description="Array of MCP tool invocations (empty if no tools called)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                "message": "I've created the task 'Buy groceries' for you.",
                "tool_calls": [
                    {
                        "tool": "add_task",
                        "arguments": {
                            "user_id": "user_abc123",
                            "title": "Buy groceries",
                            "description": ""
                        },
                        "result": {
                            "success": True,
                            "task": {
                                "id": 42,
                                "title": "Buy groceries",
                                "completed": False
                            }
                        }
                    }
                ]
            }
        }


# =============================================================================
# Chat Endpoint (T030-T036)
# =============================================================================

@router.post("/{user_id}/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def send_chat_message(
    user_id: str,
    request: ChatRequest,
    session: Session = Depends(get_session),
    authenticated_user_id: str = Depends(get_current_user_id)
) -> ChatResponse:
    """
    Send a message to the AI chatbot and receive a response.

    **Stateless Operation Flow:**
    1. Validate JWT token and extract user_id
    2. Verify path user_id matches authenticated user_id (authorization)
    3. Load conversation history from database (if conversation_id provided)
    4. Create new conversation if none provided
    5. Persist user message to database
    6. Run OpenAI Agent with formatted conversation history (PLACEHOLDER for now)
    7. Persist assistant response to database
    8. Return conversation_id and assistant message

    **Stateless Architecture:**
    - NO in-memory state between requests
    - Conversation history loaded ONLY from database
    - Agent reconstructed fresh per request
    - Any server instance can handle any request
    - Conversation resumes after server restart

    **Security:**
    - Requires valid JWT token in Authorization header
    - Users can only access their own conversations
    - Path user_id must match JWT user_id

    **Error Responses:**
    - 401 Unauthorized: Missing, invalid, or expired JWT token
    - 403 Forbidden: Authenticated user_id doesn't match path user_id
    - 404 Not Found: Conversation not found or doesn't belong to user
    - 500 Internal Server Error: Database or agent execution failure
    """
    # T034: Error handling - Authorization check
    if user_id != authenticated_user_id:
        logger.warning(
            f"Authorization failed: path user_id={user_id} != authenticated={authenticated_user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="user_id in path does not match authenticated user"
        )

    try:
        # T035: Request logging
        logger.info(
            f"Chat request from user={authenticated_user_id}, "
            f"conversation_id={request.conversation_id}, "
            f"message_length={len(request.message)}"
        )

        # T031: Load or create conversation
        conversation = None
        if request.conversation_id:
            # Continue existing conversation
            conversation = get_conversation(
                db=session,
                conversation_id=request.conversation_id,
                user_id=UUID(authenticated_user_id)
            )

            if not conversation:
                logger.warning(
                    f"Conversation {request.conversation_id} not found for user {authenticated_user_id}"
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="The conversation_id does not exist or does not belong to this user"
                )

            logger.debug(f"Loaded existing conversation {conversation.id}")
        else:
            # Create new conversation
            conversation = create_conversation(
                db=session,
                user_id=UUID(authenticated_user_id),
                title=None  # Could auto-generate from first message in future
            )
            logger.info(f"Created new conversation {conversation.id}")

        # T031: Load conversation history (if continuing conversation)
        conversation_messages = []
        if request.conversation_id:
            conversation_messages = get_conversation_history(
                db=session,
                conversation_id=conversation.id,
                user_id=UUID(authenticated_user_id),
                limit=50  # Load last 50 messages for agent context
            )
            logger.debug(
                f"Loaded {len(conversation_messages)} messages for conversation {conversation.id}"
            )

        # T032: Persist user message BEFORE agent execution
        user_message = save_message(
            db=session,
            conversation_id=conversation.id,
            user_id=UUID(authenticated_user_id),
            role="user",
            content=request.message,
            tool_calls=None
        )
        logger.debug(f"Persisted user message {user_message.id}")

        # T050: Run OpenAI Agent with conversation history
        try:
            from app.agent.runner import AgentRunner, Message as AgentMessage
            from app.config import settings

            # Initialize agent runner (stateless - fresh per request)
            agent_runner = AgentRunner(
                openai_api_key=settings.OPENAI_API_KEY,
                model="gpt-4",
                temperature=0.7,
                max_tokens=1000
            )

            # Format conversation history for agent
            formatted_history = [
                AgentMessage(
                    role=msg.role,
                    content=msg.content,
                    tool_calls=msg.tool_calls if hasattr(msg, 'tool_calls') else None
                )
                for msg in conversation_messages
            ]

            # Run agent with user message and history
            agent_response = agent_runner.run(
                user_id=UUID(authenticated_user_id),
                user_message=request.message,
                conversation_history=formatted_history,
                user_name=None  # Could get from user profile in future
            )

            # Extract response
            assistant_content = agent_response.message
            tool_calls_data = agent_response.tool_calls

            logger.info(
                f"Agent executed successfully, "
                f"tool_calls={len(tool_calls_data)}, "
                f"finish_reason={agent_response.finish_reason}"
            )

        except ImportError as e:
            logger.error(f"OpenAI SDK not installed: {e}")
            assistant_content = (
                "OpenAI SDK is not available. Please install it: pip install openai"
            )
            tool_calls_data = []
        except Exception as e:
            logger.error(f"Agent execution failed: {e}", exc_info=True)
            assistant_content = (
                "I encountered an issue processing your request. "
                "Please try again or rephrase your message."
            )
            tool_calls_data = []

        # T033: Persist assistant response
        assistant_message = save_message(
            db=session,
            conversation_id=conversation.id,
            user_id=UUID(authenticated_user_id),
            role="assistant",
            content=assistant_content,
            tool_calls=tool_calls_data if tool_calls_data else None
        )
        logger.debug(f"Persisted assistant message {assistant_message.id}")

        # T035: Log successful completion
        logger.info(
            f"Chat request completed for conversation {conversation.id}, "
            f"user={authenticated_user_id}"
        )

        # Return response following chat-api.yaml contract
        return ChatResponse(
            conversation_id=conversation.id,
            message=assistant_content,
            tool_calls=tool_calls_data
        )

    except HTTPException:
        # Re-raise HTTP exceptions (401, 403, 404)
        raise

    except Exception as e:
        # T034: Error handling - Catch-all for database and other errors
        logger.error(
            f"Chat endpoint error for user {authenticated_user_id}: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
