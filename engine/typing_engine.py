"""
Auto Typer Pro — Cross-Platform Typing Engine
Supports Windows, macOS, and Linux. Auto-detects the best typing method per platform.
"""
import time
import random
import subprocess
import platform
import logging
from threading import Thread, Event
from pynput.keyboard import Controller, Key

from config import TYPING_PATTERNS, BROWSERS, COUNTDOWN_SECONDS

logger = logging.getLogger("AutoTyper.Engine")

# Detect platform once
PLATFORM = platform.system()  # "Windows", "Darwin", "Linux"


def _has_xdotool() -> bool:
    """Check if xdotool is available (Linux only)."""
    if PLATFORM != "Linux":
        return False
    try:
        subprocess.run(["xdotool", "--version"], capture_output=True, timeout=2)
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _clipboard_copy(text: str):
    """Cross-platform clipboard copy."""
    try:
        import pyperclip
        pyperclip.copy(text)
        return True
    except Exception:
        pass

    # Platform-specific fallbacks
    try:
        if PLATFORM == "Linux":
            p = subprocess.Popen(["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE)
            p.communicate(text.encode())
            return True
        elif PLATFORM == "Darwin":
            p = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
            p.communicate(text.encode())
            return True
        elif PLATFORM == "Windows":
            p = subprocess.Popen(["clip"], stdin=subprocess.PIPE, shell=True)
            p.communicate(text.encode())
            return True
    except Exception:
        pass
    return False


# Check xdotool once at startup
HAS_XDOTOOL = _has_xdotool()


class TypingEngine:
    """
    Cross-platform typing engine.
    - Linux: xdotool (VM-safe) → pynput fallback
    - Windows: pyautogui → pynput fallback
    - macOS: pyautogui → pynput fallback
    """

    def __init__(self):
        self.kb = Controller()
        self.pause_event = Event()
        self.stop_event = Event()
        self.typing_active = False

        # Progress
        self.typed_chars = 0
        self.total_chars = 0
        self.start_time = 0
        self.elapsed_time = 0
        self.errors_simulated = 0

        # Speed history
        self.speed_samples = []
        self._sample_interval = 20
        self._last_sample_time = 0
        self._last_sample_chars = 0

        # Callbacks (set by UI)
        self.on_progress = None    # fn(typed, total, elapsed, eta_secs)
        self.on_status = None      # fn(text, color)
        self.on_finish = None      # fn(status, stats_dict)
        self.on_char_typed = None  # fn(char)

        self.pause_event.set()

        logger.info(f"Engine initialized | Platform: {PLATFORM} | xdotool: {HAS_XDOTOOL}")

    # =====================================================
    # PUBLIC API
    # =====================================================

    def start(self, code: str, config: dict):
        if self.typing_active:
            return

        self.stop_event.clear()
        self.pause_event.clear()
        self.typing_active = True
        self.typed_chars = 0
        self.total_chars = len(code)
        self.errors_simulated = 0
        self.speed_samples = []
        self.start_time = time.time()
        self._last_sample_time = self.start_time
        self._last_sample_chars = 0

        Thread(target=self._engine_loop, args=(code, config), daemon=True).start()

    def pause(self):
        if self.typing_active:
            self.pause_event.clear()
            self._emit_status("⏸ PAUSED", "#e67e22")

    def resume(self):
        self.pause_event.set()

    def stop(self):
        self.stop_event.set()
        self.pause_event.set()

    # =====================================================
    # INTERNAL ENGINE
    # =====================================================

    def _engine_loop(self, code: str, config: dict):
        base_gap = config.get("speed", 0.03)
        humanize = config.get("humanize", True)
        pattern_name = config.get("pattern", "Programmer")
        error_sim = config.get("error_simulation", False)
        clipboard_mode = config.get("clipboard_mode", False)
        url = config.get("url", "")
        browser = config.get("browser", "none")

        pattern = TYPING_PATTERNS.get(pattern_name, TYPING_PATTERNS["Programmer"])

        # --- Browser launch ---
        if url and browser != "none":
            self._launch_browser(browser, url)

        # --- Wait for INSERT ---
        self._emit_status("⏸ PRESS INSERT TO BEGIN", "#d35400")
        if not self._check_pause(initial=True):
            return self._finish("STOPPED")

        # --- Clipboard paste mode ---
        if clipboard_mode:
            self._clipboard_paste(code)
            return self._finish("✅ DONE")

        # --- Main character loop ---
        last_gui_update = time.time()

        for i, char in enumerate(code):
            if not self._check_pause():
                return self._finish("STOPPED")

            if error_sim and char.isalpha() and random.random() < pattern["error_rate"]:
                self._simulate_error(char, base_gap)

            if humanize and random.random() < pattern["pause_chance"]:
                time.sleep(random.uniform(0.5, 2.0))

            self._type_char(char)
            if self.on_char_typed:
                self.on_char_typed(char)

            delay = self._calculate_delay(char, base_gap, humanize, pattern)
            time.sleep(delay)

            self.typed_chars += 1

            if self.typed_chars % self._sample_interval == 0:
                self._record_speed_sample()

            now = time.time()
            if now - last_gui_update > 0.5 or self.typed_chars == self.total_chars:
                self.elapsed_time = now - self.start_time
                eta = self._estimate_eta(base_gap, pattern)
                if self.on_progress:
                    self.on_progress(self.typed_chars, self.total_chars, self.elapsed_time, eta)
                last_gui_update = now

        self._finish("✅ DONE")

    # =====================================================
    # CROSS-PLATFORM TYPING
    # =====================================================

    def _type_char(self, char: str):
        """Send a single character — auto-selects method based on platform."""
        if char == '\n':
            self.kb.press(Key.enter)
            self.kb.release(Key.enter)
        elif char == '\t':
            self.kb.press(Key.tab)
            self.kb.release(Key.tab)
        else:
            if PLATFORM == "Linux" and HAS_XDOTOOL:
                # xdotool is the most reliable on Linux VMs
                try:
                    subprocess.run(['xdotool', 'type', '--clearmodifiers', char],
                                   timeout=2, capture_output=True)
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    self.kb.type(char)
            elif PLATFORM == "Windows":
                try:
                    import pyautogui
                    pyautogui.write(char, interval=0)
                except Exception:
                    self.kb.type(char)
            elif PLATFORM == "Darwin":
                try:
                    import pyautogui
                    pyautogui.write(char, interval=0)
                except Exception:
                    self.kb.type(char)
            else:
                # Pure pynput fallback (any OS)
                self.kb.type(char)

    def _simulate_error(self, correct_char: str, base_gap: float):
        """Type a wrong character, pause, backspace."""
        wrong = chr(ord(correct_char) + random.choice([-1, 1, 2, -2]))
        if wrong.isprintable():
            self._type_char(wrong)
            time.sleep(base_gap * random.uniform(1.5, 3.0))
            self.kb.press(Key.backspace)
            self.kb.release(Key.backspace)
            time.sleep(base_gap * random.uniform(0.5, 1.0))
            self.errors_simulated += 1

    def _clipboard_paste(self, code: str):
        """Cross-platform clipboard paste."""
        try:
            if not _clipboard_copy(code):
                raise RuntimeError("Failed to copy to clipboard")
            time.sleep(0.3)

            # Ctrl+V (or Cmd+V on macOS)
            if PLATFORM == "Darwin":
                self.kb.press(Key.cmd)
                self.kb.press('v')
                self.kb.release('v')
                self.kb.release(Key.cmd)
            else:
                self.kb.press(Key.ctrl)
                self.kb.press('v')
                self.kb.release('v')
                self.kb.release(Key.ctrl)

            self.typed_chars = self.total_chars
            if self.on_progress:
                self.on_progress(self.total_chars, self.total_chars, 0, 0)
        except Exception as e:
            logger.error(f"Clipboard paste failed: {e}")
            self._emit_status("⚠ Clipboard paste failed", "#e74c3c")

    # =====================================================
    # CROSS-PLATFORM BROWSER LAUNCH
    # =====================================================

    def _launch_browser(self, browser: str, url: str):
        """Launch browser on any platform."""
        exe = BROWSERS.get(browser)
        if not exe:
            return

        try:
            if PLATFORM == "Windows":
                import os
                os.startfile(url)
            elif PLATFORM == "Darwin":
                subprocess.Popen(["open", "-a", exe, url])
            else:
                subprocess.Popen([exe, url])
        except Exception as e:
            self._emit_status(f"⚠ Browser failed: {e}", "#e74c3c")

        for i in range(5, 0, -1):
            if self.stop_event.is_set():
                return
            self._emit_status(f"⏳ Browser opening... {i}s", "#f39c12")
            time.sleep(1)

    # =====================================================
    # DELAY / PAUSE / ETA
    # =====================================================

    def _calculate_delay(self, char: str, base_gap: float, humanize: bool, pattern: dict) -> float:
        delay = base_gap
        if not humanize:
            return delay

        lo, hi = pattern["speed_variance"]
        delay *= random.uniform(lo, hi)

        if char in ' .,:;!?(){}[]':
            delay *= pattern["punctuation_multiplier"]
        if char == '\n':
            delay *= pattern["newline_multiplier"]
        if random.random() < pattern["burst_chance"]:
            delay *= 0.3

        return max(0.001, delay)

    def _check_pause(self, initial=False):
        if not self.pause_event.is_set() or initial:
            status = "⏸ WAITING... (Press Insert)" if initial else "⏸ PAUSED"
            self._emit_status(status, "#d35400")

            while True:
                self.pause_event.wait()
                if self.stop_event.is_set():
                    return False

                aborted = False
                for i in range(COUNTDOWN_SECONDS, 0, -1):
                    if self.stop_event.is_set():
                        return False
                    if not self.pause_event.is_set():
                        aborted = True
                        break
                    label = "Starting" if initial else "Resuming"
                    self._emit_status(f"⏳ {label} in {i}s...", "#f39c12")
                    time.sleep(1)

                if not aborted:
                    self._emit_status("⌨ TYPING ACTIVE", "#2ecc71")
                    return True
        return True

    def _estimate_eta(self, base_gap: float, pattern: dict) -> float:
        remaining = self.total_chars - self.typed_chars
        if self.elapsed_time > 0 and self.typed_chars > 0:
            return remaining * (self.elapsed_time / self.typed_chars)
        return remaining * base_gap

    def _record_speed_sample(self):
        now = time.time()
        dt = now - self._last_sample_time
        dc = self.typed_chars - self._last_sample_chars
        if dt > 0:
            self.speed_samples.append((now - self.start_time, dc / dt))
        self._last_sample_time = now
        self._last_sample_chars = self.typed_chars

    def _finish(self, status: str):
        self.typing_active = False
        self.elapsed_time = time.time() - self.start_time if self.start_time else 0
        stats = {
            "typed_chars": self.typed_chars,
            "total_chars": self.total_chars,
            "elapsed_time": self.elapsed_time,
            "errors_simulated": self.errors_simulated,
            "speed_samples": self.speed_samples,
            "avg_cps": self.typed_chars / self.elapsed_time if self.elapsed_time > 0 else 0,
            "avg_wpm": (self.typed_chars / 5) / (self.elapsed_time / 60) if self.elapsed_time > 0 else 0,
        }
        if self.on_finish:
            self.on_finish(status, stats)

    def _emit_status(self, text: str, color: str):
        if self.on_status:
            self.on_status(text, color)

    def get_live_stats(self) -> dict:
        elapsed = time.time() - self.start_time if self.start_time and self.typing_active else self.elapsed_time
        cps = self.typed_chars / elapsed if elapsed > 0 else 0
        wpm = (self.typed_chars / 5) / (elapsed / 60) if elapsed > 0 else 0
        return {
            "typed": self.typed_chars,
            "total": self.total_chars,
            "elapsed": elapsed,
            "cps": round(cps, 1),
            "wpm": round(wpm, 1),
            "errors": self.errors_simulated,
            "progress": self.typed_chars / self.total_chars if self.total_chars > 0 else 0,
        }
