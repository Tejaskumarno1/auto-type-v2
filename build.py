#!/usr/bin/env python3
"""
Auto Typer Pro — Build Script
Creates a standalone desktop application using PyInstaller.

Usage:
    python build.py          # Build standalone app
    python build.py --onefile  # Build as single .exe file (slower start, easier sharing)

Outputs:
    dist/AutoTyperPro/       # Standalone app folder (default)
    dist/AutoTyperPro        # Single executable (with --onefile)
"""
import subprocess
import sys
import platform
import os

APP_NAME = "AutoTyperPro"


def build():
    onefile = "--onefile" in sys.argv

    # Collect all source modules
    hidden_imports = [
        "customtkinter",
        "pynput",
        "pynput.keyboard",
        "pynput.keyboard._xorg",
        "pynput.keyboard._win32",
        "pynput.keyboard._darwin",
        "pynput._util",
        "pynput._util.xorg",
        "pynput._util.win32",
        "pynput._util.darwin",
        "pyautogui",
        "pyperclip",
        "PIL",
        "Pygments",
        "pystray",
        "config",
        "engine",
        "engine.typing_engine",
        "features",
        "features.profiles",
        "features.snippets",
        "features.history",
        "features.scheduler",
        "features.analytics",
        "ui",
        "ui.app",
        "ui.overlay",
        "ui.widgets",
        "ui.dialogs",
    ]

    # Data files (customtkinter themes etc.)
    import customtkinter
    ctk_path = os.path.dirname(customtkinter.__file__)

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", APP_NAME,
        "--windowed",  # No console window
        "--noconfirm",
        "--clean",
        f"--add-data={ctk_path}:customtkinter",
        "--add-data=config.py:.",
        "--add-data=engine:engine",
        "--add-data=features:features",
        "--add-data=ui:ui",
    ]

    for imp in hidden_imports:
        cmd.extend(["--hidden-import", imp])

    if onefile:
        cmd.append("--onefile")

    # Platform-specific
    system = platform.system()
    if system == "Linux":
        cmd.extend(["--hidden-import", "pynput.keyboard._xorg"])
    elif system == "Windows":
        cmd.extend(["--hidden-import", "pynput.keyboard._win32"])
    elif system == "Darwin":
        cmd.extend(["--hidden-import", "pynput.keyboard._darwin"])

    cmd.append("main.py")

    print(f"🔨 Building {APP_NAME} for {system}...")
    print(f"   Mode: {'Single File' if onefile else 'One Folder'}")
    print(f"   Command: {' '.join(cmd)}")
    print()

    result = subprocess.run(cmd)

    if result.returncode == 0:
        if onefile:
            suffix = ".exe" if system == "Windows" else ""
            path = f"dist/{APP_NAME}{suffix}"
        else:
            path = f"dist/{APP_NAME}/"
        print(f"\n✅ Build successful!")
        print(f"   Output: {path}")
        if system == "Linux" and not onefile:
            print(f"\n   Run: ./dist/{APP_NAME}/{APP_NAME}")
        elif system == "Windows":
            print(f"\n   Run: dist\\{APP_NAME}\\{APP_NAME}.exe")
        elif system == "Darwin":
            print(f"\n   Run: open dist/{APP_NAME}.app (if bundled) or ./dist/{APP_NAME}/{APP_NAME}")
    else:
        print(f"\n❌ Build failed with code {result.returncode}")
        sys.exit(1)


if __name__ == "__main__":
    build()
