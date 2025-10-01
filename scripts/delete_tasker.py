#!/usr/bin/env python3
"""
Delete a task from a JSON task list by ID.
"""

import argparse
import json
import os
import sys
from typing import List, Dict, Optional


EXIT_SUCCESS = 0
EXIT_NOT_FOUND = 1
EXIT_ERROR = 2


def load_tasks(path: str) -> List[Dict]:
    if not os.path.exists(path):
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(EXIT_ERROR)

    try:
        with open(path, "r", encoding="utf-8") as f:
            tasks = json.load(f)
        if not isinstance(tasks, list):
            raise ValueError("JSON root must be a list.")
        return tasks
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error: Invalid JSON in {path}: {e}", file=sys.stderr)
        sys.exit(EXIT_ERROR)
    except OSError as e:
        print(f"Error: Cannot read file {path}: {e}", file=sys.stderr)
        sys.exit(EXIT_ERROR)


def save_tasks(path: str, tasks: List[Dict]) -> None:
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(tasks, f, indent=2, ensure_ascii=False)
    except OSError as e:
        print(f"Error: Cannot write to file {path}: {e}", file=sys.stderr)
        sys.exit(EXIT_ERROR)


def find_task(tasks: List[Dict], task_id: int) -> Optional[Dict]:
    return next((t for t in tasks if t.get("id") == task_id), None)


def confirm(prompt: str) -> bool:
    try:
        return input(f"{prompt} [y/N]: ").strip().lower() in ("y", "yes")
    except EOFError:
        return False


def delete_task(path: str, task_id: int, assume_yes: bool) -> int:
    tasks = load_tasks(path)
    if not tasks:
        print("Error: No tasks available.", file=sys.stderr)
        return EXIT_NOT_FOUND

    task = find_task(tasks, task_id)
    if not task:
        print(f"Error: Task ID {task_id} not found.", file=sys.stderr)
        return EXIT_NOT_FOUND

    title = task.get("title", "(untitled)")
    if not assume_yes and not confirm(f"Delete task #{task_id}: '{title}'?"):
        print("Aborted.")
        return EXIT_NOT_FOUND

    updated_tasks = [t for t in tasks if t.get("id") != task_id]
    if len(updated_tasks) == len(tasks):
        print("Error: Task could not be deleted (race condition?).", file=sys.stderr)
        return EXIT_NOT_FOUND

    save_tasks(path, updated_tasks)
    print(f"Task #{task_id} deleted.")
    return EXIT_SUCCESS


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Delete a task by ID from a JSON task list.")
    parser.add_argument("id", help="Task ID to delete.", type=int)
    parser.add_argument("-y", "--yes", action="store_true", help="Skip confirmation.")
    parser.add_argument("--db", default="tasks.json", help="Path to JSON task file.")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    return delete_task(args.db, args.id, args.yes)


if __name__ == "__main__":
    raise SystemExit(main())
