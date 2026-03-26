"""
Auto Typer Pro — Enhanced Floating Overlay v2.1
Fixed: increased height so buttons are always visible, better layout.
"""
import customtkinter as ctk
import tkinter as tk
from features.analytics import format_eta, format_time


class ActiveOverlay:
    """
    Premium floating overlay with speed graph, char preview, controls.
    Fixed: buttons no longer get cut off.
    """

    def __init__(self, parent, theme: dict):
        self.parent = parent
        self.theme = theme
        self.overlay = None
        self._components = {}
        self._minimized = False
        self._speed_points = []
        self._max_graph_points = 60

    def show(self):
        if self.overlay and self.overlay.winfo_exists():
            self.overlay.destroy()

        self._speed_points = []
        self._minimized = False

        self.overlay = ctk.CTkToplevel(self.parent)
        self.overlay.overrideredirect(True)
        self.overlay.attributes("-topmost", True)
        self.overlay.attributes("-alpha", 0.96)

        self._full_width, self._full_height = 500, 380  # Increased height from 320
        self._mini_width, self._mini_height = 500, 50
        x = (self.overlay.winfo_screenwidth() // 2) - (self._full_width // 2)
        y = 30
        self.overlay.geometry(f"{self._full_width}x{self._full_height}+{x}+{y}")
        self.overlay.configure(fg_color=self.theme["sidebar"])

        self._outer = ctk.CTkFrame(self.overlay, fg_color=self.theme["sidebar"],
                                    border_width=2, border_color=self.theme["accent"])
        self._outer.pack(expand=True, fill="both", padx=1, pady=1)

        self._build_full_ui()

    def _build_full_ui(self):
        for w in self._outer.winfo_children():
            w.destroy()

        # ─── DRAG BAR ─────────────────────────────────────
        drag = ctk.CTkFrame(self._outer, height=30, corner_radius=0, fg_color=self.theme["bg"])
        drag.pack(fill="x", side="top")

        title = ctk.CTkLabel(drag, text="⌨  Auto Typer Pro — Live Session",
                             font=ctk.CTkFont(size=11, weight="bold"),
                             text_color=self.theme["text_dim"])
        title.pack(side="left", padx=10, pady=3)

        ctk.CTkButton(drag, text="─", width=28, height=22, corner_radius=6,
                      fg_color=self.theme["highlight"], hover_color=self.theme["border"],
                      font=ctk.CTkFont(size=12, weight="bold"),
                      text_color=self.theme["text_dim"],
                      command=self._toggle_minimize).pack(side="right", padx=5, pady=3)

        for w in (drag, title):
            w.bind("<Button-1>", self._start_move)
            w.bind("<B1-Motion>", self._do_move)

        # ─── CONTENT FRAME (scrollable area) ──────────────
        content = ctk.CTkFrame(self._outer, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=12, pady=(6, 10))

        # ─── STATUS ROW ───────────────────────────────────
        status_frame = ctk.CTkFrame(content, fg_color="transparent")
        status_frame.pack(fill="x", pady=(0, 4))

        self._components["status"] = ctk.CTkLabel(
            status_frame, text="⏸ WAITING... (Press Insert)",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="#d35400")
        self._components["status"].pack(side="left")

        self._components["eta"] = ctk.CTkLabel(
            status_frame, text="ETA: --:--  |  0%",
            font=ctk.CTkFont(size=12, weight="bold"), text_color=self.theme["accent"])
        self._components["eta"].pack(side="right")

        # ─── STATS ROW ────────────────────────────────────
        stats = ctk.CTkFrame(content, fg_color=self.theme["bg"], corner_radius=8)
        stats.pack(fill="x", pady=(2, 4))
        stats.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        stat_defs = [
            ("chars", "📝", "0/0"),
            ("cps", "⚡", "0.0/s"),
            ("wpm", "🔤", "0 WPM"),
            ("errors", "🔴", "0 errs"),
            ("elapsed", "⏱", "0:00"),
        ]
        for i, (key, icon, default) in enumerate(stat_defs):
            f = ctk.CTkFrame(stats, fg_color="transparent")
            f.grid(row=0, column=i, padx=3, pady=5)
            ctk.CTkLabel(f, text=icon, font=ctk.CTkFont(size=11)).pack()
            lbl = ctk.CTkLabel(f, text=default, font=ctk.CTkFont(size=11, weight="bold"),
                               text_color=self.theme["text"])
            lbl.pack()
            self._components[key] = lbl

        # ─── PROGRESS BAR ─────────────────────────────────
        self._components["progress"] = ctk.CTkProgressBar(
            content, height=10, progress_color=self.theme["accent"],
            fg_color=self.theme["bg"], corner_radius=5)
        self._components["progress"].pack(fill="x", pady=(4, 4))
        self._components["progress"].set(0)

        # ─── SPEED GRAPH ──────────────────────────────────
        graph_frame = ctk.CTkFrame(content, fg_color=self.theme["bg"], corner_radius=8)
        graph_frame.pack(fill="x", pady=(2, 4))

        ctk.CTkLabel(graph_frame, text="Speed Graph", font=ctk.CTkFont(size=10),
                     text_color=self.theme["text_dim"]).pack(anchor="w", padx=8, pady=(3, 0))

        self._graph_canvas = tk.Canvas(graph_frame, height=50, bg=self.theme["bg"],
                                        highlightthickness=0)
        self._graph_canvas.pack(fill="x", padx=8, pady=(0, 5))

        # ─── CHAR PREVIEW + SHORTCUTS ─────────────────────
        info_row = ctk.CTkFrame(content, fg_color="transparent")
        info_row.pack(fill="x", pady=(0, 4))

        ctk.CTkLabel(info_row, text="Current:", font=ctk.CTkFont(size=10),
                     text_color=self.theme["text_dim"]).pack(side="left")
        self._components["char_preview"] = ctk.CTkLabel(
            info_row, text="—",
            font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
            text_color=self.theme["accent"])
        self._components["char_preview"].pack(side="left", padx=5)

        ctk.CTkLabel(info_row, text="ESC: Pause  |  INS: Resume",
                     font=ctk.CTkFont(size=9), text_color=self.theme["text_dim"]).pack(side="right")

        # ─── CONTROL BUTTONS (ALWAYS VISIBLE) ─────────────
        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(fill="x", side="bottom", pady=(6, 0))
        btn_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self._components["pause_btn"] = ctk.CTkButton(
            btn_frame, text="⏸ Pause", fg_color=self.theme["warning"],
            text_color="black", hover_color="#d68910", height=36,
            font=ctk.CTkFont(size=13, weight="bold"), corner_radius=8)
        self._components["pause_btn"].grid(row=0, column=0, padx=3, sticky="ew")

        self._components["resume_btn"] = ctk.CTkButton(
            btn_frame, text="⏯ Resume", fg_color="#d35400",
            hover_color="#ba4a00", state="disabled", height=36,
            font=ctk.CTkFont(size=13, weight="bold"), corner_radius=8)
        self._components["resume_btn"].grid(row=0, column=1, padx=3, sticky="ew")

        self._components["stop_btn"] = ctk.CTkButton(
            btn_frame, text="⏹ Stop", fg_color=self.theme["danger"],
            hover_color="#922b21", height=36,
            font=ctk.CTkFont(size=13, weight="bold"), corner_radius=8)
        self._components["stop_btn"].grid(row=0, column=2, padx=3, sticky="ew")

    def _build_mini_ui(self):
        for w in self._outer.winfo_children():
            w.destroy()

        row = ctk.CTkFrame(self._outer, fg_color="transparent")
        row.pack(fill="both", expand=True, padx=10)
        row.grid_columnconfigure(1, weight=1)

        self._components["status"] = ctk.CTkLabel(
            row, text="⌨ TYPING...", font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.theme["accent"])
        self._components["status"].grid(row=0, column=0, padx=(0, 10))

        self._components["progress"] = ctk.CTkProgressBar(
            row, height=8, progress_color=self.theme["accent"],
            fg_color=self.theme["bg"], corner_radius=4)
        self._components["progress"].grid(row=0, column=1, sticky="ew", padx=5)
        self._components["progress"].set(0)

        self._components["eta"] = ctk.CTkLabel(
            row, text="0%", font=ctk.CTkFont(size=11, weight="bold"),
            text_color=self.theme["text_dim"])
        self._components["eta"].grid(row=0, column=2, padx=5)

        ctk.CTkButton(row, text="◻", width=28, height=22, corner_radius=6,
                      fg_color=self.theme["highlight"], hover_color=self.theme["border"],
                      font=ctk.CTkFont(size=12), text_color=self.theme["text_dim"],
                      command=self._toggle_minimize).grid(row=0, column=3, padx=(5, 0))

        for w in (row, self._components["status"]):
            w.bind("<Button-1>", self._start_move)
            w.bind("<B1-Motion>", self._do_move)

    def _toggle_minimize(self):
        if self._minimized:
            x, y = self.overlay.winfo_x(), self.overlay.winfo_y()
            self.overlay.geometry(f"{self._full_width}x{self._full_height}+{x}+{y}")
            self._build_full_ui()
            if hasattr(self, '_bound_controls'):
                self.bind_controls(*self._bound_controls)
            self._minimized = False
        else:
            x, y = self.overlay.winfo_x(), self.overlay.winfo_y()
            self.overlay.geometry(f"{self._mini_width}x{self._mini_height}+{x}+{y}")
            self._build_mini_ui()
            self._minimized = True

    def _start_move(self, e):
        self.overlay._drag_x, self.overlay._drag_y = e.x, e.y

    def _do_move(self, e):
        dx = e.x - self.overlay._drag_x
        dy = e.y - self.overlay._drag_y
        nx, ny = self.overlay.winfo_x() + dx, self.overlay.winfo_y() + dy
        self.overlay.geometry(f"+{nx}+{ny}")

    def bind_controls(self, pause_fn, resume_fn, stop_fn):
        self._bound_controls = (pause_fn, resume_fn, stop_fn)
        if "pause_btn" in self._components:
            self._components["pause_btn"].configure(command=pause_fn)
        if "resume_btn" in self._components:
            self._components["resume_btn"].configure(command=resume_fn)
        if "stop_btn" in self._components:
            self._components["stop_btn"].configure(command=stop_fn)

    def update_progress(self, typed: int, total: int, elapsed: float, eta_secs: float,
                        cps: float = 0, wpm: float = 0, errors: int = 0):
        if not self.overlay or not self.overlay.winfo_exists():
            return

        pct = typed / total if total > 0 else 0

        if "progress" in self._components:
            self._components["progress"].set(pct)
        if "eta" in self._components:
            if self._minimized:
                self._components["eta"].configure(text=f"{pct*100:.0f}%")
            else:
                self._components["eta"].configure(text=f"ETA: {format_eta(eta_secs)}  |  {pct*100:.0f}%")

        if not self._minimized:
            if "chars" in self._components:
                self._components["chars"].configure(text=f"{typed:,}/{total:,}")
            if "cps" in self._components:
                self._components["cps"].configure(text=f"{cps:.1f}/s")
            if "wpm" in self._components:
                self._components["wpm"].configure(text=f"{wpm:.0f} WPM")
            if "errors" in self._components:
                self._components["errors"].configure(text=f"{errors} errs")
            if "elapsed" in self._components:
                self._components["elapsed"].configure(text=format_time(elapsed))

            self._speed_points.append(cps)
            if len(self._speed_points) > self._max_graph_points:
                self._speed_points = self._speed_points[-self._max_graph_points:]
            self._draw_speed_graph()

    def update_char_preview(self, char: str):
        if not self.overlay or not self.overlay.winfo_exists():
            return
        if "char_preview" in self._components:
            display = repr(char) if char in ('\n', '\t', ' ') else char
            self._components["char_preview"].configure(text=display)

    def _draw_speed_graph(self):
        if not hasattr(self, '_graph_canvas') or self._minimized:
            return
        try:
            canvas = self._graph_canvas
            canvas.delete("all")
            w = canvas.winfo_width()
            h = canvas.winfo_height()
            if w < 10 or h < 10 or len(self._speed_points) < 2:
                return

            max_speed = max(self._speed_points) or 1
            padding = 4
            n = len(self._speed_points)
            points = []
            for i, speed in enumerate(self._speed_points):
                x = padding + (i / (n - 1)) * (w - 2 * padding)
                y = h - padding - (speed / max_speed) * (h - 2 * padding)
                points.append((x, y))

            for i in range(1, len(points)):
                canvas.create_line(
                    points[i-1][0], points[i-1][1],
                    points[i][0], points[i][1],
                    fill=self.theme["accent"], width=2, smooth=True)

            fill_points = list(points) + [(points[-1][0], h), (points[0][0], h)]
            flat = [coord for p in fill_points for coord in p]
            if len(flat) >= 6:
                canvas.create_polygon(flat, fill=self.theme["accent"], stipple="gray25", outline="")
        except Exception:
            pass

    def set_status(self, text: str, color: str = "white"):
        if not self.overlay or not self.overlay.winfo_exists():
            return
        if "status" in self._components:
            self._components["status"].configure(text=text, text_color=color)

        if not self._minimized:
            if "PAUSED" in text or "WAITING" in text:
                if "pause_btn" in self._components:
                    self._components["pause_btn"].configure(state="disabled")
                if "resume_btn" in self._components:
                    self._components["resume_btn"].configure(state="normal")
            elif "TYPING" in text or "Starting" in text or "Resuming" in text:
                if "pause_btn" in self._components:
                    self._components["pause_btn"].configure(state="normal")
                if "resume_btn" in self._components:
                    self._components["resume_btn"].configure(state="disabled")

    def destroy(self):
        if self.overlay and self.overlay.winfo_exists():
            self.overlay.destroy()
            self.overlay = None

    @property
    def exists(self):
        return self.overlay is not None and self.overlay.winfo_exists()
