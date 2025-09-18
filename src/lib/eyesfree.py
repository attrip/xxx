from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class Command:
    name: str
    arg: Optional[str] = None


def parse_command(line: str) -> Tuple[bool, Optional[Command]]:
    """Parse a slash command from the input line.

    Recognized:
    /undo, /read, /done, /help, /save <path>
    Returns (is_command, Command|None)
    """
    if not line or not line.startswith("/"):
        return False, None
    parts = line.strip().split(maxsplit=1)
    name = parts[0][1:].lower()
    arg = parts[1].strip() if len(parts) > 1 else None
    if name in {"undo", "read", "done", "help"}:
        return True, Command(name)
    if name == "save":
        return True, Command(name, arg)
    # Unknown commands are still considered commands for help
    return True, Command("help")

