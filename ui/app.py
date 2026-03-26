"""
Auto Typer Pro v2.1 — Main Application Window
Senior Dev Edition — with live themes, wider sidebar, fixed scheduler, persistent data.
"""
import sys
import os
import logging
import customtkinter as ctk
from pynput import keyboard as pynput_keyboard

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    TYPING_PATTERNS, THEMES, DEFAULT_THEME,
    load_settings, save_settings, DEFAULT_SPEED, MIN_SPEED, MAX_SPEED
)
from engine.typing_engine import TypingEngine
from features.profiles import load_profiles, save_profile, delete_profile
from features.snippets import load_snippets, add_snippet, delete_snippet
from features.history import load_history, add_session, clear_history, get_aggregate_stats
from features.analytics import format_time, format_eta, calculate_session_summary
from features.scheduler import Scheduler
from ui.overlay import ActiveOverlay
from ui.widgets import Toast, StatCard, SectionLabel
from ui.dialogs import (
    ProfileSaveDialog, SessionSummaryDialog,
    SnippetEditorDialog, SchedulerDialog
)

logger = logging.getLogger("AutoTyper.App")

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class AutoTyperPro(ctk.CTk):
    """Main application window — v2.1 with all fixes."""

    SIDEBAR_WIDTH = 360  # Increased from 280

    def __init__(self):
        super().__init__()

        # Load saved settings
        self.settings = load_settings()
        self.current_theme_name = self.settings.get("theme", DEFAULT_THEME)
        self.theme = THEMES.get(self.current_theme_name, THEMES[DEFAULT_THEME])

        self.title("Auto Typer Pro v2.1 — Senior Dev Edition")
        geo = self.settings.get("window_geometry", "1250x850")
        # Only use saved geometry if it looks valid
        if "x" in geo and "+" not in geo:
            self.geometry(geo)
        else:
            self.geometry("1250x850")
        self.minsize(1050, 700)

        # Engine
        self.engine = TypingEngine()
        self.engine.on_progress = self._on_engine_progress
        self.engine.on_status = self._on_engine_status
        self.engine.on_finish = self._on_engine_finish
        self.engine.on_char_typed = self._on_char_typed

        # Scheduler
        self.scheduler = Scheduler()

        # Overlay
        self.overlay = ActiveOverlay(self, self.theme)

        # Config vars
        self.speed_var = ctk.DoubleVar(value=self.settings.get("speed", DEFAULT_SPEED))
        self.humanize_var = ctk.BooleanVar(value=self.settings.get("humanize", True))
        self.error_sim_var = ctk.BooleanVar(value=self.settings.get("error_simulation", False))
        self.clipboard_var = ctk.BooleanVar(value=self.settings.get("clipboard_mode", False))
        self.selected_browser = ctk.StringVar(value=self.settings.get("browser", "none"))
        self.selected_pattern = ctk.StringVar(value=self.settings.get("pattern", "Programmer"))
        self.word_wrap_var = ctk.BooleanVar(value=True)

        self._last_config = {}
        self._scheduler_active = False

        # Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.configure(fg_color=self.theme["bg"])

        self._build_sidebar()
        self._build_main_area()
        self._setup_hotkeys()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ======================================================================
    # LIVE THEME APPLICATION
    # ======================================================================
    def _apply_theme(self, name: str):
        """Apply theme live by rebuilding the entire UI."""
        self.current_theme_name = name
        self.theme = THEMES[name]
        self.settings["theme"] = name
        save_settings(self.settings)

        # Save current editor content + URL
        saved_code = self.code_text.get("1.0", "end").rstrip()
        saved_url = self.url_entry.get()

        # Destroy old UI
        for widget in self.winfo_children():
            widget.destroy()

        # Rebuild with new theme
        self.configure(fg_color=self.theme["bg"])
        self.overlay = ActiveOverlay(self, self.theme)

        self._build_sidebar()
        self._build_main_area()

        # Restore content
        if saved_code:
            self.code_text.insert("1.0", saved_code)
        if saved_url:
            self.url_entry.insert(0, saved_url)
        self._update_char_count()

    # ======================================================================
    # SIDEBAR — TABBED (WIDER)
    # ======================================================================
    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=self.SIDEBAR_WIDTH, corner_radius=0,
                                     fg_color=self.theme["sidebar"])
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(2, weight=1)
        self.sidebar.grid_propagate(False)

        # ─── HEADER ───────────────────────────────────────
        hdr = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 5))

        ctk.CTkLabel(hdr, text="⌨  Auto Typer Pro",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=self.theme["text"]).pack(anchor="w")
        ctk.CTkLabel(hdr, text="v2.1  •  ESC: Pause  |  INSERT: Resume",
                     font=ctk.CTkFont(size=11),
                     text_color=self.theme["text_dim"]).pack(anchor="w", pady=(2, 0))

        # ─── TAB BAR ──────────────────────────────────────
        tab_frame = ctk.CTkFrame(self.sidebar, fg_color=self.theme["bg"], corner_radius=10)
        tab_frame.grid(row=1, column=0, sticky="ew", padx=12, pady=8)
        tab_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        self.tab_buttons = {}
        tabs = [
            ("⚙", "controls", "Controls"),
            ("👤", "profiles", "Profiles"),
            ("📋", "snippets", "Snippets"),
            ("📜", "history", "History"),
            ("🎨", "settings", "Settings"),
        ]
        for i, (icon, key, tooltip) in enumerate(tabs):
            btn = ctk.CTkButton(tab_frame, text=f"{icon}", width=45, height=34,
                                corner_radius=8, font=ctk.CTkFont(size=16),
                                fg_color="transparent",
                                hover_color=self.theme["highlight"],
                                text_color=self.theme["text"],
                                command=lambda n=key: self._switch_tab(n))
            btn.grid(row=0, column=i, padx=2, pady=4)
            self.tab_buttons[key] = btn

        # ─── TAB CONTENT ──────────────────────────────────
        self.tab_container = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.tab_container.grid(row=2, column=0, sticky="nsew")
        self.tab_container.grid_columnconfigure(0, weight=1)
        self.tab_container.grid_rowconfigure(0, weight=1)

        self.tab_frames = {}
        self._build_controls_tab()
        self._build_profiles_tab()
        self._build_snippets_tab()
        self._build_history_tab()
        self._build_settings_tab()

        self._switch_tab("controls")

    def _switch_tab(self, name: str):
        for frame in self.tab_frames.values():
            frame.grid_forget()
        self.tab_frames[name].grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        for key, btn in self.tab_buttons.items():
            btn.configure(fg_color=self.theme["accent"] if key == name else "transparent",
                          text_color="white" if key == name else self.theme["text"])

        if name == "profiles":
            self._refresh_profiles()
        elif name == "snippets":
            self._refresh_snippets()
        elif name == "history":
            self._refresh_history()

    # ─── CONTROLS TAB ──────────────────────────────────
    def _build_controls_tab(self):
        frame = ctk.CTkScrollableFrame(self.tab_container, fg_color="transparent",
                                        scrollbar_button_color=self.theme["border"])
        self.tab_frames["controls"] = frame

        # Speed
        SectionLabel(frame, text="⚡ Typing Speed", text_color=self.theme["text"]).pack(anchor="w", pady=(10, 5))

        self.speed_slider = ctk.CTkSlider(frame, from_=MIN_SPEED, to=MAX_SPEED,
                                           variable=self.speed_var,
                                           command=self._on_slider_change,
                                           progress_color=self.theme["accent"],
                                           button_color=self.theme["accent"],
                                           button_hover_color=self.theme["accent_hover"])
        self.speed_slider.pack(fill="x", pady=(0, 5))

        speed_row = ctk.CTkFrame(frame, fg_color="transparent")
        speed_row.pack(fill="x", pady=(0, 10))
        self.speed_entry = ctk.CTkEntry(speed_row, width=80, justify="center", height=32,
                                         fg_color=self.theme["editor"],
                                         border_color=self.theme["border"])
        self.speed_entry.insert(0, f"{self.speed_var.get():.3f}")
        self.speed_entry.pack(side="left")
        self.speed_entry.bind("<Return>", self._on_entry_change)
        self.speed_entry.bind("<FocusOut>", self._on_entry_change)
        ctk.CTkLabel(speed_row, text="sec / char", text_color=self.theme["text_dim"],
                     font=ctk.CTkFont(size=12)).pack(side="left", padx=8)

        # Pattern
        SectionLabel(frame, text="🎭 Typing Pattern", text_color=self.theme["text"]).pack(anchor="w", pady=(5, 5))
        self.pattern_menu = ctk.CTkOptionMenu(
            frame, values=list(TYPING_PATTERNS.keys()),
            variable=self.selected_pattern,
            fg_color=self.theme["card"],
            button_color=self.theme["accent"],
            button_hover_color=self.theme["accent_hover"],
            dropdown_fg_color=self.theme["card"],
            dropdown_hover_color=self.theme["highlight"],
            dropdown_text_color=self.theme["text"],
            text_color=self.theme["text"],
            command=self._on_pattern_change)
        self.pattern_menu.pack(fill="x", pady=(0, 3))

        self.pattern_desc = ctk.CTkLabel(frame, text="", font=ctk.CTkFont(size=11),
                                          text_color=self.theme["text_dim"], wraplength=300,
                                          justify="left")
        self.pattern_desc.pack(anchor="w", pady=(0, 10))
        self._on_pattern_change(self.selected_pattern.get())

        # Options
        SectionLabel(frame, text="🔧 Engine Options", text_color=self.theme["text"]).pack(anchor="w", pady=(0, 5))
        toggles = [
            ("Humanize Speed", self.humanize_var),
            ("Simulate Typos", self.error_sim_var),
            ("Clipboard Paste", self.clipboard_var),
        ]
        for label, var in toggles:
            ctk.CTkCheckBox(frame, text=label, variable=var,
                            font=ctk.CTkFont(size=12),
                            checkbox_width=20, checkbox_height=20,
                            border_color=self.theme["border"],
                            fg_color=self.theme["accent"],
                            hover_color=self.theme["accent_hover"],
                            text_color=self.theme["text"]).pack(anchor="w", pady=3, padx=2)

        # Browser
        SectionLabel(frame, text="🌐 Browser Target", text_color=self.theme["text"]).pack(anchor="w", pady=(12, 5))
        self.browser_menu = ctk.CTkSegmentedButton(
            frame, values=["none", "edge", "chrome", "firefox"],
            variable=self.selected_browser,
            font=ctk.CTkFont(size=11),
            selected_color=self.theme["accent"],
            selected_hover_color=self.theme["accent_hover"],
            unselected_color=self.theme["card"],
            unselected_hover_color=self.theme["highlight"],
            text_color=self.theme["text"],
            text_color_disabled=self.theme["text_dim"])
        self.browser_menu.pack(fill="x", pady=(0, 12))

        # ─── CONTROL BUTTONS ──────────────────────────────
        SectionLabel(frame, text="🎮 Controls", text_color=self.theme["text"]).pack(anchor="w", pady=(0, 5))

        self.start_btn = ctk.CTkButton(frame, text="▶  START TYPING",
                                        fg_color=self.theme["success"],
                                        hover_color="#27ae60", height=42,
                                        font=ctk.CTkFont(size=15, weight="bold"),
                                        corner_radius=10,
                                        command=self._start_typing)
        self.start_btn.pack(fill="x", pady=4)

        btn_row = ctk.CTkFrame(frame, fg_color="transparent")
        btn_row.pack(fill="x", pady=3)
        btn_row.grid_columnconfigure((0, 1), weight=1)

        self.pause_btn = ctk.CTkButton(btn_row, text="⏸ Pause",
                                        fg_color=self.theme["warning"],
                                        text_color="black",
                                        hover_color="#d68910", height=36,
                                        font=ctk.CTkFont(size=13, weight="bold"),
                                        command=self._pause_typing, state="disabled")
        self.pause_btn.grid(row=0, column=0, padx=(0, 3), sticky="ew")

        self.resume_btn = ctk.CTkButton(btn_row, text="⏯ Resume",
                                         fg_color="#d35400",
                                         hover_color="#ba4a00", height=36,
                                         font=ctk.CTkFont(size=13, weight="bold"),
                                         command=self._resume_typing, state="disabled")
        self.resume_btn.grid(row=0, column=1, padx=(3, 0), sticky="ew")

        self.stop_btn = ctk.CTkButton(frame, text="⏹  STOP",
                                       fg_color=self.theme["danger"],
                                       hover_color="#922b21", height=36,
                                       font=ctk.CTkFont(size=13, weight="bold"),
                                       command=self._stop_typing, state="disabled")
        self.stop_btn.pack(fill="x", pady=4)

        # Schedule
        self.schedule_btn = ctk.CTkButton(frame, text="⏰  Schedule Start...",
                                           fg_color=self.theme["card"],
                                           border_width=1,
                                           border_color=self.theme["border"],
                                           hover_color=self.theme["highlight"],
                                           text_color=self.theme["text"], height=34,
                                           font=ctk.CTkFont(size=12),
                                           corner_radius=8,
                                           command=self._open_scheduler)
        self.schedule_btn.pack(fill="x", pady=(8, 3))

        # Schedule status label (visible during countdown)
        self.schedule_status_lbl = ctk.CTkLabel(frame, text="",
                                                  font=ctk.CTkFont(size=12, weight="bold"),
                                                  text_color=self.theme["warning"])
        self.schedule_status_lbl.pack(anchor="w", pady=(2, 5))

    # ─── PROFILES TAB ──────────────────────────────────
    def _build_profiles_tab(self):
        frame = ctk.CTkScrollableFrame(self.tab_container, fg_color="transparent",
                                        scrollbar_button_color=self.theme["border"])
        self.tab_frames["profiles"] = frame

        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x", pady=(10, 10))
        SectionLabel(header, text="👤 Typing Profiles", text_color=self.theme["text"]).pack(side="left")
        ctk.CTkButton(header, text="+ Save Current", width=120, height=30,
                      fg_color=self.theme["accent"],
                      hover_color=self.theme["accent_hover"],
                      font=ctk.CTkFont(size=12, weight="bold"),
                      corner_radius=8,
                      command=self._save_profile_dialog).pack(side="right")

        self.profiles_list_frame = ctk.CTkFrame(frame, fg_color="transparent")
        self.profiles_list_frame.pack(fill="both", expand=True)

    def _refresh_profiles(self):
        for w in self.profiles_list_frame.winfo_children():
            w.destroy()

        profiles = load_profiles()
        if not profiles:
            ctk.CTkLabel(self.profiles_list_frame, text="No profiles saved yet.\nClick '+ Save Current' to create one.",
                         text_color=self.theme["text_dim"], font=ctk.CTkFont(size=12),
                         justify="center").pack(pady=30)
            return

        for name, config in profiles.items():
            card = ctk.CTkFrame(self.profiles_list_frame, fg_color=self.theme["card"],
                                corner_radius=10, border_width=1, border_color=self.theme["border"])
            card.pack(fill="x", pady=4)

            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(fill="x", padx=12, pady=(10, 4))

            ctk.CTkLabel(info, text=name, font=ctk.CTkFont(size=14, weight="bold"),
                         text_color=self.theme["text"]).pack(anchor="w")

            pattern = config.get("pattern", "?")
            speed = config.get("speed", 0.03)
            err = "✏️ Typos" if config.get("error_simulation") else ""
            tags = f"{pattern}  •  {speed:.3f}s/char"
            if err:
                tags += f"  •  {err}"

            ctk.CTkLabel(info, text=tags, font=ctk.CTkFont(size=11),
                         text_color=self.theme["text_dim"]).pack(anchor="w")

            btn_row = ctk.CTkFrame(card, fg_color="transparent")
            btn_row.pack(fill="x", padx=12, pady=(2, 10))
            ctk.CTkButton(btn_row, text="📥 Load", width=80, height=28,
                          fg_color=self.theme["accent"],
                          hover_color=self.theme["accent_hover"],
                          font=ctk.CTkFont(size=11, weight="bold"),
                          corner_radius=6,
                          command=lambda c=config: self._load_profile(c)).pack(side="left", padx=2)
            ctk.CTkButton(btn_row, text="🗑 Delete", width=80, height=28,
                          fg_color=self.theme["danger"],
                          hover_color="#922b21",
                          font=ctk.CTkFont(size=11, weight="bold"),
                          corner_radius=6,
                          command=lambda n=name: self._delete_and_refresh_profile(n)).pack(side="right")

    def _save_profile_dialog(self):
        def on_save(name):
            config = self._get_current_config()
            save_profile(name, config)
            self._refresh_profiles()
            Toast(self, f"✅ Profile '{name}' saved!", self.theme["success"])
        ProfileSaveDialog(self, on_save=on_save)

    def _load_profile(self, config):
        self.speed_var.set(config.get("speed", DEFAULT_SPEED))
        self.speed_entry.delete(0, "end")
        self.speed_entry.insert(0, f"{self.speed_var.get():.3f}")
        self.humanize_var.set(config.get("humanize", True))

        self.error_sim_var.set(config.get("error_simulation", False))
        self.clipboard_var.set(config.get("clipboard_mode", False))
        self.selected_browser.set(config.get("browser", "none"))
        self.selected_pattern.set(config.get("pattern", "Programmer"))
        self._on_pattern_change(self.selected_pattern.get())
        Toast(self, "📥 Profile loaded!", self.theme["accent"])

    def _delete_and_refresh_profile(self, name):
        delete_profile(name)
        self._refresh_profiles()
        Toast(self, f"🗑 Deleted '{name}'", self.theme["danger"])

    # ─── SNIPPETS TAB ──────────────────────────────────
    def _build_snippets_tab(self):
        frame = ctk.CTkScrollableFrame(self.tab_container, fg_color="transparent",
                                        scrollbar_button_color=self.theme["border"])
        self.tab_frames["snippets"] = frame

        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x", pady=(10, 10))
        SectionLabel(header, text="📋 Snippet Library", text_color=self.theme["text"]).pack(side="left")

        btn_row = ctk.CTkFrame(header, fg_color="transparent")
        btn_row.pack(side="right")
        ctk.CTkButton(btn_row, text="+ New", width=70, height=30,
                      fg_color=self.theme["accent"],
                      hover_color=self.theme["accent_hover"],
                      font=ctk.CTkFont(size=12, weight="bold"),
                      corner_radius=8,
                      command=self._new_snippet).pack(side="left", padx=3)
        ctk.CTkButton(btn_row, text="📥 From Editor", width=100, height=30,
                      fg_color=self.theme["card"],
                      border_width=1, border_color=self.theme["border"],
                      hover_color=self.theme["highlight"],
                      text_color=self.theme["text"],
                      font=ctk.CTkFont(size=11),
                      corner_radius=8,
                      command=self._save_editor_as_snippet).pack(side="left", padx=3)

        self.snippets_list_frame = ctk.CTkFrame(frame, fg_color="transparent")
        self.snippets_list_frame.pack(fill="both", expand=True)

    def _refresh_snippets(self):
        for w in self.snippets_list_frame.winfo_children():
            w.destroy()

        snippets = load_snippets()
        if not snippets:
            ctk.CTkLabel(self.snippets_list_frame, text="No snippets yet.\nClick '+ New' to add one.",
                         text_color=self.theme["text_dim"], font=ctk.CTkFont(size=12),
                         justify="center").pack(pady=30)
            return

        for i, snip in enumerate(snippets):
            card = ctk.CTkFrame(self.snippets_list_frame, fg_color=self.theme["card"],
                                corner_radius=10, border_width=1, border_color=self.theme["border"])
            card.pack(fill="x", pady=4)

            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(fill="x", padx=12, pady=(10, 4))

            name = snip.get("name", "Untitled")
            lang = snip.get("language", "?")
            code = snip.get("code", "")
            preview = code[:80].replace("\n", "↵ ") + ("..." if len(code) > 80 else "")

            ctk.CTkLabel(info, text=f"{name}", font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=self.theme["text"]).pack(side="left")
            ctk.CTkLabel(info, text=f"[{lang}]", font=ctk.CTkFont(size=11),
                         text_color=self.theme["accent"]).pack(side="left", padx=5)

            ctk.CTkLabel(card, text=preview, font=ctk.CTkFont(size=10, family="Consolas"),
                         text_color=self.theme["text_dim"], anchor="w").pack(fill="x", padx=12, pady=(0, 4))

            btn_row = ctk.CTkFrame(card, fg_color="transparent")
            btn_row.pack(fill="x", padx=12, pady=(0, 10))
            ctk.CTkButton(btn_row, text="📥 Insert", width=75, height=26,
                          fg_color=self.theme["accent"],
                          hover_color=self.theme["accent_hover"],
                          font=ctk.CTkFont(size=11), corner_radius=6,
                          command=lambda c=code: self._insert_snippet(c)).pack(side="left", padx=2)
            ctk.CTkButton(btn_row, text="📋 Replace", width=75, height=26,
                          fg_color=self.theme["card"],
                          border_width=1, border_color=self.theme["border"],
                          hover_color=self.theme["highlight"],
                          text_color=self.theme["text"],
                          font=ctk.CTkFont(size=11), corner_radius=6,
                          command=lambda c=code: self._replace_with_snippet(c)).pack(side="left", padx=2)
            ctk.CTkButton(btn_row, text="🗑", width=35, height=26,
                          fg_color=self.theme["danger"], hover_color="#922b21",
                          font=ctk.CTkFont(size=11), corner_radius=6,
                          command=lambda idx=i: self._delete_and_refresh_snippet(idx)).pack(side="right")

    def _new_snippet(self):
        def on_save(name, code, lang):
            add_snippet(name, code, lang)
            self._refresh_snippets()
            Toast(self, f"✅ Snippet '{name}' saved!", self.theme["success"])
        SnippetEditorDialog(self, on_save=on_save)

    def _save_editor_as_snippet(self):
        code = self.code_text.get("1.0", "end").strip()
        if not code:
            Toast(self, "⚠ Editor is empty!", self.theme["warning"])
            return
        def on_save(name, code, lang):
            add_snippet(name, code, lang)
            self._refresh_snippets()
            Toast(self, f"✅ Snippet '{name}' saved!", self.theme["success"])
        SnippetEditorDialog(self, on_save=on_save, code=code)

    def _insert_snippet(self, code):
        self.code_text.insert("end", code)
        self._update_char_count()
        Toast(self, "📥 Snippet inserted!", self.theme["accent"])

    def _replace_with_snippet(self, code):
        self.code_text.delete("1.0", "end")
        self.code_text.insert("1.0", code)
        self._update_char_count()
        Toast(self, "📋 Editor replaced with snippet", self.theme["accent"])

    def _delete_and_refresh_snippet(self, idx):
        delete_snippet(idx)
        self._refresh_snippets()
        Toast(self, "🗑 Snippet deleted", self.theme["danger"])

    # ─── HISTORY TAB ───────────────────────────────────
    def _build_history_tab(self):
        frame = ctk.CTkScrollableFrame(self.tab_container, fg_color="transparent",
                                        scrollbar_button_color=self.theme["border"])
        self.tab_frames["history"] = frame

        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x", pady=(10, 10))
        SectionLabel(header, text="📜 Session History", text_color=self.theme["text"]).pack(side="left")
        ctk.CTkButton(header, text="🗑 Clear All", width=90, height=28,
                      fg_color=self.theme["danger"], hover_color="#922b21",
                      font=ctk.CTkFont(size=11, weight="bold"),
                      corner_radius=6,
                      command=self._clear_history).pack(side="right")

        # Aggregate stats
        self.history_stats_frame = ctk.CTkFrame(frame, fg_color=self.theme["card"],
                                                 corner_radius=10, border_width=1,
                                                 border_color=self.theme["border"])
        self.history_stats_frame.pack(fill="x", pady=(0, 10))

        self.history_list_frame = ctk.CTkFrame(frame, fg_color="transparent")
        self.history_list_frame.pack(fill="both", expand=True)

    def _refresh_history(self):
        for w in self.history_stats_frame.winfo_children():
            w.destroy()
        for w in self.history_list_frame.winfo_children():
            w.destroy()

        agg = get_aggregate_stats()

        # Aggregate stats grid
        agg_grid = ctk.CTkFrame(self.history_stats_frame, fg_color="transparent")
        agg_grid.pack(fill="x", padx=12, pady=10)
        agg_grid.grid_columnconfigure((0, 1, 2, 3), weight=1)

        agg_items = [
            ("📊 Sessions", str(agg["total_sessions"])),
            ("✅ Completed", str(agg.get("completed_sessions", 0))),
            ("📝 Total Chars", f"{agg['total_chars']:,}"),
            ("⚡ Avg WPM", f"{agg['avg_wpm']:.0f}"),
        ]
        for i, (label, value) in enumerate(agg_items):
            f = ctk.CTkFrame(agg_grid, fg_color="transparent")
            f.grid(row=0, column=i, padx=4)
            ctk.CTkLabel(f, text=label, font=ctk.CTkFont(size=10),
                         text_color=self.theme["text_dim"]).pack()
            ctk.CTkLabel(f, text=value, font=ctk.CTkFont(size=15, weight="bold"),
                         text_color=self.theme["accent"]).pack()

        # Session list
        history = load_history()
        if not history:
            ctk.CTkLabel(self.history_list_frame, text="No sessions recorded yet.\nComplete a typing session to see it here.",
                         text_color=self.theme["text_dim"], font=ctk.CTkFont(size=12),
                         justify="center").pack(pady=30)
            return

        for entry in history[:30]:
            card = ctk.CTkFrame(self.history_list_frame, fg_color=self.theme["card"],
                                corner_radius=8, border_width=1, border_color=self.theme["border"])
            card.pack(fill="x", pady=3)

            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=8)
            row.grid_columnconfigure(1, weight=1)

            status = "✅" if entry.get("completed") else "⏹"
            ts = entry.get("timestamp", "")[:16].replace("T", "  ")

            ctk.CTkLabel(row, text=f"{status} {ts}",
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=self.theme["text"]).grid(row=0, column=0, sticky="w")

            detail = (f"{entry.get('chars_typed', 0):,} chars  •  "
                      f"{format_time(entry.get('elapsed_seconds', 0))}  •  "
                      f"{entry.get('avg_wpm', 0):.0f} WPM  •  "
                      f"{entry.get('pattern', '?')}")
            ctk.CTkLabel(row, text=detail, font=ctk.CTkFont(size=10),
                         text_color=self.theme["text_dim"]).grid(row=1, column=0, sticky="w")

    def _clear_history(self):
        clear_history()
        self._refresh_history()
        Toast(self, "🗑 History cleared", self.theme["warning"])

    # ─── SETTINGS TAB ──────────────────────────────────
    def _build_settings_tab(self):
        frame = ctk.CTkScrollableFrame(self.tab_container, fg_color="transparent",
                                        scrollbar_button_color=self.theme["border"])
        self.tab_frames["settings"] = frame

        SectionLabel(frame, text="🎨 Themes", text_color=self.theme["text"]).pack(anchor="w", pady=(10, 8))

        for theme_name in THEMES.keys():
            t = THEMES[theme_name]
            is_active = theme_name == self.current_theme_name

            card = ctk.CTkFrame(frame, fg_color=t["sidebar"] if is_active else self.theme["card"],
                                corner_radius=10,
                                border_width=2 if is_active else 1,
                                border_color=t["accent"] if is_active else self.theme["border"])
            card.pack(fill="x", pady=3)

            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=8)

            # Color preview dots
            dot_frame = ctk.CTkFrame(row, fg_color="transparent")
            dot_frame.pack(side="left")
            for color in [t["accent"], t["success"], t["warning"], t["danger"]]:
                ctk.CTkLabel(dot_frame, text="●", font=ctk.CTkFont(size=14),
                             text_color=color).pack(side="left", padx=1)

            ctk.CTkLabel(row, text=f"  {theme_name}",
                         font=ctk.CTkFont(size=13, weight="bold" if is_active else "normal"),
                         text_color=t["text"]).pack(side="left", padx=5)

            if is_active:
                ctk.CTkLabel(row, text="✓ Active", font=ctk.CTkFont(size=11, weight="bold"),
                             text_color=t["accent"]).pack(side="right")
            else:
                ctk.CTkButton(row, text="Apply", width=65, height=26,
                              fg_color=t["accent"], hover_color=t["accent_hover"],
                              font=ctk.CTkFont(size=11, weight="bold"),
                              corner_radius=6,
                              command=lambda tn=theme_name: self._apply_theme(tn)).pack(side="right")

        # Editor Options
        SectionLabel(frame, text="📝 Editor Options", text_color=self.theme["text"]).pack(anchor="w", pady=(15, 8))
        ctk.CTkCheckBox(frame, text="Word Wrap", variable=self.word_wrap_var,
                        font=ctk.CTkFont(size=12),
                        fg_color=self.theme["accent"],
                        hover_color=self.theme["accent_hover"],
                        text_color=self.theme["text"],
                        command=self._toggle_word_wrap).pack(anchor="w", pady=3, padx=5)

        # Keyboard shortcuts
        SectionLabel(frame, text="⌨ Keyboard Shortcuts", text_color=self.theme["text"]).pack(anchor="w", pady=(15, 8))

        shortcuts = [
            ("ESC", "Pause typing"),
            ("INSERT", "Resume / Start typing"),
            ("Ctrl+O", "Load file (from editor)"),
        ]
        for key, desc in shortcuts:
            row = ctk.CTkFrame(frame, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=key, font=ctk.CTkFont(size=11, family="Consolas", weight="bold"),
                         text_color=self.theme["accent"], width=80, anchor="e").pack(side="left")
            ctk.CTkLabel(row, text=f"  {desc}", font=ctk.CTkFont(size=11),
                         text_color=self.theme["text_dim"]).pack(side="left")

        # Data files info
        SectionLabel(frame, text="📁 Data Storage", text_color=self.theme["text"]).pack(anchor="w", pady=(15, 5))
        ctk.CTkLabel(frame, text="All data is stored in:\n~/.auto_typer/\n\n"
                     "• profiles.json\n• snippets.json\n• history.json\n• settings.json",
                     font=ctk.CTkFont(size=11), text_color=self.theme["text_dim"],
                     justify="left").pack(anchor="w", padx=5)

        # About
        SectionLabel(frame, text="ℹ About", text_color=self.theme["text"]).pack(anchor="w", pady=(15, 5))
        ctk.CTkLabel(frame, text="Auto Typer Pro v2.1\nSenior Dev Edition\n\n"
                     "Typing Patterns • Error Simulation\n"
                     "Profiles • Snippets • History\n"
                     "Analytics • Scheduler • Themes",
                     font=ctk.CTkFont(size=11), text_color=self.theme["text_dim"],
                     justify="left").pack(anchor="w", padx=5, pady=(0, 20))

    # ======================================================================
    # MAIN EDITOR AREA
    # ======================================================================
    def _build_main_area(self):
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(2, weight=1)

        # ─── URL BAR ──────────────────────────────────────
        url_frame = ctk.CTkFrame(main, corner_radius=10, fg_color=self.theme["card"],
                                  border_width=1, border_color=self.theme["border"])
        url_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        url_frame.grid_columnconfigure(0, weight=1)

        self.url_entry = ctk.CTkEntry(url_frame,
                                       placeholder_text="🌐  Enter target URL (optional — for browser auto-open)...",
                                       height=42, font=ctk.CTkFont(size=13),
                                       fg_color=self.theme["editor"],
                                       border_color=self.theme["border"],
                                       text_color=self.theme["text"])
        self.url_entry.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        # ─── ANALYTICS BAR ────────────────────────────────
        self.analytics_frame = ctk.CTkFrame(main, corner_radius=10, fg_color=self.theme["card"],
                                             border_width=1, border_color=self.theme["border"])
        self.analytics_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        self.analytics_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        self.stat_cards = {}
        stats_def = [
            ("chars", "📝 Characters", "0 / 0"),
            ("speed", "⚡ Speed", "0.0 ch/s"),
            ("wpm", "🔤 WPM", "0"),
            ("elapsed", "⏱ Elapsed", "0:00"),
            ("eta", "⏳ ETA", "--:--"),
        ]
        for i, (key, label, default) in enumerate(stats_def):
            card = StatCard(self.analytics_frame, label=label, value=default,
                            accent=self.theme["accent"], fg_color=self.theme["card"])
            card.grid(row=0, column=i, padx=5, pady=8, sticky="ew")
            self.stat_cards[key] = card

        # ─── EDITOR AREA ──────────────────────────────────
        editor_frame = ctk.CTkFrame(main, corner_radius=10, fg_color=self.theme["card"],
                                     border_width=1, border_color=self.theme["border"])
        editor_frame.grid(row=2, column=0, sticky="nsew")
        editor_frame.grid_columnconfigure(0, weight=1)
        editor_frame.grid_rowconfigure(1, weight=1)

        # Editor header
        hdr = ctk.CTkFrame(editor_frame, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", padx=15, pady=(10, 5))
        hdr.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(hdr, text="📝  Source Code / Text",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color=self.theme["text"]).grid(row=0, column=0, sticky="w")

        self.char_count_lbl = ctk.CTkLabel(hdr, text="0 chars  •  0 lines  •  0 words",
                                             font=ctk.CTkFont(size=11),
                                             text_color=self.theme["text_dim"])
        self.char_count_lbl.grid(row=0, column=1, sticky="e", padx=10)

        btn_frame = ctk.CTkFrame(hdr, fg_color="transparent")
        btn_frame.grid(row=0, column=2, sticky="e")

        ctk.CTkButton(btn_frame, text="📂 Load File", width=100, height=30,
                      fg_color=self.theme["accent"],
                      hover_color=self.theme["accent_hover"],
                      font=ctk.CTkFont(size=12, weight="bold"),
                      corner_radius=8,
                      command=self._load_file).pack(side="left", padx=3)
        ctk.CTkButton(btn_frame, text="🗑 Clear", width=70, height=30,
                      fg_color=self.theme["card"],
                      border_width=1, border_color=self.theme["border"],
                      hover_color=self.theme["highlight"],
                      text_color=self.theme["text"],
                      font=ctk.CTkFont(size=11),
                      corner_radius=8,
                      command=self._clear_editor).pack(side="left", padx=3)

        # Code textbox
        wrap_mode = "word" if self.word_wrap_var.get() else "none"
        self.code_text = ctk.CTkTextbox(editor_frame,
                                         font=ctk.CTkFont(family="Consolas", size=14),
                                         wrap=wrap_mode,
                                         fg_color=self.theme["editor"],
                                         text_color=self.theme["text"],
                                         scrollbar_button_color=self.theme["border"])
        self.code_text.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.code_text.bind("<KeyRelease>", lambda e: self._update_char_count())

        # ─── STATUS FOOTER ─────────────────────────────────
        footer = ctk.CTkFrame(main, corner_radius=10, fg_color=self.theme["card"],
                               border_width=1, border_color=self.theme["border"], height=55)
        footer.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        footer.grid_columnconfigure(1, weight=1)

        self.status_lbl = ctk.CTkLabel(footer, text="⬤  READY",
                                        font=ctk.CTkFont(size=15, weight="bold"),
                                        text_color=self.theme["text_dim"])
        self.status_lbl.grid(row=0, column=0, padx=15, pady=12, sticky="w")

        self.progress_bar = ctk.CTkProgressBar(footer, progress_color=self.theme["accent"],
                                                fg_color=self.theme["bg"])
        self.progress_bar.grid(row=0, column=1, padx=15, pady=12, sticky="ew")
        self.progress_bar.set(0)

        self.progress_lbl = ctk.CTkLabel(footer, text="0 / 0  |  0%",
                                          font=ctk.CTkFont(size=12, weight="bold"),
                                          text_color=self.theme["text"])
        self.progress_lbl.grid(row=0, column=2, padx=(0, 15), pady=12, sticky="e")

    # ======================================================================
    # ENGINE CALLBACKS
    # ======================================================================
    def _on_engine_progress(self, typed, total, elapsed, eta_secs):
        def ui_update():
            pct = typed / total if total > 0 else 0
            self.progress_bar.set(pct)
            self.progress_lbl.configure(text=f"{typed:,} / {total:,}  |  {pct*100:.0f}%")

            stats = self.engine.get_live_stats()
            self.stat_cards["chars"].set_value(f"{typed:,}")
            self.stat_cards["speed"].set_value(f"{stats['cps']:.1f}")
            self.stat_cards["wpm"].set_value(f"{stats['wpm']:.0f}")
            self.stat_cards["elapsed"].set_value(format_time(elapsed))
            self.stat_cards["eta"].set_value(format_eta(eta_secs))

            self.overlay.update_progress(typed, total, elapsed, eta_secs,
                                          stats['cps'], stats['wpm'], stats['errors'])
        self.after(0, ui_update)

    def _on_engine_status(self, text, color):
        def ui_update():
            self.status_lbl.configure(text=text, text_color=color)
            self.overlay.set_status(text, color)

            if "PAUSED" in text or "WAITING" in text:
                self.pause_btn.configure(state="disabled")
                self.resume_btn.configure(state="normal")
            elif "TYPING" in text or "Starting" in text or "Resuming" in text:
                self.pause_btn.configure(state="normal")
                self.resume_btn.configure(state="disabled")
        self.after(0, ui_update)

    def _on_engine_finish(self, status, stats):
        def ui_update():
            color = self.theme["success"] if "DONE" in status else self.theme["danger"]
            self.status_lbl.configure(text=status, text_color=color)

            self.start_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")
            self.pause_btn.configure(state="disabled")
            self.resume_btn.configure(state="disabled")
            self.overlay.destroy()

            # Log to history (persistent)
            add_session(stats, self._last_config)

            # Show summary
            summary = calculate_session_summary(stats)
            SessionSummaryDialog(self, summary, self.theme)

            Toast(self, status, color)
        self.after(0, ui_update)

    def _on_char_typed(self, char):
        """Called from engine thread for each character typed."""
        self.after(0, lambda: self.overlay.update_char_preview(char))

    # ======================================================================
    # CONTROLS
    # ======================================================================
    def _start_typing(self):
        code = self.code_text.get("1.0", "end").strip()
        if not code:
            Toast(self, "⚠ Source code is empty!", self.theme["warning"])
            return

        config = self._get_current_config()
        config["url"] = self.url_entry.get().strip()
        self._last_config = config

        # Cancel any active scheduler
        if self.scheduler.active:
            self.scheduler.cancel()
            self._scheduler_active = False
            self.schedule_status_lbl.configure(text="")

        # UI state
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.pause_btn.configure(state="normal")
        self.resume_btn.configure(state="normal")
        self.progress_bar.set(0)

        for card in self.stat_cards.values():
            card.set_value("—")

        # Show overlay
        self.overlay = ActiveOverlay(self, self.theme)
        self.overlay.show()
        self.overlay.bind_controls(self._pause_typing, self._resume_typing, self._stop_typing)

        # Start engine
        self.engine.start(code, config)

    def _pause_typing(self):
        self.engine.pause()

    def _resume_typing(self):
        self.engine.resume()

    def _stop_typing(self):
        self.engine.stop()

    def _get_current_config(self) -> dict:
        try:
            speed = max(MIN_SPEED, min(MAX_SPEED, float(self.speed_entry.get())))
        except ValueError:
            speed = DEFAULT_SPEED
        return {
            "speed": speed,
            "humanize": self.humanize_var.get(),
            "pattern": self.selected_pattern.get(),
            "error_simulation": self.error_sim_var.get(),
            "clipboard_mode": self.clipboard_var.get(),
            "browser": self.selected_browser.get(),
        }

    # ======================================================================
    # SCHEDULER (FIXED)
    # ======================================================================
    def _open_scheduler(self):
        def on_schedule(mode, value):
            # Cancel any existing schedule
            if self.scheduler.active:
                self.scheduler.cancel()

            self._scheduler_active = True

            def on_countdown(remaining):
                """Called from scheduler thread — use self.after for thread safety."""
                mins, secs = divmod(remaining, 60)
                text = f"⏰ Starting in {mins}:{secs:02d}..."
                self.after(0, lambda: self.status_lbl.configure(
                    text=text, text_color=self.theme["warning"]))
                self.after(0, lambda: self.schedule_status_lbl.configure(text=text))

            def on_ready():
                """Called from scheduler thread when countdown reaches 0."""
                self._scheduler_active = False
                self.after(0, lambda: self.schedule_status_lbl.configure(text=""))
                self.after(0, self._start_typing)

            self.scheduler.on_countdown = on_countdown
            self.scheduler.on_ready = on_ready

            if mode == "delay":
                self.scheduler.schedule_delay(value)
                Toast(self, f"⏰ Scheduled: starting in {value}s", self.theme["accent"])
                self.schedule_status_lbl.configure(text=f"⏰ Starting in {value}s...")
            elif mode == "time":
                h, m = value
                self.scheduler.schedule_time(h, m)
                Toast(self, f"⏰ Scheduled: {h:02d}:{m:02d}", self.theme["accent"])
                self.schedule_status_lbl.configure(text=f"⏰ Scheduled for {h:02d}:{m:02d}")

        SchedulerDialog(self, on_schedule=on_schedule)

    # ======================================================================
    # UTILITIES
    # ======================================================================
    def _on_slider_change(self, val):
        self.speed_entry.delete(0, "end")
        self.speed_entry.insert(0, f"{float(val):.3f}")

    def _on_entry_change(self, *_):
        try:
            v = max(MIN_SPEED, min(MAX_SPEED, float(self.speed_entry.get())))
            self.speed_var.set(v)
        except ValueError:
            pass

    def _on_pattern_change(self, name):
        pattern = TYPING_PATTERNS.get(name, {})
        self.pattern_desc.configure(text=pattern.get("description", ""))

    def _load_file(self):
        path = ctk.filedialog.askopenfilename(filetypes=[
            ("All files", "*.*"),
            ("Python", "*.py"),
            ("Java", "*.java"),
            ("C/C++", "*.c *.cpp *.h"),
            ("JavaScript", "*.js *.ts"),
            ("HTML/CSS", "*.html *.css"),
            ("Text", "*.txt"),
        ])
        if path:
            try:
                with open(path, "r") as f:
                    content = f.read()
                self.code_text.delete("1.0", "end")
                self.code_text.insert("1.0", content)
                self._update_char_count()
                Toast(self, f"📂 Loaded: {os.path.basename(path)}", self.theme["success"])
            except Exception as e:
                Toast(self, f"⚠ Error: {e}", self.theme["danger"])

    def _clear_editor(self):
        self.code_text.delete("1.0", "end")
        self._update_char_count()

    def _toggle_word_wrap(self):
        wrap_mode = "word" if self.word_wrap_var.get() else "none"
        self.code_text.configure(wrap=wrap_mode)

    def _update_char_count(self):
        text = self.code_text.get("1.0", "end").rstrip()
        chars = len(text)
        lines = text.count("\n") + 1 if text else 0
        words = len(text.split()) if text else 0
        self.char_count_lbl.configure(text=f"{chars:,} chars  •  {lines} lines  •  {words:,} words")

    # ======================================================================
    # HOTKEYS
    # ======================================================================
    def _setup_hotkeys(self):
        def on_press(key):
            try:
                if key == pynput_keyboard.Key.escape:
                    self._pause_typing()
                elif key == pynput_keyboard.Key.insert:
                    self._resume_typing()
            except AttributeError:
                pass

        listener = pynput_keyboard.Listener(on_press=on_press)
        listener.daemon = True
        listener.start()

        self.bind("<Insert>", lambda e: self._resume_typing())
        self.bind("<Escape>", lambda e: self._pause_typing())

    # ======================================================================
    # LIFECYCLE
    # ======================================================================
    def _on_close(self):
        """Save settings and clean up."""
        geo = self.geometry()
        # Extract just WxH, not position
        if "+" in geo:
            geo = geo.split("+")[0]

        self.settings.update({
            "theme": self.current_theme_name,
            "speed": self.speed_var.get(),
            "humanize": self.humanize_var.get(),
            "browser": self.selected_browser.get(),
            "pattern": self.selected_pattern.get(),
            "error_simulation": self.error_sim_var.get(),
            "clipboard_mode": self.clipboard_var.get(),
            "window_geometry": geo,
        })
        save_settings(self.settings)

        if self.engine.typing_active:
            self.engine.stop()
        if self.scheduler.active:
            self.scheduler.cancel()
        self.overlay.destroy()
        self.destroy()
