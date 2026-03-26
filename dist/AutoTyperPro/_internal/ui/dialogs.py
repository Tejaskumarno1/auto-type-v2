"""
Auto Typer Pro — Modal Dialogs
Profile save dialog, session summary popup, snippet editor, scheduler.
Fixed: proper theming so widgets are visible on dark backgrounds.
"""
import customtkinter as ctk


def _safe_grab(dialog):
    """Safely attempt grab_set — fails silently on Linux WMs that don't support it."""
    try:
        if dialog.winfo_exists() and dialog.winfo_viewable():
            dialog.grab_set()
    except Exception:
        pass  # Dialog works fine without grab


class ProfileSaveDialog(ctk.CTkToplevel):
    """Dialog for saving a new profile — with visible themed widgets."""

    def __init__(self, parent, on_save=None):
        super().__init__(parent)
        self.title("Save Profile")
        self.geometry("420x220")
        self.attributes("-topmost", True)
        self.resizable(False, False)
        self.on_save = on_save
        self.configure(fg_color="#1e1e2e")

        self.transient(parent)
        self.after(300, lambda: _safe_grab(self))

        ctk.CTkLabel(self, text="💾  Save Current Configuration",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color="#cdd6f4").pack(pady=(25, 15))

        ctk.CTkLabel(self, text="Profile Name:", font=ctk.CTkFont(size=12),
                     text_color="#6c7086", anchor="w").pack(padx=40, anchor="w")

        self.name_entry = ctk.CTkEntry(self, placeholder_text="e.g. My Fast Config...",
                                        width=340, height=42,
                                        font=ctk.CTkFont(size=14),
                                        fg_color="#11111b",
                                        border_color="#3498db",
                                        text_color="#cdd6f4",
                                        placeholder_text_color="#6c7086")
        self.name_entry.pack(pady=(5, 15), padx=40)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=(5, 20))

        ctk.CTkButton(btn_frame, text="💾  Save Profile", fg_color="#2ecc71",
                      hover_color="#27ae60", width=150, height=38,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      corner_radius=8,
                      command=self._save).pack(side="left", padx=8)
        ctk.CTkButton(btn_frame, text="Cancel", fg_color="#45475a",
                      hover_color="#585b70", width=120, height=38,
                      font=ctk.CTkFont(size=13),
                      corner_radius=8,
                      text_color="#cdd6f4",
                      command=self.destroy).pack(side="left", padx=8)

        self.name_entry.focus_set()
        self.bind("<Return>", lambda e: self._save())

    def _save(self):
        name = self.name_entry.get().strip()
        if name and self.on_save:
            self.on_save(name)
        self.destroy()


class SessionSummaryDialog(ctk.CTkToplevel):
    """Post-session summary popup with stats."""

    def __init__(self, parent, summary: dict, theme: dict):
        super().__init__(parent)
        self.title("Session Complete")
        self.geometry("440x380")
        self.attributes("-topmost", True)
        self.resizable(False, False)
        self.transient(parent)
        self.configure(fg_color=theme["bg"])

        # Header
        status = summary.get("status", "Done")
        color = theme["success"] if "Completed" in status else theme["danger"]
        ctk.CTkLabel(self, text=status, font=ctk.CTkFont(size=24, weight="bold"),
                     text_color=color).pack(pady=(25, 15))

        # Stats
        stats_frame = ctk.CTkFrame(self, fg_color=theme["card"], corner_radius=12,
                                    border_width=1, border_color=theme["border"])
        stats_frame.pack(padx=30, fill="x")

        rows = [
            ("⏱  Duration", summary.get("time_formatted", "—")),
            ("📝  Characters", summary.get("chars", "—")),
            ("📊  Completion", summary.get("completion", "—")),
            ("⚡  Speed", summary.get("speed", "—")),
            ("🔴  Errors Simulated", summary.get("errors", "0")),
        ]
        for i, (label, value) in enumerate(rows):
            ctk.CTkLabel(stats_frame, text=label, font=ctk.CTkFont(size=13),
                         text_color=theme["text_dim"], anchor="w").grid(
                row=i, column=0, sticky="w", padx=20, pady=7)
            ctk.CTkLabel(stats_frame, text=value, font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=theme["text"], anchor="e").grid(
                row=i, column=1, sticky="e", padx=20, pady=7)
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(self, text="Close", fg_color=theme["accent"],
                      hover_color=theme["accent_hover"], width=150, height=38,
                      font=ctk.CTkFont(size=14, weight="bold"),
                      corner_radius=8,
                      command=self.destroy).pack(pady=20)


class SnippetEditorDialog(ctk.CTkToplevel):
    """Dialog for adding/editing a code snippet."""

    def __init__(self, parent, on_save=None, name="", code="", language="python"):
        super().__init__(parent)
        self.title("Snippet Editor")
        self.geometry("520x450")
        self.attributes("-topmost", True)
        self.resizable(True, True)
        self.on_save = on_save
        self.configure(fg_color="#1e1e2e")

        self.transient(parent)
        self.after(300, lambda: _safe_grab(self))

        ctk.CTkLabel(self, text="📋  Edit Snippet",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color="#cdd6f4").pack(pady=(15, 10))

        # Name
        name_frame = ctk.CTkFrame(self, fg_color="transparent")
        name_frame.pack(fill="x", padx=25, pady=5)
        ctk.CTkLabel(name_frame, text="Name:", width=60, text_color="#6c7086",
                     font=ctk.CTkFont(size=12)).pack(side="left")
        self.name_entry = ctk.CTkEntry(name_frame, placeholder_text="Snippet name...",
                                        fg_color="#11111b", border_color="#313244",
                                        text_color="#cdd6f4")
        self.name_entry.pack(side="left", fill="x", expand=True, padx=5)
        if name:
            self.name_entry.insert(0, name)

        # Language
        lang_frame = ctk.CTkFrame(self, fg_color="transparent")
        lang_frame.pack(fill="x", padx=25, pady=5)
        ctk.CTkLabel(lang_frame, text="Lang:", width=60, text_color="#6c7086",
                     font=ctk.CTkFont(size=12)).pack(side="left")
        self.lang_entry = ctk.CTkEntry(lang_frame, placeholder_text="python",
                                        fg_color="#11111b", border_color="#313244",
                                        text_color="#cdd6f4")
        self.lang_entry.pack(side="left", fill="x", expand=True, padx=5)
        if language:
            self.lang_entry.insert(0, language)

        # Code
        self.code_text = ctk.CTkTextbox(self, font=ctk.CTkFont(family="Consolas", size=13),
                                         wrap="none", height=220,
                                         fg_color="#11111b", text_color="#cdd6f4",
                                         scrollbar_button_color="#313244")
        self.code_text.pack(fill="both", expand=True, padx=25, pady=8)
        if code:
            self.code_text.insert("1.0", code)

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=12)
        ctk.CTkButton(btn_frame, text="💾  Save", fg_color="#2ecc71",
                      hover_color="#27ae60", width=130, height=38,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      corner_radius=8,
                      command=self._save).pack(side="left", padx=8)
        ctk.CTkButton(btn_frame, text="Cancel", fg_color="#45475a",
                      hover_color="#585b70", width=110, height=38,
                      font=ctk.CTkFont(size=13), corner_radius=8,
                      text_color="#cdd6f4",
                      command=self.destroy).pack(side="left", padx=8)

    def _save(self):
        name = self.name_entry.get().strip()
        code = self.code_text.get("1.0", "end").rstrip()
        lang = self.lang_entry.get().strip() or "python"
        if name and code and self.on_save:
            self.on_save(name, code, lang)
        self.destroy()


class SchedulerDialog(ctk.CTkToplevel):
    """Dialog for scheduling a delayed start."""

    def __init__(self, parent, on_schedule=None):
        super().__init__(parent)
        self.title("Schedule Typing")
        self.geometry("400x300")
        self.attributes("-topmost", True)
        self.resizable(False, False)
        self.on_schedule = on_schedule
        self.configure(fg_color="#1e1e2e")

        self.transient(parent)
        self.after(300, lambda: _safe_grab(self))

        ctk.CTkLabel(self, text="⏰  Schedule Typing Start",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color="#cdd6f4").pack(pady=(20, 15))

        # Delay option
        delay_frame = ctk.CTkFrame(self, fg_color="#11111b", corner_radius=10)
        delay_frame.pack(fill="x", padx=30, pady=5)
        inner1 = ctk.CTkFrame(delay_frame, fg_color="transparent")
        inner1.pack(fill="x", padx=15, pady=12)
        ctk.CTkLabel(inner1, text="⏳  Start after (seconds):", text_color="#cdd6f4",
                     font=ctk.CTkFont(size=12)).pack(side="left")
        self.delay_entry = ctk.CTkEntry(inner1, width=80, placeholder_text="10",
                                         fg_color="#181825", border_color="#313244",
                                         text_color="#cdd6f4", justify="center")
        self.delay_entry.pack(side="right")
        self.delay_entry.insert(0, "10")

        # Time option
        time_frame = ctk.CTkFrame(self, fg_color="#11111b", corner_radius=10)
        time_frame.pack(fill="x", padx=30, pady=5)
        inner2 = ctk.CTkFrame(time_frame, fg_color="transparent")
        inner2.pack(fill="x", padx=15, pady=12)
        ctk.CTkLabel(inner2, text="🕐  Start at time (HH:MM):", text_color="#cdd6f4",
                     font=ctk.CTkFont(size=12)).pack(side="left")
        self.time_entry = ctk.CTkEntry(inner2, width=80, placeholder_text="14:30",
                                        fg_color="#181825", border_color="#313244",
                                        text_color="#cdd6f4", justify="center")
        self.time_entry.pack(side="right")

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=18)
        ctk.CTkButton(btn_frame, text="⏳  Start Delay", fg_color="#3498db",
                      hover_color="#2980b9", width=150, height=38,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      corner_radius=8,
                      command=self._schedule_delay).pack(side="left", padx=6)
        ctk.CTkButton(btn_frame, text="🕐  Start at Time", fg_color="#9b59b6",
                      hover_color="#8e44ad", width=150, height=38,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      corner_radius=8,
                      command=self._schedule_time).pack(side="left", padx=6)

    def _schedule_delay(self):
        try:
            secs = int(self.delay_entry.get())
            if secs > 0 and self.on_schedule:
                self.on_schedule("delay", secs)
            self.destroy()
        except ValueError:
            pass

    def _schedule_time(self):
        try:
            parts = self.time_entry.get().strip().split(":")
            h, m = int(parts[0]), int(parts[1])
            if 0 <= h <= 23 and 0 <= m <= 59 and self.on_schedule:
                self.on_schedule("time", (h, m))
            self.destroy()
        except (ValueError, IndexError):
            pass
