"""
Intent classification for natural language to MCP tool mapping.

This module classifies user messages into intents and extracts
parameters for MCP tool invocation.
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any


class Intent(Enum):
    """User intent categories for task management."""
    CREATE_TASK = "create_task"
    VIEW_TASKS = "view_tasks"
    EDIT_TASK = "edit_task"
    COMPLETE_TASK = "complete_task"
    DELETE_TASK = "delete_task"
    UNKNOWN = "unknown"


class ConfidenceLevel(Enum):
    """Confidence levels for intent classification."""
    HIGH = "high"           # 0.7+ - Execute immediately
    MEDIUM = "medium"       # 0.5-0.69 - Execute with confirmation
    LOW = "low"             # 0.3-0.49 - Ask for clarification
    UNCERTAIN = "uncertain" # <0.3 - Show help message


@dataclass
class IntentResult:
    """Result of intent classification."""
    intent: Intent
    confidence: float
    confidence_level: ConfidenceLevel
    tool_name: Optional[str]
    extracted_params: Dict[str, Any] = field(default_factory=dict)
    requires_clarification: bool = False
    clarification_question: Optional[str] = None


# Intent patterns with confidence weights
# Each pattern: (regex_pattern, base_confidence)
INTENT_PATTERNS: Dict[Intent, List[tuple]] = {
    Intent.CREATE_TASK: [
        # Direct commands (high confidence)
        (r'\b(add|create|new|make)\b.*\b(task|todo|item)\b', 0.9),
        (r'\bnew task\b', 0.95),
        (r'\badd\b.*\bto\b.*\blist\b', 0.85),
        (r'\bput\b.*\bon\b.*\blist\b', 0.85),
        # Implicit requests (medium confidence)
        (r'\b(remind|remember)\b.*\bto\b', 0.7),
        (r"\bi (need|have|got|gotta) to\b", 0.65),
        (r"\bdon'?t (let me )?forget\b", 0.7),
        (r'\bi should\b', 0.45),
    ],
    Intent.VIEW_TASKS: [
        # Direct queries (high confidence)
        (r'\b(show|list|view|display|see)\b.*\b(task|todo|list|all)\b', 0.9),
        (r'\bwhat\b.*\b(task|todo|do|have)\b', 0.85),
        (r'\bmy (tasks?|todos?|list)\b', 0.8),
        # Filtered queries (high confidence)
        (r'\b(show|list|view)\b.*\b(completed?|done|finished)\b', 0.9),
        (r'\b(show|list|view)\b.*\b(incomplete|pending|remaining)\b', 0.9),
        (r'\bcompleted?\s+(tasks?|todos?)\b', 0.9),
        (r'\bincomplete\s+(tasks?|todos?)\b', 0.9),
        # Implicit queries (medium confidence)
        (r'\b(anything|something)\b.*(pending|left|to do)\b', 0.7),
        (r"\bwhat'?s on my\b", 0.75),
        (r"\bwhat do i (have|need) to\b", 0.8),
    ],
    Intent.EDIT_TASK: [
        # Direct commands (high confidence)
        (r'\b(update|change|edit|modify|rename|fix)\b.*\btask\b', 0.9),
        (r'\b(update|change|edit|modify|rename)\b.*\b(title|description|name)\b', 0.85),
        (r'\brename\b.*\bto\b', 0.8),
        # Contextual (medium confidence)
        (r'\bchange\b.*\bto\b', 0.65),
        (r'\bfix\b.*\btask\b', 0.7),
    ],
    Intent.COMPLETE_TASK: [
        # Direct commands (high confidence)
        (r'\b(complete|finish|done)\b.*\btask\b', 0.9),
        (r'\bmark\b.*\b(complete|done|finished)\b', 0.9),
        (r'\bcheck off\b', 0.85),
        (r'\btick\b.*\btask\b', 0.8),
        # Achievement statements
        (r'\bi (finished|completed|did)\b.*\btask\b', 0.85),
        (r'\bi (finished|completed|did)\b', 0.75),
        (r'\btask\b.*\b(is )?done\b', 0.75),
        # Undo commands
        (r'\b(uncomplete|reopen|undo)\b', 0.85),
        (r'\bmark\b.*\b(incomplete|not done)\b', 0.85),
    ],
    Intent.DELETE_TASK: [
        # Direct commands (high confidence)
        (r'\b(delete|remove|trash|discard|erase)\b.*\btask\b', 0.9),
        (r'\bget rid of\b', 0.85),
        # Implicit commands (medium confidence)
        (r"\bdon'?t need\b.*\b(anymore|any more)\b", 0.7),
        (r'\bcancel\b.*\btask\b', 0.65),
        (r'\bremove\b.*\bfrom\b.*\blist\b', 0.8),
    ],
}

# Tool name mapping
INTENT_TO_TOOL: Dict[Intent, Optional[str]] = {
    Intent.CREATE_TASK: "add_task",
    Intent.VIEW_TASKS: "list_tasks",
    Intent.EDIT_TASK: "update_task",
    Intent.COMPLETE_TASK: "complete_task",
    Intent.DELETE_TASK: "delete_task",
    Intent.UNKNOWN: None,
}

# Regex patterns for parameter extraction
TASK_ID_PATTERN = r'\btask\s*#?(\d+)\b|\b#(\d+)\b|\btask\s+(\d+)\b|^(\d+)$'
TITLE_PATTERNS = [
    r"['\"]([^'\"]+)['\"]",                           # Quoted text
    r'(?:called|named|titled)\s+(.+?)(?:\s*$|\s+and\b)',  # "called X"
    r'(?:^|\s)to\s+(.+?)(?:\s*$)',                    # "to X"
    r'task[:\s]+(.+?)(?:\s*$|\s+and\b)',              # "task: X"
]


def get_confidence_level(confidence: float) -> ConfidenceLevel:
    """Convert confidence score to level."""
    if confidence >= 0.7:
        return ConfidenceLevel.HIGH
    elif confidence >= 0.5:
        return ConfidenceLevel.MEDIUM
    elif confidence >= 0.3:
        return ConfidenceLevel.LOW
    else:
        return ConfidenceLevel.UNCERTAIN


def classify_intent(message: str) -> IntentResult:
    """
    Classify user message into an intent with confidence score.

    Args:
        message: User's natural language input

    Returns:
        IntentResult with classification details
    """
    message_lower = message.lower().strip()
    best_intent = Intent.UNKNOWN
    best_confidence = 0.0

    # Check each intent's patterns
    for intent, patterns in INTENT_PATTERNS.items():
        for pattern, weight in patterns:
            if re.search(pattern, message_lower, re.IGNORECASE):
                if weight > best_confidence:
                    best_confidence = weight
                    best_intent = intent

    # Determine confidence level
    confidence_level = get_confidence_level(best_confidence)

    # Extract parameters
    extracted_params = extract_parameters(message, best_intent)

    # Determine if clarification needed
    requires_clarification = False
    clarification_question = None

    if confidence_level == ConfidenceLevel.UNCERTAIN:
        requires_clarification = True
        clarification_question = get_help_message()
    elif confidence_level == ConfidenceLevel.LOW:
        requires_clarification = True
        clarification_question = get_clarification_question(best_intent)
    elif best_intent in [Intent.EDIT_TASK, Intent.COMPLETE_TASK, Intent.DELETE_TASK]:
        # These intents require task_id
        if "task_id" not in extracted_params:
            requires_clarification = True
            clarification_question = "Which task did you mean? Please specify the task number."

    return IntentResult(
        intent=best_intent,
        confidence=best_confidence,
        confidence_level=confidence_level,
        tool_name=INTENT_TO_TOOL[best_intent],
        extracted_params=extracted_params,
        requires_clarification=requires_clarification,
        clarification_question=clarification_question,
    )


def extract_parameters(message: str, intent: Intent) -> Dict[str, Any]:
    """
    Extract relevant parameters from message based on intent.

    Args:
        message: User's input message
        intent: Classified intent

    Returns:
        Dictionary of extracted parameters
    """
    params: Dict[str, Any] = {}

    # Extract task ID (common to many intents)
    id_match = re.search(TASK_ID_PATTERN, message, re.IGNORECASE)
    if id_match:
        task_id = id_match.group(1) or id_match.group(2) or id_match.group(3) or id_match.group(4)
        if task_id:
            params["task_id"] = int(task_id)

    # Intent-specific extraction
    if intent == Intent.CREATE_TASK:
        params.update(_extract_create_params(message))
    elif intent == Intent.VIEW_TASKS:
        params.update(_extract_view_params(message))
    elif intent == Intent.EDIT_TASK:
        params.update(_extract_edit_params(message))
    elif intent == Intent.COMPLETE_TASK:
        params.update(_extract_complete_params(message))
    # DELETE_TASK only needs task_id, already extracted

    return params


def _extract_create_params(message: str) -> Dict[str, Any]:
    """Extract parameters for CREATE_TASK intent."""
    params = {}

    # Try each title extraction pattern
    for pattern in TITLE_PATTERNS:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            title = match.group(1).strip()
            # Clean up common prefixes
            title = re.sub(r'^(a |an |the |my )', '', title, flags=re.IGNORECASE)
            if title and len(title) > 1:
                params["title"] = title
                break

    # Fallback: extract after key phrases
    if "title" not in params:
        # "add task X" or "create todo X"
        match = re.search(r'\b(?:add|create|new)\s+(?:task|todo)\s+(.+)', message, re.IGNORECASE)
        if match:
            params["title"] = match.group(1).strip()

    # "I need to X" fallback
    if "title" not in params:
        match = re.search(r'\bi (?:need|have|got) to\s+(.+?)(?:\s*$)', message, re.IGNORECASE)
        if match:
            params["title"] = match.group(1).strip()

    return params


def _extract_view_params(message: str) -> Dict[str, Any]:
    """Extract parameters for VIEW_TASKS intent."""
    params = {}
    message_lower = message.lower()

    # Completion status filter
    if re.search(r'\b(completed?|done|finished)\b', message_lower):
        # Check if negated
        if not re.search(r'\b(not|un|in)complete\b|\bnot done\b|\bpending\b', message_lower):
            params["completed"] = True

    if re.search(r'\b(incomplete|pending|not done|left|remaining|open)\b', message_lower):
        params["completed"] = False

    # Search term
    search_patterns = [
        r'\babout\s+["\']?(\w+)["\']?',
        r'\bcontaining\s+["\']?(\w+)["\']?',
        r'\bwith\s+["\']?(\w+)["\']?',
        r'\bfor\s+["\']?(\w+)["\']?',
    ]
    for pattern in search_patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            params["search"] = match.group(1)
            break

    # Limit
    limit_match = re.search(r'\b(first|top|last)\s+(\d+)\b', message_lower)
    if limit_match:
        params["limit"] = int(limit_match.group(2))

    return params


def _extract_edit_params(message: str) -> Dict[str, Any]:
    """Extract parameters for EDIT_TASK intent."""
    params = {}

    # Extract new title if provided
    # "change task 5 to 'new title'"
    match = re.search(r'\bto\s+["\']([^"\']+)["\']', message)
    if match:
        params["title"] = match.group(1)
    else:
        # "rename task 5 to new title"
        match = re.search(r'\bto\s+(.+?)(?:\s*$)', message)
        if match:
            title = match.group(1).strip()
            if title and not title.isdigit():
                params["title"] = title

    return params


def _extract_complete_params(message: str) -> Dict[str, Any]:
    """Extract parameters for COMPLETE_TASK intent."""
    params = {}
    message_lower = message.lower()

    # Determine completion state
    if re.search(r'\b(uncomplete|undo|reopen|not done|incomplete)\b', message_lower):
        params["completed"] = False
    else:
        params["completed"] = True

    return params


def get_clarification_question(intent: Intent) -> str:
    """Get appropriate clarification question for an intent."""
    questions = {
        Intent.CREATE_TASK: "What would you like to add to your task list?",
        Intent.VIEW_TASKS: "Would you like to see all tasks, or filter by status (completed/incomplete)?",
        Intent.EDIT_TASK: "Which task would you like to edit? Please provide the task number.",
        Intent.COMPLETE_TASK: "Which task did you complete? Please provide the task number.",
        Intent.DELETE_TASK: "Which task would you like to delete? Please provide the task number.",
        Intent.UNKNOWN: get_help_message(),
    }
    return questions.get(intent, get_help_message())


def get_help_message() -> str:
    """Get help message for unknown intents."""
    return """I'm not sure what you'd like to do. I can help you:
- Add new tasks (e.g., "Add a task to buy groceries")
- View your tasks (e.g., "Show my tasks")
- Update tasks (e.g., "Change task 3 to 'New title'")
- Complete tasks (e.g., "Mark task 5 as done")
- Delete tasks (e.g., "Delete task 2")

What would you like to do?"""


def requires_task_id(intent: Intent) -> bool:
    """Check if intent requires a task ID."""
    return intent in [Intent.EDIT_TASK, Intent.COMPLETE_TASK, Intent.DELETE_TASK]


def is_destructive_intent(intent: Intent) -> bool:
    """Check if intent is destructive (requires confirmation)."""
    return intent == Intent.DELETE_TASK


# Convenience function for quick classification
def quick_classify(message: str) -> tuple:
    """
    Quick classification returning (intent_name, tool_name, confidence).

    Args:
        message: User's input

    Returns:
        Tuple of (intent_name, tool_name, confidence)
    """
    result = classify_intent(message)
    return (result.intent.value, result.tool_name, result.confidence)
