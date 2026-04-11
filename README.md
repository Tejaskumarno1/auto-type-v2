# ⌨️ Auto Typer Pro v2.1 — Senior Dev Edition

**Auto Typer Pro** is a professional-grade desktop application designed for automated typing with a focus on human-like behavior, cross-platform reliability, and advanced productivity features.

![Version](https://img.shields.io/badge/version-2.1-blue.svg)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

---

## 🚀 Key Features

-   **🎭 Humanized Typing**: Configurable patterns (Programmer, Writer, etc.) with random delays, bursts, and thinking pauses.
-   **✏️ Error Simulation**: Automatically simulates and corrects typos for extra realism.
-   **📥 Snippet Library**: Store and quickly insert frequently used code blocks or text.
-   **👤 Profiles**: Save and load custom configurations (speed, patterns, browser targets).
-   **⏰ Scheduler**: Set a delay or a specific time to trigger the typing engine.
-   **🌐 Browser Target**: Integrated browser launcher that auto-opens URLs before typing.
-   **🎨 Gorgeous UI**: Modern interface with multiple themes (Midnight, Monokai, Cyberpunk, etc.).
-   **🖥️ VM & Linux Optimized**: Uses `xdotool` fallback for rock-solid performance in virtual environments.

---

## 🛠️ Installation (New System Guide)

Follow these steps to set up Auto Typer Pro on a fresh Linux installation (Ubuntu/Debian).

### Linux Setup (Ubuntu/Debian)
Open your terminal and run:
```bash
sudo apt update
sudo apt install -y python3-tk xclip xdotool libx11-dev
```

### Windows Setup
1.  **Install Python**: Download from [python.org](https://www.python.org/) (ensure "Add to PATH" is checked).
2.  **Open Terminal**: Use PowerShell or CMD as Administrator.
3.  **Install**: No extra system dependencies needed! Just follow the Python setup below.

### macOS Setup
1.  **Install Homebrew**: (Recommended) `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
2.  **Install Python**: `brew install python`
3.  **Permissions**: You must grant **Accessibility Permissions** to your Terminal application (System Settings > Privacy & Security > Accessibility) to allow the app to simulate typing.

---

### Python Environment (All Platforms)
Navigate to the project directory and run:

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

---

## 📖 How to Use

### 1. Launch the App
With your virtual environment active, run:
```bash
python3 main.py
```

### 2. Prepare Your Text
-   Type or paste your code/text into the **Main Editor**.
-   Alternatively, use **📂 Load File** to import a script from your disk.
-   (Optional) Enter a **🌐 Target URL** and select a browser if you want the app to open a website for you.

### 3. Configure the Engine
-   **⚡ Speed**: Adjust the slider to set your base typing speed (seconds per character).
-   **🎭 Pattern**: Select a pattern like "Programmer" (adds pauses after keywords) or "Steady" (constant speed).
-   **🔧 Options**: Toggle "Humanize Speed" or "Simulate Typos" based on your needs.

### 4. Start Typing
1.  Click the **▶ START TYPING** button. 
2.  The app will enter a **Waiting State**.
3.  Switch focus to your target window (e.g., Code Editor, Browser, Terminal).
4.  **Press `INSERT`** on your keyboard to begin the typing sequence.

---

## ⌨️ Advanced Controls & Hotkeys

| Key | Action |
| :--- | :--- |
| **INSERT** | **Start / Resume** typing after switching windows. |
| **ESC** | **Pause** the typing engine immediately. |
| **Ctrl + O** | Load a file directly into the editor. |

---

## 📁 Data Storage
All your profiles, snippets, and history are stored locally in:
`~/.auto_typer/`

- `settings.json`: Main app preferences.
- `profiles.json`: Your saved typing presets.
- `snippets.json`: Your personal code library.
- `history.json`: Aggregate stats and session logs.

---

## ⚠️ Troubleshooting (Linux)

-   **Wayland vs X11**: Some automation features may require X11. If typing isn't working on modern distros (like Ubuntu 22.04+), try logging in with the "Ubuntu on Xorg" session.
-   **Permissions**: If you get a "Permission Denied" error for `xdotool`, ensure it is installed correctly (`sudo apt install xdotool`).
-   **Focus Issues**: Remember that the app waits for you to switch to the target window and press **INSERT**. This ensures you don't accidentally type into the wrong window.

---

*Enjoy typing at the speed of thought (or slightly slower for realism)!*
