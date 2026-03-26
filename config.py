"""
Auto Typer Pro — Central Configuration & Constants
"""
import os
import json

# ============================================================
# PATHS
# ============================================================
APP_DIR = os.path.expanduser("~/.auto_typer")
PROFILES_FILE = os.path.join(APP_DIR, "profiles.json")
SNIPPETS_FILE = os.path.join(APP_DIR, "snippets.json")
HISTORY_FILE = os.path.join(APP_DIR, "history.json")
SETTINGS_FILE = os.path.join(APP_DIR, "settings.json")

# Ensure app directory exists
os.makedirs(APP_DIR, exist_ok=True)

# ============================================================
# DEFAULTS
# ============================================================
DEFAULT_SPEED = 0.03
MIN_SPEED = 0.001
MAX_SPEED = 0.5
DEFAULT_HUMANIZE = True
DEFAULT_VM_MODE = True
DEFAULT_BROWSER = "none"
COUNTDOWN_SECONDS = 3

# ============================================================
# TYPING PATTERNS
# ============================================================
TYPING_PATTERNS = {
    "Steady": {
        "description": "Consistent speed, no variance — like a machine",
        "speed_variance": (1.0, 1.0),
        "punctuation_multiplier": 1.0,
        "newline_multiplier": 1.0,
        "error_rate": 0.0,
        "burst_chance": 0.0,
        "pause_chance": 0.0,
    },
    "Programmer": {
        "description": "Fast on keywords, slower on symbols, thinking pauses",
        "speed_variance": (0.5, 1.4),
        "punctuation_multiplier": 1.5,
        "newline_multiplier": 1.8,
        "error_rate": 0.005,
        "burst_chance": 0.15,
        "pause_chance": 0.02,
    },
    "Writer": {
        "description": "Smooth flow, pauses at sentence ends",
        "speed_variance": (0.7, 1.3),
        "punctuation_multiplier": 2.0,
        "newline_multiplier": 2.5,
        "error_rate": 0.008,
        "burst_chance": 0.05,
        "pause_chance": 0.03,
    },
    "Fast Burst": {
        "description": "Very fast with intermittent pauses, like copy-typing",
        "speed_variance": (0.3, 1.0),
        "punctuation_multiplier": 0.8,
        "newline_multiplier": 1.2,
        "error_rate": 0.01,
        "burst_chance": 0.4,
        "pause_chance": 0.05,
    },
    "Hunt & Peck": {
        "description": "Slow and deliberate, like a beginner",
        "speed_variance": (1.2, 2.5),
        "punctuation_multiplier": 2.5,
        "newline_multiplier": 3.0,
        "error_rate": 0.02,
        "burst_chance": 0.0,
        "pause_chance": 0.08,
    },
}

# ============================================================
# THEMES
# ============================================================
THEMES = {
    "Midnight": {
        "bg": "#0f0f1a",
        "sidebar": "#181825",
        "editor": "#11111b",
        "accent": "#3498db",
        "accent_hover": "#2980b9",
        "text": "#cdd6f4",
        "text_dim": "#6c7086",
        "success": "#2ecc71",
        "warning": "#f39c12",
        "danger": "#e74c3c",
        "border": "#313244",
        "card": "#1e1e2e",
        "highlight": "#45475a",
    },
    "Catppuccin": {
        "bg": "#1e1e2e",
        "sidebar": "#181825",
        "editor": "#11111b",
        "accent": "#cba6f7",
        "accent_hover": "#b4befe",
        "text": "#cdd6f4",
        "text_dim": "#6c7086",
        "success": "#a6e3a1",
        "warning": "#f9e2af",
        "danger": "#f38ba8",
        "border": "#313244",
        "card": "#1e1e2e",
        "highlight": "#45475a",
    },
    "Ocean": {
        "bg": "#0a192f",
        "sidebar": "#0d2137",
        "editor": "#071320",
        "accent": "#64ffda",
        "accent_hover": "#4ad4b0",
        "text": "#e6f1ff",
        "text_dim": "#8892b0",
        "success": "#64ffda",
        "warning": "#ffd866",
        "danger": "#ff6b6b",
        "border": "#1d3557",
        "card": "#112240",
        "highlight": "#233554",
    },
    "Monokai": {
        "bg": "#272822",
        "sidebar": "#1e1f1c",
        "editor": "#1a1b18",
        "accent": "#a6e22e",
        "accent_hover": "#8bc421",
        "text": "#f8f8f2",
        "text_dim": "#75715e",
        "success": "#a6e22e",
        "warning": "#e6db74",
        "danger": "#f92672",
        "border": "#3e3d32",
        "card": "#2d2e27",
        "highlight": "#49483e",
    },
    "Cyberpunk": {
        "bg": "#0d0221",
        "sidebar": "#150530",
        "editor": "#0a0118",
        "accent": "#ff2a6d",
        "accent_hover": "#d1235a",
        "text": "#d1f7ff",
        "text_dim": "#7b6995",
        "success": "#05d9e8",
        "warning": "#ff9100",
        "danger": "#ff2a6d",
        "border": "#2a1052",
        "card": "#1a0a3e",
        "highlight": "#2d1b69",
    },
    "Light": {
        "bg": "#f5f5f5",
        "sidebar": "#e8e8e8",
        "editor": "#ffffff",
        "accent": "#2563eb",
        "accent_hover": "#1d4ed8",
        "text": "#1e293b",
        "text_dim": "#64748b",
        "success": "#16a34a",
        "warning": "#d97706",
        "danger": "#dc2626",
        "border": "#d1d5db",
        "card": "#ffffff",
        "highlight": "#e2e8f0",
    },
}

DEFAULT_THEME = "Midnight"

# ============================================================
# BROWSER EXECUTABLES
# ============================================================
BROWSERS = {
    "none": None,
    "edge": "microsoft-edge",
    "chrome": "google-chrome",
    "firefox": "firefox",
}

# ============================================================
# DATA FILE INITIALIZATION
# ============================================================
def init_data_files():
    """
    Initialize all JSON data files if they don't exist.
    This ensures data persists across sessions.
    """
    # History
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "w") as f:
            json.dump([], f)

    # Settings
    if not os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "w") as f:
            json.dump({
                "theme": DEFAULT_THEME,
                "speed": DEFAULT_SPEED,
                "humanize": DEFAULT_HUMANIZE,
                "vm_mode": DEFAULT_VM_MODE,
                "browser": DEFAULT_BROWSER,
                "pattern": "Programmer",
                "error_simulation": False,
                "clipboard_mode": False,
                "window_geometry": "1200x800",
            }, f, indent=2)

    # Profiles — only create defaults if file doesn't exist
    if not os.path.exists(PROFILES_FILE):
        with open(PROFILES_FILE, "w") as f:
            json.dump({
                "🚀 Fast Code": {
                    "speed": 0.015,
                    "humanize": True,
                    "vm_mode": True,
                    "pattern": "Programmer",
                    "error_simulation": False,
                    "clipboard_mode": False,
                    "browser": "none",
                },
                "🎓 Lecture Demo": {
                    "speed": 0.06,
                    "humanize": True,
                    "vm_mode": True,
                    "pattern": "Writer",
                    "error_simulation": True,
                    "clipboard_mode": False,
                    "browser": "none",
                },
                "⚡ Blitz Paste": {
                    "speed": 0.005,
                    "humanize": False,
                    "vm_mode": True,
                    "pattern": "Fast Burst",
                    "error_simulation": False,
                    "clipboard_mode": False,
                    "browser": "none",
                },
            }, f, indent=2)

    # Snippets — only create defaults if file doesn't exist
    if not os.path.exists(SNIPPETS_FILE):
        from datetime import datetime
        with open(SNIPPETS_FILE, "w") as f:
            json.dump([
                {
                    "name": "Python Main",
                    "code": 'if __name__ == "__main__":\n    main()\n',
                    "language": "python",
                    "created": datetime.now().isoformat(),
                },
                {
                    "name": "Java Hello World",
                    "code": 'public class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello, World!");\n    }\n}\n',
                    "language": "java",
                    "created": datetime.now().isoformat(),
                },
                {
                    "name": "HTML Boilerplate",
                    "code": '<!DOCTYPE html>\n<html lang="en">\n<head>\n    <meta charset="UTF-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <title>Document</title>\n</head>\n<body>\n    \n</body>\n</html>\n',
                    "language": "html",
                    "created": datetime.now().isoformat(),
                },
            ], f, indent=2)

# Run on import — initialize data files
init_data_files()

# ============================================================
# SETTINGS PERSISTENCE
# ============================================================
def load_settings():
    """Load settings from disk, return defaults if missing."""
    defaults = {
        "theme": DEFAULT_THEME,
        "speed": DEFAULT_SPEED,
        "humanize": DEFAULT_HUMANIZE,
        "vm_mode": DEFAULT_VM_MODE,
        "browser": DEFAULT_BROWSER,
        "pattern": "Programmer",
        "error_simulation": False,
        "clipboard_mode": False,
        "window_geometry": "1200x800",
    }
    try:
        with open(SETTINGS_FILE, "r") as f:
            saved = json.load(f)
            defaults.update(saved)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return defaults

def save_settings(settings: dict):
    """Persist settings to disk."""
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=2)
    except Exception:
        pass
