import keyboard
import pyperclip
import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent / "data.json"
EXAMPLE_PATH = Path(__file__).resolve().parent / "example-data.json"

autofill_mode = False
_status_callback = None
_data = None

fields = {
    "f": "first_name",
    "l": "last_name",
    "n": "full_name",
    "e": "email",
    "p": "phone_num",
    "a": "address",
    "c": "city",
    "s": "state",
    "z": "zipcode",
    "o": "country",
    "u": "school",
    "d": "degree",
    "m": "major",
    "g": "gpa",
    "1": "job_1_desc",
    "2": "job_2_desc",
    "i": "linkedin",
    "w": "portfolio",
    "h": "github",
}

FIELD_HOTKEY = {field: key for key, field in fields.items()}

FIELD_LABELS = {
    "first_name": "First Name",
    "last_name": "Last Name",
    "full_name": "Full Name",
    "email": "Email",
    "phone_num": "Phone",
    "address": "Address",
    "city": "City",
    "state": "State",
    "zipcode": "Zip Code",
    "country": "Country",
    "school": "School",
    "degree": "Degree",
    "major": "Major",
    "gpa": "GPA",
    "job_1_desc": "Job 1 Description",
    "job_2_desc": "Job 2 Description",
    "linkedin": "LinkedIn",
    "portfolio": "Portfolio",
    "github": "GitHub",
}

FIELD_GROUPS = [
    ("Personal", ["first_name", "last_name", "full_name", "email", "phone_num"]),
    ("Address", ["address", "city", "state", "zipcode", "country"]),
    ("Education", ["school", "degree", "major", "gpa"]),
    ("Experience", ["job_1_desc", "job_2_desc"]),
    ("Links", ["linkedin", "portfolio", "github"]),
]


def _notify_status():
    if _status_callback is not None:
        _status_callback(autofill_mode)


def set_status_callback(callback):
    global _status_callback
    _status_callback = callback


def get_data():
    return _data


def set_data(data):
    global _data
    _data = data


def load_data():
    global _data
    if not DATA_PATH.exists() and EXAMPLE_PATH.exists():
        DATA_PATH.write_text(EXAMPLE_PATH.read_text(encoding="utf-8"), encoding="utf-8")

    with open(DATA_PATH, "r", encoding="utf-8") as file:
        _data = json.load(file)
    return _data


def save_data(data=None):
    global _data
    if data is not None:
        _data = data
    with open(DATA_PATH, "w", encoding="utf-8") as file:
        json.dump(_data, file, indent=2)
        file.write("\n")


def paste_field(field, data=None):
    source = data if data is not None else _data
    if source is None or field not in source:
        return False
    value = source.get(field, "")
    if value is None:
        value = ""
    pyperclip.copy(str(value))
    keyboard.press_and_release("ctrl+v")
    return True


def copy_field(field, data=None):
    source = data if data is not None else _data
    if source is None or field not in source:
        return False
    value = source.get(field, "")
    if value is None:
        value = ""
    pyperclip.copy(str(value))
    return True


def handle_autofill(field):
    print(f"Autofilling {field}")
    paste_field(field)


def enable_autofill():
    global autofill_mode

    if autofill_mode:
        return

    autofill_mode = True

    for key, field in fields.items():
        keyboard.add_hotkey(
            key,
            lambda f=field: handle_autofill(f),
            suppress=True,
        )

    print("Autofill ON")
    _notify_status()


def disable_autofill():
    global autofill_mode

    if not autofill_mode:
        return

    autofill_mode = False

    for key in fields:
        try:
            keyboard.remove_hotkey(key)
        except KeyError:
            pass

    print("Autofill OFF")
    _notify_status()


def toggle_autofill():
    if autofill_mode:
        disable_autofill()
    else:
        enable_autofill()
    return autofill_mode


def initialize_hotkeys(blocking=False):
    load_data()

    keyboard.add_hotkey("ctrl+alt+space", toggle_autofill)

    print("Application Assistant is Running")
    print("Ctrl + Alt + Space - Toggle autofill")

    if blocking:
        print("ESC - Quit")
        keyboard.wait("esc")
        disable_autofill()
