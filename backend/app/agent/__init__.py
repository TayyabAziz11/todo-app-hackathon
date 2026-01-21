"""
AI Agent module for Todo AI Chatbot.

This module contains:
- System prompts for agent behavior
- Intent classification for NL to tool mapping
- Agent runner for processing chat messages
"""

from app.agent.prompts import (
    TODO_AGENT_SYSTEM_PROMPT,
    get_system_prompt,
    get_system_prompt_compact,
    detect_intent,
    INTENT_PATTERNS,
)

from app.agent.intent_classifier import (
    Intent,
    ConfidenceLevel,
    IntentResult,
    classify_intent,
    extract_parameters,
    get_clarification_question,
    get_help_message,
    requires_task_id,
    is_destructive_intent,
    quick_classify,
)

from app.agent.runner import (
    Message,
    AgentResponse,
    AgentRunner,
    create_agent_runner,
)

__all__ = [
    # Prompts
    "TODO_AGENT_SYSTEM_PROMPT",
    "get_system_prompt",
    "get_system_prompt_compact",
    "detect_intent",
    "INTENT_PATTERNS",
    # Intent Classifier
    "Intent",
    "ConfidenceLevel",
    "IntentResult",
    "classify_intent",
    "extract_parameters",
    "get_clarification_question",
    "get_help_message",
    "requires_task_id",
    "is_destructive_intent",
    "quick_classify",
    # Agent Runner
    "Message",
    "AgentResponse",
    "AgentRunner",
    "create_agent_runner",
]
