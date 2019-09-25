import os
import string

directions = ["up", "down", "left", "right"]

arrows = [f"arrow_{d}" for d in directions]

characters = list(string.ascii_lowercase + string.digits)

modifiers = ['control', 'shift', 'alt']
keyboard = ['space', 'enter', 'escape', 'delete', 'page_up', 'page_down', '(', '[', '{', ')', ']', '}']

mouse = [f"mouse{n}" for n in [1, 2, 3]]

inputs = (
        characters
        + arrows
        + keyboard
        + mouse
          )

inputs_up = [f"{i}-up" for i in inputs]

events = inputs + inputs_up


def to_fn_name(event: str):
    if event.endswith("-up"):
        event = event[:-3] + "_released"
    if event[0].isnumeric():  # :( method name can't start with a digit
        event = "_" + event
    changes = {
        "(": "parenthesis_left",
        ")": "parenthesis_right",
        "[": "bracket_left",
        "]": "bracket_right",
        "{": "brace_left",
        "}": "brace_right",
    }
    for char, name in changes.items():
        event = event.replace(char, name)
    return event


event_fn_dict = {e: to_fn_name(e) for e in events}

if __name__ == "__main__":
    with open(os.path.join(os.path.dirname(__file__), "commandmgr.py"), "w") as f:
        f.write("class BaseCommandMgr:\n")
        f.write("    def __init__(self):\n")
        f.write("        self.mapping = {\n")
        for event, fn_name in event_fn_dict.items():
            f.write(f'            "{event}": self.{fn_name},\n')
        f.write("        }\n")
        f.write("\n")
        for fn_name in event_fn_dict.values():
            f.write(f"    def {fn_name}(self):\n")
            f.write("        pass\n")
            f.write("\n")
