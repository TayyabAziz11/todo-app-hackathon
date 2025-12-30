"""
TodoManager: Core business logic for managing todos in memory.

This module provides the TodoManager class which handles all CRUD operations
for todos using in-memory storage (Python dictionary).

Phase 1: In-memory storage only (no persistence)
"""

from typing import Dict, Any, Optional, List


class TodoManager:
    """
    Manages in-memory todo storage and operations.

    This class handles:
    - Adding new todos with unique sequential IDs
    - Listing all todos sorted by ID
    - Deleting todos by ID
    - Updating todo title and description
    - Marking todos as complete/incomplete
    - Input validation and sanitization

    Storage:
        In-memory dictionary: Dict[int, Dict[str, Any]]
        Sequential ID counter: int (never decrements, IDs never reused)

    Thread Safety:
        Not thread-safe (Phase 1 assumption: single-process, single-user)
    """

    def __init__(self):
        """
        Initialize TodoManager with empty storage and ID counter at 1.

        Creates:
            _todos: Empty dictionary for storing todos
            _next_id: ID counter starting at 1
        """
        self._todos: Dict[int, Dict[str, Any]] = {}
        self._next_id: int = 1

    def _trim_whitespace(self, text: Optional[str]) -> Optional[str]:
        """
        Trim leading and trailing whitespace from text.

        Args:
            text: String to trim, or None

        Returns:
            Trimmed string, or None if input was None
        """
        if text is None:
            return None
        return text.strip()

    def _validate_title(self, title: str) -> None:
        """
        Validate todo title meets requirements.

        Requirements (per spec.md FR-005, FR-020):
            - Not empty after trimming
            - Not whitespace-only
            - <= 200 characters after trimming

        Args:
            title: Title to validate (already trimmed)

        Raises:
            ValueError: If title is empty or exceeds 200 characters
        """
        if not title:
            raise ValueError("Title cannot be empty")
        if len(title) > 200:
            raise ValueError("Title cannot exceed 200 characters")

    def add_todo(self, title: str, description: Optional[str] = None) -> int:
        """
        Add a new todo with title and optional description.

        Process (per data-model.md):
            1. Trim title and description
            2. Validate title (not empty, <= 200 chars)
            3. Assign next available ID
            4. Increment ID counter
            5. Store todo in dictionary
            6. Return assigned ID

        Args:
            title: Todo title (required, 1-200 chars after trim)
            description: Todo description (optional, trimmed if provided)

        Returns:
            Assigned todo ID (integer)

        Raises:
            ValueError: If title is empty or > 200 characters

        Examples:
            >>> manager = TodoManager()
            >>> id1 = manager.add_todo("Buy groceries")
            >>> id1
            1
            >>> id2 = manager.add_todo("Call dentist", "Annual checkup")
            >>> id2
            2
        """
        # Trim whitespace
        title = self._trim_whitespace(title)
        description = self._trim_whitespace(description)

        # Validate title
        self._validate_title(title)

        # Assign ID and store todo
        todo_id = self._next_id
        self._todos[todo_id] = {
            "id": todo_id,
            "title": title,
            "description": description,
            "completed": False  # New todos start as incomplete
        }

        # Increment ID counter (never decrements, even after deletion)
        self._next_id += 1

        return todo_id

    def list_todos(self) -> List[Dict[str, Any]]:
        """
        List all todos sorted by ID.

        Returns:
            List of todo dictionaries sorted by ID (ascending)
            Empty list if no todos exist

        Each todo dictionary contains:
            - id: int
            - title: str
            - description: str | None
            - completed: bool

        Examples:
            >>> manager = TodoManager()
            >>> manager.add_todo("Buy milk")
            1
            >>> manager.add_todo("Call mom", "Ask about dinner")
            2
            >>> todos = manager.list_todos()
            >>> len(todos)
            2
            >>> todos[0]["id"]
            1
            >>> todos[0]["completed"]
            False
        """
        # Return sorted list of todos (sorted by ID ascending)
        return sorted(self._todos.values(), key=lambda t: t["id"])

    def delete_todo(self, todo_id: int) -> None:
        """
        Delete a todo by ID.

        Args:
            todo_id: ID of todo to delete

        Raises:
            ValueError: If todo_id not found

        Notes:
            - Deleted IDs are never reused (per spec.md FR-003, data-model.md BR-003)
            - ID counter continues to increment

        Examples:
            >>> manager = TodoManager()
            >>> id1 = manager.add_todo("Task 1")
            >>> id2 = manager.add_todo("Task 2")
            >>> manager.delete_todo(id1)
            >>> len(manager.list_todos())
            1
            >>> manager.delete_todo(999)
            Traceback (most recent call last):
                ...
            ValueError: Todo with ID 999 not found
        """
        if todo_id not in self._todos:
            raise ValueError(f"Todo with ID {todo_id} not found")

        del self._todos[todo_id]

    def update_todo(self, todo_id: int, title: Optional[str] = None,
                    description: Optional[str] = None) -> None:
        """
        Update a todo's title and/or description.

        Args:
            todo_id: ID of todo to update
            title: New title (optional, if None, keep existing)
            description: New description (optional, if None, keep existing)

        Raises:
            ValueError: If todo_id not found or if title validation fails

        Notes:
            - At least one of title or description must be provided
            - Title validation applies if title is provided
            - Completed status is not changed

        Examples:
            >>> manager = TodoManager()
            >>> id1 = manager.add_todo("Buy milk")
            >>> manager.update_todo(id1, title="Buy almond milk")
            >>> todos = manager.list_todos()
            >>> todos[0]["title"]
            'Buy almond milk'
            >>> manager.update_todo(id1, description="Unsweetened")
            >>> todos = manager.list_todos()
            >>> todos[0]["description"]
            'Unsweetened'
        """
        if todo_id not in self._todos:
            raise ValueError(f"Todo with ID {todo_id} not found")

        # Update title if provided
        if title is not None:
            title = self._trim_whitespace(title)
            self._validate_title(title)
            self._todos[todo_id]["title"] = title

        # Update description if provided
        if description is not None:
            description = self._trim_whitespace(description)
            self._todos[todo_id]["description"] = description

    def toggle_complete(self, todo_id: int) -> bool:
        """
        Toggle the completion status of a todo.

        Args:
            todo_id: ID of todo to toggle

        Returns:
            New completion status (True if now complete, False if now incomplete)

        Raises:
            ValueError: If todo_id not found

        Examples:
            >>> manager = TodoManager()
            >>> id1 = manager.add_todo("Buy milk")
            >>> manager.toggle_complete(id1)
            True
            >>> manager.toggle_complete(id1)
            False
            >>> manager.toggle_complete(999)
            Traceback (most recent call last):
                ...
            ValueError: Todo with ID 999 not found
        """
        if todo_id not in self._todos:
            raise ValueError(f"Todo with ID {todo_id} not found")

        # Toggle the completed status
        current_status = self._todos[todo_id]["completed"]
        new_status = not current_status
        self._todos[todo_id]["completed"] = new_status

        return new_status
