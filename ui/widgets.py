"""
Auto Typer Pro — Custom Reusable Widgets
Toast notifications, stat cards, and other reusable UI components.
"""
import customtkinter as ctk


class Toast(ctk.CTkToplevel):
    """Non-blocking toast notification that auto-dismisses."""

    def __init__(self, parent, message: str, color: str = "#2ecc71", duration: int = 3000):
        super().__init__(parent)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.0)

        # Position bottom-right of parent
        px = parent.winfo_rootx() + parent.winfo_width() - 350
        py = parent.winfo_rooty() + parent.winfo_height() - 80
        self.geometry(f"320x50+{px}+{py}")
        self.configure(fg_color=color)

        frame = ctk.CTkFrame(self, fg_color=color, corner_radius=12)
        frame.pack(expand=True, fill="both", padx=2, pady=2)

        ctk.CTkLabel(frame, text=message, font=ctk.CTkFont(size=13, weight="bold"),
                     text_color="white").pack(expand=True, padx=15)

        # Fade in
        self._fade_in(0.0)
        self.after(duration, self._fade_out, 1.0)

    def _fade_in(self, alpha):
        if alpha < 0.95:
            alpha += 0.1
            self.attributes("-alpha", alpha)
            self.after(30, self._fade_in, alpha)
        else:
            self.attributes("-alpha", 0.95)

    def _fade_out(self, alpha):
        if alpha > 0.05:
            alpha -= 0.1
            try:
                self.attributes("-alpha", alpha)
                self.after(30, self._fade_out, alpha)
            except Exception:
                pass
        else:
            try:
                self.destroy()
            except Exception:
                pass


class StatCard(ctk.CTkFrame):
    """A small stat display card with label + value."""

    def __init__(self, parent, label: str, value: str = "—", accent: str = "#3498db", **kwargs):
        super().__init__(parent, corner_radius=10, border_width=1, border_color=accent, **kwargs)

        self._label = ctk.CTkLabel(self, text=label, font=ctk.CTkFont(size=11),
                                   text_color="#6c7086")
        self._label.pack(padx=12, pady=(8, 0))

        self._value = ctk.CTkLabel(self, text=value, font=ctk.CTkFont(size=18, weight="bold"),
                                   text_color=accent)
        self._value.pack(padx=12, pady=(0, 8))

    def set_value(self, value: str):
        self._value.configure(text=value)

    def set_color(self, color: str):
        self._value.configure(text_color=color)
        self.configure(border_color=color)


class SectionLabel(ctk.CTkLabel):
    """Styled section header label."""

    def __init__(self, parent, text: str, **kwargs):
        super().__init__(parent, text=text,
                         font=ctk.CTkFont(size=13, weight="bold"),
                         anchor="w", **kwargs)


class IconButton(ctk.CTkButton):
    """Small icon-style button."""

    def __init__(self, parent, text: str, color: str = "#3498db", **kwargs):
        super().__init__(parent, text=text, width=35, height=30,
                         fg_color=color, hover_color=self._darken(color),
                         font=ctk.CTkFont(size=14), corner_radius=8, **kwargs)

    @staticmethod
    def _darken(hex_color: str) -> str:
        """Darken a hex color by 20%."""
        try:
            r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
            r, g, b = int(r * 0.8), int(g * 0.8), int(b * 0.8)
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            return hex_color
