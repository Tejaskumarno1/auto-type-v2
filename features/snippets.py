"""
Auto Typer Pro — Snippet Library
Save, load, and manage reusable code snippets. Data persists in ~/.auto_typer/snippets.json
"""
import json
import logging
from datetime import datetime
from config import SNIPPETS_FILE

logger = logging.getLogger("AutoTyper.Snippets")


def load_snippets() -> list:
    """Load all snippets from disk. File is guaranteed to exist by config.init_data_files()."""
    try:
        with open(SNIPPETS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_snippets(snippets: list):
    """Save all snippets to disk."""
    try:
        with open(SNIPPETS_FILE, "w") as f:
            json.dump(snippets, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save snippets: {e}")


def add_snippet(name: str, code: str, language: str = "python"):
    """Add a new snippet."""
    snippets = load_snippets()
    snippets.append({
        "name": name,
        "code": code,
        "language": language,
        "created": datetime.now().isoformat(),
    })
    save_snippets(snippets)


def delete_snippet(index: int):
    """Delete snippet by index."""
    snippets = load_snippets()
    if 0 <= index < len(snippets):
        snippets.pop(index)
        save_snippets(snippets)


def update_snippet(index: int, name: str, code: str, language: str = "python"):
    """Update an existing snippet."""
    snippets = load_snippets()
    if 0 <= index < len(snippets):
        snippets[index].update({"name": name, "code": code, "language": language})
        save_snippets(snippets)
