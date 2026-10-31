"""
ui.py  -  Terminal UI helpers
Indie Game: Skill Tree & Quest Dependency Engine

DBMS Assignment - 10 (Mini Project)
Name    : Aditya Yadnik
Class   : SY CS-A
Roll No : 2070134
PRN     : 1251070951
"""

import os
import shutil


class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    RED     = "\033[91m"
    CYAN    = "\033[96m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    ORANGE  = "\033[38;5;214m"


def enable_ansi():
    if os.name == "nt":
        os.system("")


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def width() -> int:
    return shutil.get_terminal_size((80, 24)).columns


def hr(char="-", color=C.DIM):
    print(color + char * width() + C.RESET)


def banner(title: str, subtitle: str = "", assignment: str = "", student: str = ""):
    w = width()
    clear()
    print(C.MAGENTA + "=" * w + C.RESET)
    if assignment:
        pad = max(0, (w - len(assignment)) // 2)
        print(C.BOLD + C.YELLOW + " " * pad + assignment + C.RESET)
        print(C.MAGENTA + "-" * w + C.RESET)
    pad = max(0, (w - len(title)) // 2)
    print(C.BOLD + C.MAGENTA + " " * pad + title + C.RESET)
    if subtitle:
        pad2 = max(0, (w - len(subtitle)) // 2)
        print(C.DIM + " " * pad2 + subtitle + C.RESET)
    if student:
        print(C.MAGENTA + "-" * w + C.RESET)
        pad3 = max(0, (w - len(student)) // 2)
        print(C.CYAN + " " * pad3 + student + C.RESET)
    print(C.MAGENTA + "=" * w + C.RESET)
    print()


def section(title: str):
    print()
    print(C.CYAN + C.BOLD + f"  >> {title}" + C.RESET)
    hr("-", C.DIM)


def success(msg: str):
    print(C.GREEN + f"  [OK]  {msg}" + C.RESET)


def error(msg: str):
    print(C.RED + f"  [ERR] {msg}" + C.RESET)


def warn(msg: str):
    print(C.YELLOW + f"  [!]  {msg}" + C.RESET)


def info(msg: str):
    print(C.BLUE + f"  [i]  {msg}" + C.RESET)


def table(rows: list, headers: list, col_widths: list = None):
    if not rows:
        warn("No records found.")
        return
    if col_widths is None:
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(cell)))
    fmt = "  " + "  ".join(f"{{:<{w}}}" for w in col_widths)
    sep = "  " + "  ".join("-" * w for w in col_widths)
    print(C.BOLD + fmt.format(*headers) + C.RESET)
    print(C.DIM + sep + C.RESET)
    for row in rows:
        print(fmt.format(*[str(v)[:col_widths[i]] for i, v in enumerate(row)]))


def prompt(label: str, default: str = "") -> str:
    hint = f" [{default}]" if default else ""
    val = input(f"  {C.YELLOW}{label}{hint}: {C.RESET}").strip()
    return val if val else default


def prompt_int(label: str, default: int = 0) -> int:
    while True:
        raw = prompt(label, str(default))
        try:
            return int(raw)
        except ValueError:
            error("Please enter a whole number.")


def prompt_list(label: str) -> list:
    """Prompt for a comma-separated list; returns list of stripped strings."""
    raw = prompt(f"{label} (comma-separated, or blank for none)")
    if not raw:
        return []
    return [x.strip().upper() for x in raw.split(",") if x.strip()]


def prompt_choice(options: list, label: str = "Choose") -> int:
    for i, opt in enumerate(options, 1):
        print(f"  {C.CYAN}{i:>2}{C.RESET}. {opt}")
    while True:
        raw = prompt(label)
        try:
            n = int(raw)
            if 1 <= n <= len(options):
                return n
        except ValueError:
            pass
        error(f"Enter a number between 1 and {len(options)}.")


def pause():
    input(C.DIM + "\n  Press Enter to continue..." + C.RESET)


def show_document(doc: dict, title: str = "Document"):
    """Pretty-print a MongoDB document."""
    section(title)
    for k, v in doc.items():
        if k == "_id":
            print(f"  {C.DIM}_id    {C.RESET}: {C.DIM}{v}{C.RESET}")
        elif isinstance(v, list):
            print(f"  {C.CYAN}{k:<14}{C.RESET}: [{', '.join(str(i) for i in v)}]")
        elif isinstance(v, dict):
            print(f"  {C.CYAN}{k:<14}{C.RESET}: " + "{" + ", ".join(f"{dk}: {dv}" for dk, dv in v.items()) + "}")
        else:
            print(f"  {C.CYAN}{k:<14}{C.RESET}: {v}")
