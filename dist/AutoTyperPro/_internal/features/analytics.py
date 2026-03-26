"""
Auto Typer Pro — Analytics Module
Processes typing session data for statistics and visualizations.
"""
import logging

logger = logging.getLogger("AutoTyper.Analytics")


def format_time(seconds: float) -> str:
    """Format seconds into H:MM:SS or M:SS."""
    if seconds < 0:
        return "0:00"
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def format_eta(seconds: float) -> str:
    """Format estimated time remaining."""
    if seconds <= 0:
        return "Done"
    return format_time(seconds)


def calculate_session_summary(stats: dict) -> dict:
    """
    Generate a human-readable session summary from engine stats.
    """
    elapsed = stats.get("elapsed_time", 0)
    typed = stats.get("typed_chars", 0)
    total = stats.get("total_chars", 0)
    errors = stats.get("errors_simulated", 0)
    cps = stats.get("avg_cps", 0)
    wpm = stats.get("avg_wpm", 0)

    completion = (typed / total * 100) if total > 0 else 0

    return {
        "time_formatted": format_time(elapsed),
        "chars": f"{typed:,} / {total:,}",
        "completion": f"{completion:.1f}%",
        "speed": f"{cps:.1f} chars/s  |  {wpm:.0f} WPM",
        "errors": str(errors),
        "status": "✅ Completed" if typed == total else "⏹ Stopped",
    }


def generate_speed_graph_data(speed_samples: list, width: int = 300, height: int = 80) -> list:
    """
    Convert speed samples into normalized (x, y) points for drawing on a canvas.
    Returns list of (x, y) tuples.
    """
    if not speed_samples or len(speed_samples) < 2:
        return []

    max_time = max(s[0] for s in speed_samples)
    max_speed = max(s[1] for s in speed_samples) or 1

    points = []
    padding = 5
    for timestamp, cps in speed_samples:
        x = padding + (timestamp / max_time) * (width - 2 * padding)
        y = height - padding - (cps / max_speed) * (height - 2 * padding)
        points.append((x, y))

    return points
