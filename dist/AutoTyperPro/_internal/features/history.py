"""
Auto Typer Pro — Session History
Logs every typing session for review and analytics. Data persists in ~/.auto_typer/history.json
"""
import json
import logging
from datetime import datetime
from config import HISTORY_FILE

logger = logging.getLogger("AutoTyper.History")

MAX_HISTORY_ENTRIES = 200


def load_history() -> list:
    """Load session history from disk. File is guaranteed to exist by config.init_data_files()."""
    try:
        with open(HISTORY_FILE, "r") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_history(history: list):
    """Save session history to disk."""
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=2)
        logger.info(f"History saved: {len(history)} entries")
    except Exception as e:
        logger.error(f"Failed to save history: {e}")


def add_session(stats: dict, config: dict):
    """
    Record a completed session. Reads existing history, appends, and saves back.
    """
    history = load_history()
    entry = {
        "timestamp": datetime.now().isoformat(),
        "chars_typed": stats.get("typed_chars", 0),
        "total_chars": stats.get("total_chars", 0),
        "elapsed_seconds": round(stats.get("elapsed_time", 0), 2),
        "avg_cps": round(stats.get("avg_cps", 0), 1),
        "avg_wpm": round(stats.get("avg_wpm", 0), 1),
        "errors_simulated": stats.get("errors_simulated", 0),
        "pattern": config.get("pattern", "Unknown"),
        "speed_setting": config.get("speed", 0.03),
        "completed": stats.get("typed_chars", 0) == stats.get("total_chars", 0),
    }
    history.insert(0, entry)  # Most recent first

    # Cap history size
    if len(history) > MAX_HISTORY_ENTRIES:
        history = history[:MAX_HISTORY_ENTRIES]

    save_history(history)
    return entry


def clear_history():
    """Clear all history."""
    save_history([])


def get_aggregate_stats() -> dict:
    """Calculate aggregate statistics across all sessions."""
    history = load_history()
    if not history:
        return {"total_sessions": 0, "completed_sessions": 0, "total_chars": 0, "total_time": 0, "avg_wpm": 0}

    total_chars = sum(h.get("chars_typed", 0) for h in history)
    total_time = sum(h.get("elapsed_seconds", 0) for h in history)
    completed = sum(1 for h in history if h.get("completed", False))
    avg_wpm = sum(h.get("avg_wpm", 0) for h in history) / len(history)

    return {
        "total_sessions": len(history),
        "completed_sessions": completed,
        "total_chars": total_chars,
        "total_time": round(total_time, 1),
        "avg_wpm": round(avg_wpm, 1),
    }
