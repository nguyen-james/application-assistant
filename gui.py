import customtkinter as ctk

from hotkeys import (
    FIELD_GROUPS,
    FIELD_HOTKEY,
    autofill_mode,
    copy_field,
    disable_autofill,
    initialize_hotkeys,
    paste_field,
    set_status_callback,
    toggle_autofill,
)

COLORS = {
    "bg": "#12151c",
    "surface": "#1a1f2b",
    "border": "#2e3648",
    "text": "#e8ecf4",
    "muted": "#8b95a8",
    "accent": "#e8a838",
    "accent_hover": "#f0b84d",
    "on": "#3dba7a",
    "on_dim": "#1a3d2a",
    "danger": "#e07070",
}

PASTE_DELAY_MS = 1500
CATEGORY_COLUMNS = 2
# Two rows only — stack Experience + Links in the shorter column so nothing clips
LAYOUT = [
    [["Personal"], ["Address"]],
    [["Education"], ["Experience", "Links"]],
]


class ApplicationAssistantApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Application Assistant")
        self.geometry("420x360")
        self.minsize(360, 300)
        self.configure(fg_color=COLORS["bg"])

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self._paste_after_id = None
        self._countdown_after_id = None
        self._always_on_top = True

        self._build_controls()
        self._build_buttons()
        self._build_feedback()

        self.attributes("-topmost", True)

        set_status_callback(self._on_autofill_status)
        initialize_hotkeys(blocking=False)
        self._on_autofill_status(autofill_mode)

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_controls(self):
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.pack(fill="x", padx=8, pady=(8, 2))

        self.toggle_btn = ctk.CTkButton(
            bar,
            text="Autofill OFF",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            text_color="#1a1408",
            height=24,
            width=100,
            corner_radius=5,
            command=toggle_autofill,
        )
        self.toggle_btn.pack(side="left")

        self.pin_switch = ctk.CTkSwitch(
            bar,
            text="Pin",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLORS["muted"],
            progress_color=COLORS["accent"],
            button_color=COLORS["text"],
            button_hover_color=COLORS["accent_hover"],
            fg_color=COLORS["border"],
            width=36,
            command=self._toggle_always_on_top,
        )
        self.pin_switch.select()
        self.pin_switch.pack(side="right")

    def _build_buttons(self):
        groups = dict(FIELD_GROUPS)
        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=6, pady=2)

        for col in range(CATEGORY_COLUMNS):
            grid.grid_columnconfigure(col, weight=1, uniform="cats")

        for row_index, row_cells in enumerate(LAYOUT):
            for col_index, stacked_names in enumerate(row_cells):
                cell = ctk.CTkFrame(grid, fg_color="transparent")
                cell.grid(row=row_index, column=col_index, sticky="nsew", padx=3, pady=2)

                for group_name in stacked_names:
                    self._add_category(cell, group_name, groups[group_name])

    def _add_category(self, parent, group_name, field_keys):
        category = ctk.CTkFrame(parent, fg_color="transparent")
        category.pack(fill="x", pady=(0, 4))

        ctk.CTkLabel(
            category,
            text=group_name,
            font=ctk.CTkFont(family="Segoe UI Semibold", size=10),
            text_color=COLORS["accent"],
            anchor="w",
            height=16,
        ).pack(fill="x", padx=2, pady=(0, 1))

        for field in field_keys:
            hotkey = FIELD_HOTKEY.get(field, "")
            label = f"{field} [{hotkey}]" if hotkey else field

            ctk.CTkButton(
                category,
                text=label,
                font=ctk.CTkFont(family="Consolas", size=10),
                fg_color=COLORS["surface"],
                hover_color=COLORS["border"],
                text_color=COLORS["text"],
                height=22,
                corner_radius=4,
                border_width=1,
                border_color=COLORS["border"],
                command=lambda f=field: self._schedule_paste(f),
            ).pack(fill="x", padx=2, pady=1)

    def _build_feedback(self):
        self.feedback = ctk.CTkLabel(
            self,
            text="Ctrl+Alt+Space toggles autofill",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=COLORS["muted"],
            anchor="w",
            height=16,
        )
        self.feedback.pack(fill="x", padx=10, pady=(0, 8))

    def _set_feedback(self, message, color=None):
        self.feedback.configure(text=message, text_color=color or COLORS["accent"])

    def _toggle_always_on_top(self):
        self._always_on_top = bool(self.pin_switch.get())
        self.attributes("-topmost", self._always_on_top)

    def _on_autofill_status(self, enabled):
        def update():
            if enabled:
                self.toggle_btn.configure(
                    text="Autofill ON",
                    fg_color=COLORS["on"],
                    hover_color="#4ad08c",
                    text_color="#0c1a12",
                )
                self._set_feedback("Armed — press a field key to paste.", COLORS["on"])
            else:
                self.toggle_btn.configure(
                    text="Autofill OFF",
                    fg_color=COLORS["accent"],
                    hover_color=COLORS["accent_hover"],
                    text_color="#1a1408",
                )
                self._set_feedback("Ctrl+Alt+Space toggles autofill", COLORS["muted"])

        self.after(0, update)

    def _cancel_pending_paste(self):
        if self._paste_after_id is not None:
            self.after_cancel(self._paste_after_id)
            self._paste_after_id = None
        if self._countdown_after_id is not None:
            self.after_cancel(self._countdown_after_id)
            self._countdown_after_id = None

    def _schedule_paste(self, field):
        self._cancel_pending_paste()
        copy_field(field)

        remaining = PASTE_DELAY_MS // 1000

        def tick(left):
            if left <= 0:
                return
            self._set_feedback(f"Click target… pasting {field} in {left}s")
            self._countdown_after_id = self.after(1000, lambda: tick(left - 1))

        tick(remaining)

        def do_paste():
            self._paste_after_id = None
            if paste_field(field):
                self._set_feedback(f"Pasted {field}.", COLORS["on"])
            else:
                self._set_feedback("Paste failed.", COLORS["danger"])

        self._paste_after_id = self.after(PASTE_DELAY_MS, do_paste)

    def _on_close(self):
        self._cancel_pending_paste()
        disable_autofill()
        self.destroy()


def run_app():
    app = ApplicationAssistantApp()
    app.mainloop()
