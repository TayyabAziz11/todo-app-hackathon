"""
CLI: Command-line interface for Todo application.

This module provides the interactive menu-driven interface for todo management.
It handles user input, validation, and output formatting in a stateful REPL loop.

Phase 1 interactive mode:
- Add: Prompt for title and description, create new todo
- List: Display all todos with IDs and status
- Delete: Prompt for ID, remove todo
- Toggle: Mark todo complete/incomplete
- Exit: Gracefully terminate application
"""

import sys
from typing import Optional
from todo_manager import TodoManager


def display_menu() -> None:
    """
    Display the interactive menu.

    Shows available commands and prompts user for input.
    """
    print("\n" + "=" * 50)
    print("TODO APP - PHASE 1")
    print("=" * 50)
    print("1. Add a todo")
    print("2. View all todos")
    print("3. Update a todo")
    print("4. Delete a todo")
    print("5. Mark todo complete / incomplete")
    print("6. Exit")
    print("=" * 50)


def get_user_input(prompt: str) -> str:
    """
    Get user input with a prompt.

    Args:
        prompt: Prompt message to display

    Returns:
        User input string (stripped of whitespace)
    """
    return input(prompt).strip()


def interactive_add(manager: TodoManager) -> None:
    """
    Interactive add todo workflow.

    Prompts user for title (required) and description (optional).
    Validates input and displays confirmation or error.

    Args:
        manager: TodoManager instance
    """
    print("\n--- Add New Todo ---")

    # Get title (required)
    title = get_user_input("Enter title (required, max 200 chars): ")

    if not title:
        print("Error: Title cannot be empty", file=sys.stderr)
        return

    # Get description (optional)
    description = get_user_input("Enter description (optional, press Enter to skip): ")
    if not description:
        description = None

    # Add todo
    try:
        todo_id = manager.add_todo(title, description)
        print(f"\n✓ Todo added successfully with ID: {todo_id}")
    except ValueError as e:
        print(f"\nError: {e}", file=sys.stderr)


def interactive_list(manager: TodoManager) -> None:
    """
    Interactive list todos workflow.

    Displays all todos with IDs, titles, descriptions, and status.
    Shows message if no todos exist.

    Args:
        manager: TodoManager instance
    """
    print("\n--- All Todos ---")

    todos = manager.list_todos()

    if not todos:
        print("No todos found")
        return

    for i, todo in enumerate(todos):
        if i > 0:
            print()  # Blank line between todos

        status = "✓ Complete" if todo['completed'] else "○ Incomplete"
        print(f"ID: {todo['id']} | Status: {status}")
        print(f"Title: {todo['title']}")
        if todo['description'] is not None:
            print(f"Description: {todo['description']}")


def interactive_update(manager: TodoManager) -> None:
    """
    Interactive update todo workflow.

    Prompts user for todo ID and new title/description.
    Allows updating title, description, or both.

    Args:
        manager: TodoManager instance
    """
    print("\n--- Update Todo ---")

    # Get ID from user
    id_input = get_user_input("Enter todo ID to update: ")

    # Validate ID format
    try:
        todo_id = int(id_input)
    except ValueError:
        print(f"Error: Invalid ID format. Please enter a number.", file=sys.stderr)
        return

    # Check if todo exists
    todos = manager.list_todos()
    todo_exists = any(t['id'] == todo_id for t in todos)
    if not todo_exists:
        print(f"\nError: Todo with ID {todo_id} not found", file=sys.stderr)
        return

    # Get current todo to show existing values
    current_todo = next(t for t in todos if t['id'] == todo_id)
    print(f"\nCurrent title: {current_todo['title']}")
    print(f"Current description: {current_todo['description'] or '(none)'}")

    # Get new values
    print("\nEnter new values (press Enter to keep current):")
    new_title = get_user_input("New title: ")
    new_description = get_user_input("New description: ")

    # Validate at least one field is provided
    if not new_title and not new_description:
        print("\nNo changes made (both fields empty)")
        return

    # Update todo
    try:
        update_title = new_title if new_title else None
        update_desc = new_description if new_description else None
        manager.update_todo(todo_id, title=update_title, description=update_desc)
        print(f"\n✓ Todo {todo_id} updated successfully")
    except ValueError as e:
        print(f"\nError: {e}", file=sys.stderr)


def interactive_delete(manager: TodoManager) -> None:
    """
    Interactive delete todo workflow.

    Prompts user for todo ID and attempts deletion.
    Validates ID exists and displays confirmation or error.

    Args:
        manager: TodoManager instance
    """
    print("\n--- Delete Todo ---")

    # Get ID from user
    id_input = get_user_input("Enter todo ID to delete: ")

    # Validate ID format
    try:
        todo_id = int(id_input)
    except ValueError:
        print(f"Error: Invalid ID format. Please enter a number.", file=sys.stderr)
        return

    # Delete todo
    try:
        manager.delete_todo(todo_id)
        print(f"\n✓ Todo {todo_id} deleted successfully")
    except ValueError as e:
        print(f"\nError: {e}", file=sys.stderr)


def interactive_toggle(manager: TodoManager) -> None:
    """
    Interactive toggle todo status workflow.

    Prompts user for todo ID and toggles completion status.
    Shows new status after toggle.

    Args:
        manager: TodoManager instance
    """
    print("\n--- Mark Complete/Incomplete ---")

    # Get ID from user
    id_input = get_user_input("Enter todo ID to toggle: ")

    # Validate ID format
    try:
        todo_id = int(id_input)
    except ValueError:
        print(f"Error: Invalid ID format. Please enter a number.", file=sys.stderr)
        return

    # Toggle todo
    try:
        new_status = manager.toggle_complete(todo_id)
        status_text = "complete" if new_status else "incomplete"
        print(f"\n✓ Todo {todo_id} marked as {status_text}")
    except ValueError as e:
        print(f"\nError: {e}", file=sys.stderr)


def run_interactive_app(manager: TodoManager) -> int:
    """
    Run the interactive todo application in REPL mode.

    Displays menu repeatedly and processes user commands until exit.
    Handles invalid input gracefully without crashing.

    Args:
        manager: TodoManager instance

    Returns:
        Exit code (0 for normal exit, 1 for error)
    """
    print("\nWelcome to Todo App - Phase 1 (Interactive Mode)")

    while True:
        try:
            display_menu()
            choice = get_user_input("\nEnter your choice (1-6): ")

            if choice == '1' or choice.lower() == 'add':
                interactive_add(manager)
            elif choice == '2' or choice.lower() == 'list' or choice.lower() == 'view':
                interactive_list(manager)
            elif choice == '3' or choice.lower() == 'update':
                interactive_update(manager)
            elif choice == '4' or choice.lower() == 'delete':
                interactive_delete(manager)
            elif choice == '5' or choice.lower() == 'toggle' or choice.lower() == 'complete':
                interactive_toggle(manager)
            elif choice == '6' or choice.lower() == 'exit' or choice.lower() == 'quit':
                print("\nGoodbye! Your todos will be lost (no persistence in Phase 1).")
                return 0
            else:
                print(f"\nError: Invalid choice '{choice}'. Please enter 1-6.", file=sys.stderr)

        except KeyboardInterrupt:
            print("\n\nOperation cancelled. Returning to menu...")
            continue

        except EOFError:
            print("\n\nEOF detected. Exiting...")
            return 0
