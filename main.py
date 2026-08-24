import keyboard
import pyperclip
import json


autofill_mode = False

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


def load_data():
    with open("data.json", "r") as file:
        return json.load(file)


def paste_field(data, field):
    pyperclip.copy(data[field])
    keyboard.press_and_release("ctrl+v")


def handle_autofill(data, field):
    print(f"Autofilling {field}")
    paste_field(data, field)


def enable_autofill(data):
    global autofill_mode

    if autofill_mode:
        return

    autofill_mode = True

    for key, field in fields.items():
        keyboard.add_hotkey(
            key,
            lambda f=field: handle_autofill(data, f),
            suppress=True
        )

    print("Autofill ON")


def disable_autofill():
    global autofill_mode

    if not autofill_mode:
        return

    autofill_mode = False

    # Remove all currently registered autofill hotkeys
    for key in fields:
        keyboard.remove_hotkey(key)

    print("Autofill OFF")


def toggle_autofill(data):
    if autofill_mode:
        disable_autofill()
    else:
        enable_autofill(data)


def main():
    data = load_data()

    keyboard.add_hotkey(
        "ctrl+alt+space",
        lambda: toggle_autofill(data)
    )

    print("Application Assistant is Active")
    print("Ctrl + Alt + Space → Toggle autofill")
    print("ESC → Quit")

    keyboard.wait("esc")


if __name__ == "__main__":
    main()