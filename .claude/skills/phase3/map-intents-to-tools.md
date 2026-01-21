# Skill: map-intents-to-tools

## 1. Skill Name
`map-intents-to-tools`

## 2. Purpose
Define comprehensive mappings between natural language user intents and MCP tool calls for the Todo AI Chatbot. This skill specifies phrase patterns for each action (add, list, update, delete, complete), confidence thresholds for intent classification, tool chaining logic for multi-step operations, and safe handling of ambiguous commands.

## 3. Applicable Agents
- **todo-ai-agent-designer** (primary)
- mcp-tool-architect (tool alignment)
- chat-api-orchestrator (integration)
- phase3-qa-demo (testing/validation)
- test-qa-validator (intent testing)

## 4. Inputs
- **MCP Tool Definitions**: Tool schemas from `design-mcp-tools` skill
- **System Prompt**: Agent behavior from `define-agent-system-prompt`
- **User Research**: Common phrasings for task management
- **Domain Knowledge**: Task management terminology
- **Edge Cases**: Ambiguous and multi-intent scenarios

## 5. Outputs
- **Intent-to-Tool Mapping Table**: Complete mapping with patterns
- **Confidence Thresholds**: Classification certainty rules
- **Tool Chaining Logic**: Multi-step operation flows
- **Ambiguity Resolution Rules**: Safe handling procedures
- **Example Phrases**: 10+ examples per intent
- **Implementation Code**: Intent classifier module

## 6. Scope & Boundaries

### In Scope
- Intent classification patterns (add, list, update, complete, delete)
- Confidence scoring and thresholds
- Single-intent to single-tool mappings
- Multi-intent to tool-chain mappings
- Ambiguity detection and resolution
- Fallback behaviors for unknown intents
- Context-aware intent refinement

### Out of Scope
- Natural Language Understanding model training
- Speech-to-text processing
- Sentiment analysis
- Language translation
- User preference learning
- Intent prediction before user input

## 7. Reusability Notes
- **Phase 3**: Core intent mapping for chatbot
- **Phase 4**: Extend with collaboration intents (share, assign)
- **Phase 5**: Add advanced intents (remind, schedule)
- **Cross-Project**: Pattern library reusable for other domains

### Reusability Mechanisms
- Intent patterns as configuration (not hardcoded)
- Confidence thresholds adjustable
- Tool chaining rules composable
- Ambiguity handlers pluggable

## 8. Dependencies

### Upstream Dependencies
- `design-mcp-tools` (tool definitions)
- `define-agent-system-prompt` (behavioral context)
- User research data (common phrases)

### Downstream Dependencies
- `chat-api-orchestrator` (uses mappings in chat flow)
- `phase3-qa-demo` (validates mappings)
- Test suites (intent classification tests)

### Parallel Dependencies
- `implement-mcp-server` (tools being called)

## 9. Quality Expectations

### Completeness
- Every common phrasing covered for each intent
- All edge cases documented
- All ambiguous scenarios addressed
- Fallback defined for every unknown case

### Accuracy
- High-confidence mappings are correct 95%+
- Medium-confidence triggers clarification
- Low-confidence triggers safe fallback
- No false positives for dangerous operations

### Robustness
- Handles typos and variations
- Works with incomplete sentences
- Manages multi-language hints
- Graceful degradation on uncertainty

### Testability
- Every mapping has test cases
- Confidence thresholds verifiable
- Chaining logic testable
- Ambiguity handling measurable

## 10. Example Usage (Complete Intent Mapping)

---

## Intent-to-Tool Mapping Table

### Primary Intent Mappings

| Intent | Tool | Confidence Required | Requires ID |
|--------|------|---------------------|-------------|
| `CREATE_TASK` | `add_task` | LOW (0.3+) | No |
| `VIEW_TASKS` | `list_tasks` | LOW (0.3+) | No |
| `EDIT_TASK` | `update_task` | MEDIUM (0.5+) | Yes |
| `COMPLETE_TASK` | `complete_task` | MEDIUM (0.5+) | Yes |
| `DELETE_TASK` | `delete_task` | HIGH (0.7+) | Yes |

### Confidence Threshold Definitions

| Level | Score Range | Action |
|-------|-------------|--------|
| **HIGH** | 0.7 - 1.0 | Execute immediately |
| **MEDIUM** | 0.5 - 0.69 | Execute with confirmation |
| **LOW** | 0.3 - 0.49 | Ask for clarification |
| **UNCERTAIN** | 0.0 - 0.29 | Fallback to help message |

---

## Intent: CREATE_TASK → `add_task`

### Pattern Categories

**Direct Commands** (High Confidence: 0.85+)
```
- "Add a task to {title}"
- "Create a new todo: {title}"
- "Make a task called {title}"
- "New task: {title}"
- "Add {title} to my list"
```

**Implicit Requests** (Medium Confidence: 0.6-0.84)
```
- "I need to {title}"
- "I have to {title}"
- "Don't let me forget to {title}"
- "Remind me to {title}"
- "Put {title} on my list"
```

**Casual Mentions** (Low Confidence: 0.3-0.59)
```
- "I should {title}"
- "Maybe I'll {title}"
- "{title} would be good to do"
- "Thinking about {title}"
```

### Example Phrases (20+)

| Phrase | Confidence | Extracted Title |
|--------|------------|-----------------|
| "Add a task to buy groceries" | 0.95 | "buy groceries" |
| "Create todo: call mom" | 0.92 | "call mom" |
| "New task - finish report" | 0.90 | "finish report" |
| "Put 'dentist appointment' on my list" | 0.85 | "dentist appointment" |
| "I need to pick up dry cleaning" | 0.75 | "pick up dry cleaning" |
| "Don't let me forget the meeting" | 0.70 | "the meeting" |
| "Remind me to water plants" | 0.68 | "water plants" |
| "I have to submit the form" | 0.65 | "submit the form" |
| "I should call the bank" | 0.45 | "call the bank" |
| "Maybe exercise later" | 0.35 | "exercise later" |

### Title Extraction Rules

1. After "to/for": `"Add a task to {TITLE}"` → TITLE
2. After colon: `"New task: {TITLE}"` → TITLE
3. In quotes: `"Add '{TITLE}'"` → TITLE
4. After "called/named": `"task called {TITLE}"` → TITLE
5. Remainder: `"I need to {TITLE}"` → TITLE

---

## Intent: VIEW_TASKS → `list_tasks`

### Pattern Categories

**Direct Queries** (High Confidence: 0.9+)
```
- "Show me my tasks"
- "List all my todos"
- "What are my tasks?"
- "Display my todo list"
- "View all tasks"
```

**Filtered Queries** (High Confidence: 0.85+)
```
- "Show completed tasks"
- "List incomplete tasks"
- "What haven't I done?"
- "Show me what's left"
- "Tasks about {keyword}"
```

**Implicit Queries** (Medium Confidence: 0.5-0.8)
```
- "What do I have to do?"
- "What's on my list?"
- "Anything pending?"
- "Do I have tasks?"
```

### Example Phrases (20+)

| Phrase | Confidence | Filter Applied |
|--------|------------|----------------|
| "Show me my tasks" | 0.95 | None |
| "List all todos" | 0.93 | None |
| "What are my tasks?" | 0.90 | None |
| "Show completed tasks" | 0.92 | `completed=true` |
| "List incomplete tasks" | 0.90 | `completed=false` |
| "What haven't I finished?" | 0.85 | `completed=false` |
| "Show tasks about groceries" | 0.88 | `search="groceries"` |
| "Do I have anything about work?" | 0.80 | `search="work"` |
| "What do I need to do?" | 0.75 | `completed=false` |
| "What's on my plate?" | 0.65 | None |
| "Anything left?" | 0.55 | `completed=false` |

### Filter Extraction Rules

| Pattern | Filter |
|---------|--------|
| "completed", "done", "finished" | `completed=true` |
| "incomplete", "pending", "not done", "left", "remaining" | `completed=false` |
| "about {X}", "containing {X}", "with {X}" | `search=X` |
| "first N", "top N" | `limit=N` |

---

## Intent: EDIT_TASK → `update_task`

### Pattern Categories

**Direct Commands** (High Confidence: 0.85+)
```
- "Update task {id} to {new_value}"
- "Change task {id} title to {title}"
- "Edit task {id}"
- "Rename task {id} to {title}"
- "Modify task {id}"
```

**Contextual Commands** (Medium Confidence: 0.6-0.84)
```
- "Change the {task_reference} to {new_value}"
- "Update the grocery task"
- "Fix the title of that one"
- "Edit my first task"
```

### Example Phrases (15+)

| Phrase | Confidence | Task ID | New Title |
|--------|------------|---------|-----------|
| "Update task 5 to 'Buy organic milk'" | 0.95 | 5 | "Buy organic milk" |
| "Change task 3 title to 'Call dentist tomorrow'" | 0.92 | 3 | "Call dentist tomorrow" |
| "Rename task 7 to 'Finish quarterly report'" | 0.90 | 7 | "Finish quarterly report" |
| "Edit task 2" | 0.85 | 2 | (ask user) |
| "Change the grocery task to 'Shop at Costco'" | 0.70 | (search) | "Shop at Costco" |
| "Fix task 1's description" | 0.75 | 1 | (ask user) |
| "Update the first one" | 0.50 | (clarify) | (clarify) |

### Ambiguity Handling

**No task ID provided**:
1. Check conversation context for recently mentioned task
2. If single task in list, assume that one
3. Otherwise, call `list_tasks` and ask user to specify

**No new value provided**:
1. Confirm task identification
2. Ask: "What would you like to change it to?"

---

## Intent: COMPLETE_TASK → `complete_task`

### Pattern Categories

**Direct Commands** (High Confidence: 0.9+)
```
- "Mark task {id} as complete"
- "Complete task {id}"
- "Done with task {id}"
- "Finish task {id}"
- "Check off task {id}"
```

**Achievement Statements** (High Confidence: 0.8-0.9)
```
- "I finished task {id}"
- "Task {id} is done"
- "Completed {task_reference}"
- "I did {task_reference}"
```

**Undo Commands** (High Confidence: 0.85+)
```
- "Uncomplete task {id}"
- "Mark task {id} incomplete"
- "Undo completing task {id}"
- "Reopen task {id}"
```

### Example Phrases (20+)

| Phrase | Confidence | Task ID | Completed |
|--------|------------|---------|-----------|
| "Mark task 3 as complete" | 0.95 | 3 | true |
| "Complete task 5" | 0.93 | 5 | true |
| "Done with task 7" | 0.90 | 7 | true |
| "I finished task 2" | 0.88 | 2 | true |
| "Check off task 4" | 0.85 | 4 | true |
| "Task 1 is done" | 0.82 | 1 | true |
| "I did the grocery task" | 0.75 | (search) | true |
| "Finished the report" | 0.70 | (search) | true |
| "Uncomplete task 3" | 0.90 | 3 | false |
| "Reopen task 5" | 0.85 | 5 | false |
| "Mark task 2 as not done" | 0.88 | 2 | false |
| "Undo completing task 1" | 0.85 | 1 | false |

### Completed State Detection

| Pattern | `completed` Value |
|---------|-------------------|
| complete, done, finish, check off, tick | `true` |
| uncomplete, undo, reopen, not done, incomplete | `false` |

---

## Intent: DELETE_TASK → `delete_task`

### Pattern Categories

**Direct Commands** (High Confidence: 0.9+)
```
- "Delete task {id}"
- "Remove task {id}"
- "Get rid of task {id}"
- "Trash task {id}"
```

**Implicit Commands** (Medium Confidence: 0.6-0.8)
```
- "I don't need task {id} anymore"
- "Cancel task {id}"
- "Task {id} is no longer needed"
- "Forget about task {id}"
```

### Example Phrases (15+)

| Phrase | Confidence | Task ID | Requires Confirmation |
|--------|------------|---------|----------------------|
| "Delete task 5" | 0.95 | 5 | Yes |
| "Remove task 3" | 0.93 | 3 | Yes |
| "Get rid of task 7" | 0.90 | 7 | Yes |
| "Trash task 2" | 0.85 | 2 | Yes |
| "I don't need task 4 anymore" | 0.75 | 4 | Yes |
| "Cancel task 1" | 0.70 | 1 | Yes |
| "Delete the grocery task" | 0.80 | (search) | Yes |
| "Remove all completed tasks" | 0.85 | (multiple) | Yes (extra) |

### Safety Rules (CRITICAL)

1. **Always require task ID** - Never delete without explicit identification
2. **Confirm before deletion** - "Are you sure you want to delete '{title}'?"
3. **Reject bulk delete without explicit list** - "Delete all" requires clarification
4. **No undo available** - Warn user deletion is permanent

---

## Tool Chaining Logic

### Chain: Search + Action

When user references task by name instead of ID:

```
User: "Complete the grocery task"

Chain:
1. list_tasks(search="grocery") → Find matching tasks
2. IF single match: complete_task(task_id=matched_id)
   IF multiple matches: Ask user to choose
   IF no matches: "I couldn't find a task about 'grocery'"
```

### Chain: Create + Complete

User wants to log already-completed task:

```
User: "Add 'buy milk' and mark it done"

Chain:
1. add_task(title="buy milk") → Get new task_id
2. complete_task(task_id=new_id, completed=true)
3. Response: "I've added 'buy milk' and marked it complete."
```

### Chain: List + Action

User needs to see tasks before acting:

```
User: "Complete my first task"

Chain:
1. list_tasks(limit=5) → Get task list with IDs
2. Identify "first" as task with lowest ID or oldest
3. complete_task(task_id=first_id)
```

### Chain: Batch Operations

User wants to act on multiple tasks:

```
User: "Complete tasks 1, 3, and 5"

Chain:
1. complete_task(task_id=1)
2. complete_task(task_id=3)
3. complete_task(task_id=5)
4. Response: "I've marked tasks 1, 3, and 5 as complete."
```

---

## Ambiguity Resolution Rules

### Rule 1: Missing Task ID

**Trigger**: Action requires task_id but none provided
**Resolution**:
```
1. Check conversation context for recently mentioned task
2. If found: "Did you mean task #{id} ('{title}')?"
3. If not found: Call list_tasks, then ask user to specify
```

### Rule 2: Multiple Matching Tasks

**Trigger**: Search returns multiple results
**Resolution**:
```
1. List matching tasks with IDs
2. Ask: "I found multiple tasks. Which one did you mean?"
3. Wait for user to specify by ID or clearer description
```

### Rule 3: Ambiguous Action

**Trigger**: Intent unclear between two operations
**Resolution**:
```
| Ambiguity | Clarification Question |
|-----------|------------------------|
| update vs complete | "Do you want to edit the task details or mark it as done?" |
| complete vs delete | "Do you want to mark it complete or remove it entirely?" |
| add vs update | "Do you want to create a new task or update an existing one?" |
```

### Rule 4: Dangerous Operation

**Trigger**: Delete or bulk operation requested
**Resolution**:
```
1. Always confirm: "Are you sure you want to delete '{title}'? This cannot be undone."
2. Require explicit "yes" or "confirm"
3. Accept: yes, confirm, do it, sure, proceed
4. Reject: no, cancel, wait, stop, nevermind
```

### Rule 5: Unknown Intent

**Trigger**: Confidence below 0.3 for all intents
**Resolution**:
```
Response: "I'm not sure what you'd like to do. I can help you:
- Add new tasks
- View your task list
- Update task details
- Mark tasks complete
- Delete tasks

What would you like to do?"
```

---

## Implementation: Intent Classifier Module

**File**: `backend/app/agent/intent_classifier.py`

```python
"""
Intent classification for natural language to MCP tool mapping.
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple, Dict, Any


class Intent(Enum):
    CREATE_TASK = "create_task"
    VIEW_TASKS = "view_tasks"
    EDIT_TASK = "edit_task"
    COMPLETE_TASK = "complete_task"
    DELETE_TASK = "delete_task"
    UNKNOWN = "unknown"


class ConfidenceLevel(Enum):
    HIGH = "high"         # 0.7+
    MEDIUM = "medium"     # 0.5-0.69
    LOW = "low"           # 0.3-0.49
    UNCERTAIN = "uncertain"  # <0.3


@dataclass
class IntentResult:
    """Result of intent classification."""
    intent: Intent
    confidence: float
    confidence_level: ConfidenceLevel
    tool_name: Optional[str]
    extracted_params: Dict[str, Any]
    requires_clarification: bool
    clarification_question: Optional[str]


# Intent patterns with weights
INTENT_PATTERNS = {
    Intent.CREATE_TASK: [
        (r'\b(add|create|new|make)\b.*\b(task|todo|item)\b', 0.9),
        (r'\b(add|put)\b.*\b(to|on)\b.*\blist\b', 0.85),
        (r'\b(remind|remember)\b.*\bto\b', 0.7),
        (r"\bi (need|have|got) to\b", 0.65),
        (r"\bdon'?t (let me )?forget\b", 0.7),
        (r'\bnew task\b', 0.95),
    ],
    Intent.VIEW_TASKS: [
        (r'\b(show|list|view|display|see)\b.*\b(task|todo|list)\b', 0.9),
        (r'\bwhat.*\b(task|todo|do|have)\b', 0.85),
        (r'\bmy (task|todo|list)\b', 0.8),
        (r'\b(anything|something)\b.*(pending|left|do)\b', 0.7),
        (r"\bwhat'?s on my\b", 0.75),
    ],
    Intent.EDIT_TASK: [
        (r'\b(update|change|edit|modify|rename|fix)\b.*\btask\b', 0.9),
        (r'\b(update|change|edit|modify|rename)\b.*\b(title|description)\b', 0.85),
        (r'\brename\b.*\bto\b', 0.8),
        (r'\bchange\b.*\bto\b', 0.7),
    ],
    Intent.COMPLETE_TASK: [
        (r'\b(complete|finish|done|mark)\b.*\btask\b', 0.9),
        (r'\bmark.*\b(complete|done|finished)\b', 0.9),
        (r'\bcheck off\b', 0.85),
        (r'\bi (finished|completed|did)\b', 0.8),
        (r'\btask.*\b(is )?done\b', 0.75),
        (r'\b(uncomplete|reopen|undo)\b', 0.85),
    ],
    Intent.DELETE_TASK: [
        (r'\b(delete|remove|trash|discard)\b.*\btask\b', 0.9),
        (r'\bget rid of\b', 0.85),
        (r"\bdon'?t need\b.*\banymore\b", 0.7),
        (r'\bcancel\b.*\btask\b', 0.65),
    ],
}

# Task ID extraction pattern
TASK_ID_PATTERN = r'\btask\s*#?(\d+)\b|\b#(\d+)\b|\btask\s+(\d+)\b'

# Title extraction patterns
TITLE_PATTERNS = [
    r"['\"]([^'\"]+)['\"]",  # Quoted text
    r'(?:called|named|titled)\s+(.+?)(?:\s*$|\s+and\b)',
    r'(?:to|task[:\s]+)\s*(.+?)(?:\s*$|\s+and\b)',
]


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
    if best_confidence >= 0.7:
        confidence_level = ConfidenceLevel.HIGH
    elif best_confidence >= 0.5:
        confidence_level = ConfidenceLevel.MEDIUM
    elif best_confidence >= 0.3:
        confidence_level = ConfidenceLevel.LOW
    else:
        confidence_level = ConfidenceLevel.UNCERTAIN

    # Map intent to tool
    tool_mapping = {
        Intent.CREATE_TASK: "add_task",
        Intent.VIEW_TASKS: "list_tasks",
        Intent.EDIT_TASK: "update_task",
        Intent.COMPLETE_TASK: "complete_task",
        Intent.DELETE_TASK: "delete_task",
        Intent.UNKNOWN: None,
    }

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
        if "task_id" not in extracted_params:
            requires_clarification = True
            clarification_question = "Which task did you mean? Please specify the task number."

    return IntentResult(
        intent=best_intent,
        confidence=best_confidence,
        confidence_level=confidence_level,
        tool_name=tool_mapping[best_intent],
        extracted_params=extracted_params,
        requires_clarification=requires_clarification,
        clarification_question=clarification_question,
    )


def extract_parameters(message: str, intent: Intent) -> Dict[str, Any]:
    """Extract relevant parameters from message based on intent."""
    params = {}

    # Extract task ID
    id_match = re.search(TASK_ID_PATTERN, message, re.IGNORECASE)
    if id_match:
        task_id = id_match.group(1) or id_match.group(2) or id_match.group(3)
        params["task_id"] = int(task_id)

    # Extract title for CREATE_TASK
    if intent == Intent.CREATE_TASK:
        for pattern in TITLE_PATTERNS:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                params["title"] = match.group(1).strip()
                break

    # Extract filters for VIEW_TASKS
    if intent == Intent.VIEW_TASKS:
        if re.search(r'\b(complete|done|finished)\b', message, re.IGNORECASE):
            if not re.search(r'\bnot\b|\bincomplete\b|\bpending\b', message, re.IGNORECASE):
                params["completed"] = True
        if re.search(r'\b(incomplete|pending|not done|left|remaining)\b', message, re.IGNORECASE):
            params["completed"] = False
        # Search term
        search_match = re.search(r'\babout\s+["\']?(\w+)["\']?\b', message, re.IGNORECASE)
        if search_match:
            params["search"] = search_match.group(1)

    # Extract completion state
    if intent == Intent.COMPLETE_TASK:
        if re.search(r'\b(uncomplete|undo|reopen|not done|incomplete)\b', message, re.IGNORECASE):
            params["completed"] = False
        else:
            params["completed"] = True

    return params


def get_clarification_question(intent: Intent) -> str:
    """Get clarification question for an intent."""
    questions = {
        Intent.CREATE_TASK: "What would you like to add to your task list?",
        Intent.VIEW_TASKS: "Would you like to see all tasks, or just incomplete/completed ones?",
        Intent.EDIT_TASK: "Which task would you like to edit, and what should I change?",
        Intent.COMPLETE_TASK: "Which task did you complete?",
        Intent.DELETE_TASK: "Which task would you like to delete?",
        Intent.UNKNOWN: get_help_message(),
    }
    return questions.get(intent, get_help_message())


def get_help_message() -> str:
    """Get the help message for unknown intents."""
    return """I'm not sure what you'd like to do. I can help you:
- Add new tasks (e.g., "Add a task to buy groceries")
- View your tasks (e.g., "Show my tasks")
- Update tasks (e.g., "Change task 3 to 'New title'")
- Complete tasks (e.g., "Mark task 5 as done")
- Delete tasks (e.g., "Delete task 2")

What would you like to do?"""
```

---

## Testing Matrix

### Test Cases per Intent

| Intent | Test Case | Input | Expected Output |
|--------|-----------|-------|-----------------|
| CREATE | Direct | "Add task buy milk" | HIGH, add_task, title="buy milk" |
| CREATE | Implicit | "I need to call mom" | MEDIUM, add_task, title="call mom" |
| CREATE | Vague | "Maybe groceries" | LOW, clarify |
| VIEW | Direct | "Show my tasks" | HIGH, list_tasks |
| VIEW | Filtered | "Show completed" | HIGH, list_tasks, completed=true |
| VIEW | Implicit | "What's left?" | MEDIUM, list_tasks, completed=false |
| EDIT | With ID | "Update task 5" | HIGH, update_task, task_id=5 |
| EDIT | No ID | "Change the title" | MEDIUM, clarify |
| COMPLETE | With ID | "Done with task 3" | HIGH, complete_task, task_id=3 |
| COMPLETE | Undo | "Uncomplete task 2" | HIGH, complete_task, completed=false |
| DELETE | With ID | "Delete task 7" | HIGH, delete_task, task_id=7 |
| DELETE | No ID | "Remove it" | LOW, clarify |
| UNKNOWN | Random | "Hello there" | UNCERTAIN, help message |

---

## Metadata
- **Version**: 1.0.0
- **Phase Introduced**: Phase 3
- **Last Updated**: 2026-01-19
- **Skill Type**: Design + Implementation
- **Execution Surface**: Agent (todo-ai-agent-designer)
- **Prerequisite Skills**: `design-mcp-tools`, `define-agent-system-prompt`
