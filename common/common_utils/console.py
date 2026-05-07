import os
from rich.console import Console

if os.name != 'nt' and "TERM" not in os.environ:
    os.environ["TERM"] = "xterm-256color"

# Force terminal true helps with spinner visibility in sub-shells
console = Console(force_terminal=True)

def get_console():
    return console