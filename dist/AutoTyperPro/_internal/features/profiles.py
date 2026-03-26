"""
Auto Typer Pro — Profiles Manager
Save/load complete typing configurations. Data persists in ~/.auto_typer/profiles.json
"""
import json
import logging
from config import PROFILES_FILE

logger = logging.getLogger("AutoTyper.Profiles")


def load_profiles() -> dict:
    """Load all profiles from disk. File is guaranteed to exist by config.init_data_files()."""
    try:
        with open(PROFILES_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_profiles(profiles: dict):
    """Save all profiles to disk."""
    try:
        with open(PROFILES_FILE, "w") as f:
            json.dump(profiles, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save profiles: {e}")


def save_profile(name: str, config: dict):
    """Save or update a single profile."""
    profiles = load_profiles()
    profiles[name] = config
    save_profiles(profiles)


def delete_profile(name: str):
    """Delete a profile by name."""
    profiles = load_profiles()
    profiles.pop(name, None)
    save_profiles(profiles)
