import time
import random
import subprocess
from threading import Thread, Event
from pynput import keyboard as pynput_keyboard
from pynput.keyboard import Controller, Key
import customtkinter as ctk

# Professional appearance settings
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class AutoTyperPro(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Auto Typer Pro (Senior Dev Edition)")
        self.geometry("1100x750")
        self.minsize(950, 650)

        # Core Engine State
        self.kb = Controller()
        self.pause_event = Event()
        self.stop_event = Event()
        self.typing_active = False
        
        # User Configuration State
        self.speed_var = ctk.DoubleVar(value=0.03) # Slightly slower default for reliability
        self.humanize_var = ctk.BooleanVar(value=True)
        self.vm_mode_var = ctk.BooleanVar(value=True) # Enables VM safe typing
        self.auto_indent_var = ctk.BooleanVar(value=False) # MUST default to False so it types tabs!
        self.selected_browser = ctk.StringVar(value="none")
        
        # Progress Tracking
        self.typed_chars = 0
        self.total_chars = 0

        # Layout mapping
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_editor_area()
        self._setup_hotkeys()
        
        self.pause_event.set()
        self.mainloop()

    # ==========================================
    # UI CONSTRUCTION 
    # ==========================================

    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color="#181825") # Deep dark
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_rowconfigure(10, weight=1)

        # App Header
        hdr = ctk.CTkLabel(sidebar, text="Auto Typer Pro", font=ctk.CTkFont(size=22, weight="bold"))
        hdr.grid(row=0, column=0, padx=20, pady=(20, 5))
        
        sub = ctk.CTkLabel(sidebar, text="ESC: Pause | INS: Resume", font=ctk.CTkFont(size=12), text_color="gray")
        sub.grid(row=1, column=0, padx=20, pady=(0, 20))

        # --- Section 1: Typing Dynamics ---
        ctk.CTkLabel(sidebar, text="Typing Dynamics", font=ctk.CTkFont(size=14, weight="bold"), anchor="w").grid(row=2, column=0, padx=20, pady=(10,0), sticky="w")
        
        self.speed_slider = ctk.CTkSlider(sidebar, from_=0.001, to=0.5, variable=self.speed_var, command=self._on_slider_change)
        self.speed_slider.grid(row=3, column=0, padx=20, pady=(10, 5), sticky="ew")

        speed_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        speed_frame.grid(row=4, column=0, padx=20, pady=(0, 5), sticky="ew")
        speed_frame.grid_columnconfigure(0, weight=1)
        
        self.speed_entry = ctk.CTkEntry(speed_frame, width=70, justify="center")
        self.speed_entry.insert(0, "0.030")
        self.speed_entry.grid(row=0, column=0, sticky="w")
        self.speed_entry.bind("<Return>", self._on_entry_change)
        self.speed_entry.bind("<FocusOut>", self._on_entry_change)
        ctk.CTkLabel(speed_frame, text="sec/char", text_color="gray").grid(row=0, column=1, sticky="w", padx=5)

        self.humanize_chk = ctk.CTkCheckBox(sidebar, text="Humanize Speed Variance", variable=self.humanize_var)
        self.humanize_chk.grid(row=5, column=0, padx=20, pady=(5, 5), sticky="w")
        
        self.vm_chk = ctk.CTkCheckBox(sidebar, text="VM Compatibility Mode", variable=self.vm_mode_var)
        self.vm_chk.grid(row=6, column=0, padx=20, pady=(5, 15), sticky="w")

        # --- Section 2: Target Settings ---
        ctk.CTkLabel(sidebar, text="Target Environment", font=ctk.CTkFont(size=14, weight="bold"), anchor="w").grid(row=7, column=0, padx=20, pady=(10,0), sticky="w")

        ctk.CTkLabel(sidebar, text="Browser Engine:", text_color="gray", anchor="w").grid(row=8, column=0, padx=20, pady=(5, 5), sticky="w")
        self.browser_menu = ctk.CTkSegmentedButton(sidebar, values=["none", "edge", "chrome", "firefox"], variable=self.selected_browser)
        self.browser_menu.grid(row=9, column=0, padx=20, pady=(0, 20), sticky="ew")

        # --- Section 3: Controls ---
        ctrl_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        ctrl_frame.grid(row=11, column=0, padx=20, pady=(0, 20), sticky="ew")
        ctrl_frame.grid_columnconfigure(0, weight=1)
        ctrl_frame.grid_columnconfigure(1, weight=1)

        self.start_btn = ctk.CTkButton(ctrl_frame, text="▶ Start", fg_color="#2ecc71", hover_color="#27ae60", command=self._start_typing)
        self.start_btn.grid(row=0, column=0, columnspan=2, pady=5, sticky="ew")

        self.pause_btn = ctk.CTkButton(ctrl_frame, text="⏸ Pause", fg_color="#f39c12", text_color="black", hover_color="#d68910", command=self._pause_typing, state="disabled")
        self.pause_btn.grid(row=1, column=0, padx=(0, 2), pady=5, sticky="ew")

        self.resume_btn = ctk.CTkButton(ctrl_frame, text="⏯ Rsm", fg_color="#d35400", hover_color="#ba4a00", command=self._resume_typing, state="disabled")
        self.resume_btn.grid(row=1, column=1, padx=(2, 0), pady=5, sticky="ew")

        self.stop_btn = ctk.CTkButton(ctrl_frame, text="⏹ Stop", fg_color="#c0392b", hover_color="#922b21", command=self._stop_typing, state="disabled")
        self.stop_btn.grid(row=2, column=0, columnspan=2, pady=5, sticky="ew")


    def _build_editor_area(self):
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(1, weight=1)

        # URL
        url_frm = ctk.CTkFrame(main, corner_radius=10)
        url_frm.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        url_frm.grid_columnconfigure(0, weight=1)
        self.url_entry = ctk.CTkEntry(url_frm, placeholder_text="Enter target URL (optional, if using a browser engine)...", height=45, font=ctk.CTkFont(size=14))
        self.url_entry.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        # Text Editor
        txt_frm = ctk.CTkFrame(main, corner_radius=10)
        txt_frm.grid(row=1, column=0, sticky="nsew")
        txt_frm.grid_columnconfigure(0, weight=1)
        txt_frm.grid_rowconfigure(1, weight=1)

        hdr_frm = ctk.CTkFrame(txt_frm, fg_color="transparent")
        hdr_frm.grid(row=0, column=0, sticky="ew", padx=15, pady=(10, 5))
        hdr_frm.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(hdr_frm, text="Source Code/Text", font=ctk.CTkFont(size=15, weight="bold")).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(hdr_frm, text="📂 Load File", width=120, command=self._load_file).grid(row=0, column=1, sticky="e")

        self.code_text = ctk.CTkTextbox(txt_frm, font=ctk.CTkFont(family="Consolas", size=14), wrap="none", fg_color="#11111b")
        self.code_text.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        # Status & Progress Footer
        ftr_frm = ctk.CTkFrame(main, corner_radius=10, height=60)
        ftr_frm.grid(row=2, column=0, sticky="ew", pady=(15, 0))
        ftr_frm.grid_columnconfigure(1, weight=1)

        self.status_lbl = ctk.CTkLabel(ftr_frm, text="READY", font=ctk.CTkFont(size=16, weight="bold"), text_color="gray")
        self.status_lbl.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        self.progress_bar = ctk.CTkProgressBar(ftr_frm)
        self.progress_bar.grid(row=0, column=1, padx=20, pady=15, sticky="ew")
        self.progress_bar.set(0)

        self.progress_lbl = ctk.CTkLabel(ftr_frm, text="0 / 0 | 0%", font=ctk.CTkFont(size=13))
        self.progress_lbl.grid(row=0, column=2, padx=(0, 20), pady=15, sticky="e")

    # ==========================================
    # PREMIUM ACTIVE OVERLAY
    # ==========================================
    def _show_active_overlay(self):
        if hasattr(self, 'overlay') and self.overlay and self.overlay.winfo_exists():
            self.overlay.destroy()
            
        self.overlay = ctk.CTkToplevel(self)
        self.overlay.overrideredirect(True) # No borders
        self.overlay.attributes("-topmost", True)
        self.overlay.attributes("-alpha", 0.95)
        
        # Position top center
        width = 400
        height = 150
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = 50
        self.overlay.geometry(f"{width}x{height}+{x}+{y}")
        self.overlay.configure(fg_color="#181825")
        
        # Inner border
        inner_frame = ctk.CTkFrame(self.overlay, fg_color="#181825", border_width=2, border_color="#3498db")
        inner_frame.pack(expand=True, fill="both", padx=2, pady=2)
        
        # Drag bar
        drag_bar = ctk.CTkFrame(inner_frame, height=30, corner_radius=0, fg_color="#11111b")
        drag_bar.pack(fill="x", side="top")
        
        title_lbl = ctk.CTkLabel(drag_bar, text="🖱 Auto Typer Active (Drag to move)", font=ctk.CTkFont(size=12, weight="bold"), text_color="gray")
        title_lbl.pack(pady=4)

        # Dragging mechanics
        def start_move(event):
            self.overlay.x = event.x
            self.overlay.y = event.y
        def do_move(event):
            deltax = event.x - self.overlay.x
            deltay = event.y - self.overlay.y
            x = self.overlay.winfo_x() + deltax
            y = self.overlay.winfo_y() + deltay
            self.overlay.geometry(f"+{x}+{y}")

        drag_bar.bind("<Button-1>", start_move)
        drag_bar.bind("<B1-Motion>", do_move)
        title_lbl.bind("<Button-1>", start_move)
        title_lbl.bind("<B1-Motion>", do_move)

        # Content Area
        content = ctk.CTkFrame(inner_frame, fg_color="transparent")
        content.pack(expand=True, fill="both", padx=20, pady=10)

        # Labels
        info_frame = ctk.CTkFrame(content, fg_color="transparent")
        info_frame.pack(fill="x")
        
        self.overlay_status_lbl = ctk.CTkLabel(info_frame, text="✅ PREPARING...", font=ctk.CTkFont(size=14, weight="bold"), text_color="white")
        self.overlay_status_lbl.pack(side="left")
        
        self.overlay_eta_lbl = ctk.CTkLabel(info_frame, text="ETA: --:--   |   0%", font=ctk.CTkFont(size=13, weight="bold"), text_color="#3498db")
        self.overlay_eta_lbl.pack(side="right")

        self.overlay_progress_bar = ctk.CTkProgressBar(content, height=8, progress_color="#3498db")
        self.overlay_progress_bar.pack(fill="x", pady=(10, 15))
        self.overlay_progress_bar.set(0)

        # Buttons
        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(fill="x")
        btn_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.overlay_pause_btn = ctk.CTkButton(btn_frame, text="⏸ Pause", fg_color="#f39c12", text_color="black", hover_color="#d68910", command=self._pause_typing)
        self.overlay_pause_btn.grid(row=0, column=0, padx=5, sticky="ew")

        self.overlay_resume_btn = ctk.CTkButton(btn_frame, text="⏯ Resume", fg_color="#d35400", hover_color="#ba4a00", command=self._resume_typing, state="disabled")
        self.overlay_resume_btn.grid(row=0, column=1, padx=5, sticky="ew")

        self.overlay_stop_btn = ctk.CTkButton(btn_frame, text="⏹ Stop", fg_color="#c0392b", hover_color="#922b21", command=self._stop_typing)
        self.overlay_stop_btn.grid(row=0, column=2, padx=5, sticky="ew")

    def _update_overlay(self, pct, mins, secs):
        if hasattr(self, 'overlay') and self.overlay and self.overlay.winfo_exists():
            self.overlay_progress_bar.set(pct)
            status = "PAUSED" if not self.pause_event.is_set() else f"{mins:02d}:{secs:02d}"
            self.overlay_eta_lbl.configure(text=f"ETA: {status}   |   {pct*100:.0f}%")

    def _sync_overlay_status(self, text, color="white"):
        if hasattr(self, 'overlay') and self.overlay and self.overlay.winfo_exists():
            self.overlay_status_lbl.configure(text=text, text_color=color)
            if "PAUSED" in text or "WAITING" in text:
                self.overlay_pause_btn.configure(state="disabled")
                self.overlay_resume_btn.configure(state="normal")
            elif "TYPING" in text or "Starting" in text or "Resuming" in text:
                self.overlay_pause_btn.configure(state="normal")
                self.overlay_resume_btn.configure(state="disabled")

    def _destroy_active_overlay(self):
        if hasattr(self, 'overlay') and self.overlay and self.overlay.winfo_exists():
            self.overlay.destroy()

    # ==========================================
    # CORE LOGIC & STATE MANAGEMENT
    # ==========================================

    def _set_status(self, text, color=None):
        self.status_lbl.configure(text=text, text_color=color if color else "gray")

    def _update_progress_ui(self):
        if self.total_chars > 0:
            pct = self.typed_chars / self.total_chars
            self.progress_bar.set(pct)
            self.progress_lbl.configure(text=f"{self.typed_chars} / {self.total_chars} | {pct*100:.0f}%")
            
            # Formulate ETA
            try: gap = float(self.speed_entry.get())
            except: gap = 0.03
            rem = self.total_chars - self.typed_chars
            mins, secs = divmod(int(rem * gap), 60)
            
            # Sync to pill
            self._update_overlay(pct, mins, secs)

    def _on_slider_change(self, val):
        self.speed_entry.delete(0, "end")
        self.speed_entry.insert(0, f"{float(val):.3f}")

    def _on_entry_change(self, *_):
        try:
            v = max(0.001, min(0.5, float(self.speed_entry.get())))
            self.speed_var.set(v)
        except ValueError: pass

    def _load_file(self):
        path = ctk.filedialog.askopenfilename(filetypes=[("All files", "*.*")])
        if path:
            try:
                with open(path, "r") as f: content = f.read()
                self.code_text.delete("1.0", "end")
                self.code_text.insert("1.0", content)
            except Exception as e:
                self._set_status("File Error", "#e74c3c")

    def _start_typing(self):
        code = self.code_text.get("1.0", "end").strip()
        if not code:
            self._set_status("⚠ Source Code is empty!", "#f39c12")
            return

        # Read config safely
        try: base_gap = max(0.001, min(0.5, float(self.speed_entry.get())))
        except: base_gap = 0.03
        humanize = self.humanize_var.get()
        vm_mode = self.vm_mode_var.get()
        url = self.url_entry.get().strip()

        # Update GUI states
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.resume_btn.configure(state="normal")
        self.pause_btn.configure(state="normal")
        self.stop_event.clear()
        self.pause_event.clear() # Block initially
        self.typing_active = True
        self.typed_chars = 0
        self.total_chars = len(code.replace('\n', ''))
        self.progress_bar.set(0)
        self._show_active_overlay()

        # Engine Thread
        def engine():
            sel_browser = self.selected_browser.get()
            if url and sel_browser != "none":
                exe = {"edge": "microsoft-edge", "chrome": "google-chrome", "firefox": "firefox"}[sel_browser]
                subprocess.Popen([exe, url])
                for i in range(5, 0, -1):
                    if self.stop_event.is_set(): return self._finish("STOPPED")
                    self.after(0, self._set_status, f"⏳ Browser... {i}s", "#f39c12")
                    self.after(0, self._sync_overlay_status, f"⏳ Browser opening in {i}s...", "#f39c12")
                    time.sleep(1)

            self.after(0, self._set_status, "⏸ PRESS INSERT TO BEGIN", "#d35400")
            self.after(0, self._sync_overlay_status, "⏸ WAITING... (Press Insert)   ", "#d35400")

            def check_pause(initial=False):
                if not self.pause_event.is_set() or initial:
                    self.after(0, self._set_status, "⏸ PAUSED" if not initial else "⏸ WAITING", "#d35400")
                    self.after(0, self._sync_overlay_status, "⏸ PAUSED" if not initial else "⏸ WAITING... (Press Insert)   ", "#d35400")
                    
                    while True:
                        self.pause_event.wait()
                        if self.stop_event.is_set(): return False
                        
                        aborted = False
                        # 3 second delay on resume for safety
                        for i in range(3, 0, -1):
                            if self.stop_event.is_set(): return False
                            if not self.pause_event.is_set(): aborted = True; break
                            self.after(0, self._set_status, f"⏳ {'Starting' if initial else 'Resuming'} {i}s", "#f39c12")
                            self.after(0, self._sync_overlay_status, f"⏳ {'Starting' if initial else 'Resuming'} in {i}s... ", "#f39c12")
                            
                            # Countdown on resume button
                            if hasattr(self, 'overlay') and self.overlay and self.overlay.winfo_exists():
                                self.after(0, lambda sec=i: self.overlay_resume_btn.configure(text=f"⏳ {sec}s..."))
                            time.sleep(1)
                        if not aborted:
                            self.after(0, self._set_status, "⌨ TYPING...", "#2ecc71")
                            self.after(0, self._sync_overlay_status, "⌨ TYPING ACTIVE       ", "#2ecc71")
                            if hasattr(self, 'overlay') and self.overlay and self.overlay.winfo_exists():
                                self.after(0, lambda: self.overlay_resume_btn.configure(text="⏯ Resume"))
                            return True
                return True

            if not check_pause(initial=True): return self._finish("STOPPED")

            # Main Typing Loop
            last_gui_update = time.time()
            
            # 100% Clone Typing: Iterate exactly character by character
            for char in code:
                if not check_pause(): return self._finish("STOPPED")
                
                if char == '\n':
                    self.kb.press(Key.enter)
                    self.kb.release(Key.enter)
                    if humanize: time.sleep(base_gap * random.uniform(1.2, 2.0))
                    else: time.sleep(base_gap)
                elif char == '\t':
                    self.kb.press(Key.tab)
                    self.kb.release(Key.tab)
                    time.sleep(base_gap)
                else:
                    if vm_mode:
                        try:
                            # xdotool flawlessly handles modifier synthesis (Shift) across hypervisor barriers
                            subprocess.run(['xdotool', 'type', '--clearmodifiers', char])
                        except FileNotFoundError:
                            self.kb.type(char) # Fallback if xdotool is missing
                    else:
                        self.kb.type(char) # Implicitly handles Shift, but frequently blind-drops on VMs
                    
                    # Human variance
                    current_gap = base_gap
                    if humanize:
                        current_gap *= random.uniform(0.6, 1.6) # Variable speed
                        if char in [' ', '.', ',', ':', '(']:
                            current_gap *= 1.3 # Slightly longer pauses on punctuation
                    time.sleep(current_gap)

                self.typed_chars += 1
                
                # Decoupled GUI updates (max 2fps)
                if time.time() - last_gui_update > 0.5 or self.typed_chars == self.total_chars:
                    self.after(0, self._update_progress_ui)
                    last_gui_update = time.time()

            self._finish("✅ DONE")

        Thread(target=engine, daemon=True).start()

    def _finish(self, status):
        self.typing_active = False
        color = "#2ecc71" if "DONE" in status else "#e74c3c"
        self.after(0, self._set_status, status, color)
        self.after(0, self._update_progress_ui)
        self.after(0, self._destroy_active_overlay)
        self.after(0, lambda: self.start_btn.configure(state="normal"))
        self.after(0, lambda: self.stop_btn.configure(state="disabled"))
        self.after(0, lambda: self.resume_btn.configure(state="disabled"))
        self.after(0, lambda: self.pause_btn.configure(state="disabled"))

    # ==========================================
    # HOTKEYS & CONTROLS
    # ==========================================
    def _pause_typing(self):
        if self.typing_active:
            self.pause_event.clear()
            self._set_status("⏸ PAUSED", "#e67e22")
            self._sync_overlay_status("⏸ PAUSED", "#f39c12")

    def _resume_typing(self):
        self.pause_event.set()

    def _stop_typing(self):
        self.stop_event.set()
        self.pause_event.set() # Unblock

    def _setup_hotkeys(self):
        def on_press(key):
            try:
                if key == pynput_keyboard.Key.escape: self._pause_typing()
                elif key == pynput_keyboard.Key.insert: self._resume_typing()
            except AttributeError: pass
        listener = pynput_keyboard.Listener(on_press=on_press)
        listener.daemon = True
        listener.start()
        self.bind("<Insert>", lambda e: self._resume_typing())
        self.bind("<Escape>", lambda e: self._pause_typing())


if __name__ == "__main__":
    app = AutoTyperPro()
