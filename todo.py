#!/usr/bin/env python3
"""
Todo CLI Application - Main Entry Point

Phase 1: In-memory todo management (Interactive Mode)
- Add todos with title and optional description
- List all todos
- Delete todos by ID
- Mark todos complete/incomplete (Phase 3 placeholder)
- Interactive menu-driven REPL interface

Usage:
    python todo.py

    This launches an interactive console session where you can:
    1. Add todos
    2. List all todos
    3. Delete todos
    4. Mark complete/incomplete (Phase 3)
    5. Exit

Note: All todos are stored in memory and will be lost when you exit.
"""

import sys
from cli import run_interactive_app
from todo_manager import TodoManager


def main() -> int:
    """
    Main entry point for todo CLI application (interactive mode).

    Returns:
        Exit code:
            0: Normal exit (user chose exit)
            1: Error exit
            2: System error (unexpected exception)

    Process:
        1. Create TodoManager instance (in-memory storage)
        2. Launch interactive REPL loop
        3. Handle exceptions and exit codes
    """
    try:
        # Initialize TodoManager (in-memory storage)
        manager = TodoManager()

        # Run interactive application
        return run_interactive_app(manager)

    except KeyboardInterrupt:
        # User interrupted (Ctrl+C)
        print("\n\nApplication terminated by user (Ctrl+C)", file=sys.stderr)
        return 1

    except Exception as e:
        # Unexpected system error
        print(f"\nError: An unexpected error occurred: {e}", file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
