import customtkinter as ctk

from hotkeys import (
    FIELD_GROUPS,
    FIELD_HOTKEY,
    FIELD_LABELS,
    autofill_mode,
    copy_field,
    disable_autofill,
    get_data,
    initialize_hotkeys,
    paste_field,
    save_data,
    set_data,
    set_status_callback,
    toggle_autofill,
)

# Distinctive utility palette — slate + amber, not purple defaults
COLORS = {
    "bg": "#12151c",
    "surface": "#1a1f2b",
    "surface_alt": "#222836",
    "border": "#2e3648",
    "text": "#e8ecf4",
    "muted": "#8b95a8",
    "accent": "#e8a838",
    "accent_hover": "#f0b84d",
    "accent_dim": "#3d3018",
    "on": "#3dba7a",
    "on_dim": "#1a3d2a",
    "off": "#6b7280",
    "danger": "#e07070",
}

LONG_FIELDS = {"job_1_desc", "job_2_desc", "address"}
PASTE_DELAY_MS = 1500


class ApplicationAssistantApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Application Assistant")
        self.geometry("780x720")
        self.minsize(640, 560)
        self.configure(fg_color=COLORS["bg"])

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self._entries = {}
        self._paste_after_id = None
        self._countdown_after_id = None

        self._build_header()
        self._build_controls()
        self._build_fields()
        self._build_footer()

        set_status_callback(self._on_autofill_status)
        initialize_hotkeys(blocking=False)
        self._load_entries_from_data()
        self._on_autofill_status(autofill_mode)

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 8))

        title_col = ctk.CTkFrame(header, fg_color="transparent")
        title_col.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            title_col,
            text="Application Assistant",
            font=ctk.CTkFont(family="Segoe UI Semibold", size=26),
            text_color=COLORS["text"],
            anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_col,
            text="Paste profile fields into forms with a hotkey or one click.",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["muted"],
            anchor="w",
        ).pack(anchor="w", pady=(2, 0))

        self.status_pill = ctk.CTkLabel(
            header,
            text="Autofill OFF",
            font=ctk.CTkFont(family="Segoe UI Semibold", size=12),
            text_color=COLORS["muted"],
            fg_color=COLORS["surface_alt"],
            corner_radius=8,
            padx=14,
            pady=8,
        )
        self.status_pill.pack(side="right", padx=(12, 0))

    def _build_controls(self):
        controls = ctk.CTkFrame(
            self,
            fg_color=COLORS["surface"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
        )
        controls.pack(fill="x", padx=24, pady=(8, 12))

        inner = ctk.CTkFrame(controls, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=14)

        self.toggle_btn = ctk.CTkButton(
            inner,
            text="Enable Autofill",
            font=ctk.CTkFont(family="Segoe UI Semibold", size=14),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            text_color="#1a1408",
            height=40,
            width=160,
            corner_radius=8,
            command=self._toggle_autofill,
        )
        self.toggle_btn.pack(side="left")

        hint = ctk.CTkLabel(
            inner,
            text="Ctrl + Alt + Space  ·  then press a field key (f, e, p…)",
            font=ctk.CTkFont(family="Consolas", size=12),
            text_color=COLORS["muted"],
            anchor="w",
        )
        hint.pack(side="left", padx=(16, 0))

        self.save_btn = ctk.CTkButton(
            inner,
            text="Save Profile",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            fg_color=COLORS["surface_alt"],
            hover_color=COLORS["border"],
            text_color=COLORS["text"],
            height=40,
            width=120,
            corner_radius=8,
            border_width=1,
            border_color=COLORS["border"],
            command=self._save_profile,
        )
        self.save_btn.pack(side="right")

        self.feedback = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["accent"],
            anchor="w",
        )
        self.feedback.pack(fill="x", padx=28, pady=(0, 4))

    def _build_fields(self):
        self.scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS["surface"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
            scrollbar_button_color=COLORS["border"],
            scrollbar_button_hover_color=COLORS["muted"],
        )
        self.scroll.pack(fill="both", expand=True, padx=24, pady=(0, 8))

        for group_name, field_keys in FIELD_GROUPS:
            group = ctk.CTkFrame(self.scroll, fg_color="transparent")
            group.pack(fill="x", padx=12, pady=(14, 4))

            ctk.CTkLabel(
                group,
                text=group_name.upper(),
                font=ctk.CTkFont(family="Segoe UI Semibold", size=11),
                text_color=COLORS["accent"],
                anchor="w",
            ).pack(anchor="w", pady=(0, 8))

            for field in field_keys:
                self._add_field_row(group, field)

    def _add_field_row(self, parent, field):
        row = ctk.CTkFrame(parent, fg_color=COLORS["surface_alt"], corner_radius=8)
        row.pack(fill="x", pady=4)

        top = ctk.CTkFrame(row, fg_color="transparent")
        top.pack(fill="x", padx=12, pady=(10, 4))

        label_text = FIELD_LABELS.get(field, field)
        hotkey = FIELD_HOTKEY.get(field, "")

        ctk.CTkLabel(
            top,
            text=label_text,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text"],
            anchor="w",
        ).pack(side="left")

        if hotkey:
            ctk.CTkLabel(
                top,
                text=hotkey.upper(),
                font=ctk.CTkFont(family="Consolas", size=11),
                text_color=COLORS["accent"],
                fg_color=COLORS["accent_dim"],
                corner_radius=4,
                width=28,
                height=22,
            ).pack(side="left", padx=(8, 0))

        body = ctk.CTkFrame(row, fg_color="transparent")
        body.pack(fill="x", padx=12, pady=(0, 10))

        if field in LONG_FIELDS:
            widget = ctk.CTkTextbox(
                body,
                height=72,
                font=ctk.CTkFont(family="Segoe UI", size=13),
                fg_color=COLORS["bg"],
                text_color=COLORS["text"],
                border_width=1,
                border_color=COLORS["border"],
                corner_radius=6,
            )
            widget.pack(side="left", fill="x", expand=True, padx=(0, 8))
        else:
            widget = ctk.CTkEntry(
                body,
                height=34,
                font=ctk.CTkFont(family="Segoe UI", size=13),
                fg_color=COLORS["bg"],
                text_color=COLORS["text"],
                border_width=1,
                border_color=COLORS["border"],
                corner_radius=6,
            )
            widget.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self._entries[field] = widget

        btn_col = ctk.CTkFrame(body, fg_color="transparent")
        btn_col.pack(side="right")

        ctk.CTkButton(
            btn_col,
            text="Copy",
            width=64,
            height=32,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color=COLORS["border"],
            hover_color=COLORS["muted"],
            text_color=COLORS["text"],
            corner_radius=6,
            command=lambda f=field: self._copy_now(f),
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            btn_col,
            text="Paste",
            width=64,
            height=32,
            font=ctk.CTkFont(family="Segoe UI Semibold", size=12),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            text_color="#1a1408",
            corner_radius=6,
            command=lambda f=field: self._schedule_paste(f),
        ).pack(side="left")

    def _build_footer(self):
        footer = ctk.CTkLabel(
            self,
            text="Paste waits 1.5s so you can click into the target field first.",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLORS["muted"],
        )
        footer.pack(pady=(0, 14))

    def _get_entry_value(self, field):
        widget = self._entries[field]
        if isinstance(widget, ctk.CTkTextbox):
            return widget.get("1.0", "end-1c")
        return widget.get()

    def _set_entry_value(self, field, value):
        widget = self._entries[field]
        text = "" if value is None else str(value)
        if isinstance(widget, ctk.CTkTextbox):
            widget.delete("1.0", "end")
            widget.insert("1.0", text)
        else:
            widget.delete(0, "end")
            widget.insert(0, text)

    def _collect_data(self):
        data = get_data() or {}
        for field in self._entries:
            data[field] = self._get_entry_value(field)
        return data

    def _load_entries_from_data(self):
        data = get_data() or {}
        for field in self._entries:
            self._set_entry_value(field, data.get(field, ""))

    def _set_feedback(self, message, color=None):
        self.feedback.configure(text=message, text_color=color or COLORS["accent"])

    def _toggle_autofill(self):
        # Persist current edits so hotkeys use fresh values
        set_data(self._collect_data())
        toggle_autofill()

    def _on_autofill_status(self, enabled):
        def update():
            if enabled:
                self.status_pill.configure(
                    text="Autofill ON",
                    text_color=COLORS["on"],
                    fg_color=COLORS["on_dim"],
                )
                self.toggle_btn.configure(
                    text="Disable Autofill",
                    fg_color=COLORS["danger"],
                    hover_color="#c85858",
                    text_color=COLORS["text"],
                )
                self._set_feedback("Autofill armed — press a field key to paste.", COLORS["on"])
            else:
                self.status_pill.configure(
                    text="Autofill OFF",
                    text_color=COLORS["muted"],
                    fg_color=COLORS["surface_alt"],
                )
                self.toggle_btn.configure(
                    text="Enable Autofill",
                    fg_color=COLORS["accent"],
                    hover_color=COLORS["accent_hover"],
                    text_color="#1a1408",
                )
                self._set_feedback("")

        self.after(0, update)

    def _save_profile(self):
        data = self._collect_data()
        save_data(data)
        self._set_feedback("Profile saved to data.json.", COLORS["on"])

    def _copy_now(self, field):
        set_data(self._collect_data())
        if copy_field(field):
            label = FIELD_LABELS.get(field, field)
            self._set_feedback(f"Copied {label} to clipboard.")
        else:
            self._set_feedback("Nothing to copy.", COLORS["danger"])

    def _cancel_pending_paste(self):
        if self._paste_after_id is not None:
            self.after_cancel(self._paste_after_id)
            self._paste_after_id = None
        if self._countdown_after_id is not None:
            self.after_cancel(self._countdown_after_id)
            self._countdown_after_id = None

    def _schedule_paste(self, field):
        self._cancel_pending_paste()
        set_data(self._collect_data())
        copy_field(field)

        label = FIELD_LABELS.get(field, field)
        remaining = PASTE_DELAY_MS // 1000

        def tick(left):
            if left <= 0:
                return
            self._set_feedback(f"Click the form field… pasting {label} in {left}s")
            self._countdown_after_id = self.after(1000, lambda: tick(left - 1))

        tick(remaining)

        def do_paste():
            self._paste_after_id = None
            if paste_field(field):
                self._set_feedback(f"Pasted {label}.", COLORS["on"])
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
