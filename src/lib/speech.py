from __future__ import annotations

import os
import platform
import shlex
import shutil
import subprocess
from typing import Optional


def _is_dry_run(dry_run: Optional[bool]) -> bool:
    if dry_run is not None:
        return dry_run
    return os.getenv("SPEECH_DRY_RUN", "0") == "1"


def is_mac() -> bool:
    return platform.system().lower() == "darwin"


def speak(text: str, voice: Optional[str] = None, rate: Optional[int] = None, *, enabled: bool = True, dry_run: Optional[bool] = None) -> bool:
    """Speak the given text.

    macOS: uses `say` if available. Others: no-op (returns False) unless dry run.
    Returns True if action was performed (or simulated in dry-run).
    """
    if not enabled or not text:
        return False

    if _is_dry_run(dry_run):
        return True

    if is_mac() and shutil.which("say"):
        cmd = ["say"]
        if voice:
            cmd += ["-v", voice]
        if rate:
            cmd += ["-r", str(rate)]
        cmd += [text]
        try:
            subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception:
            return False
    return False


def chime(sound: str = "Glass", *, enabled: bool = True, dry_run: Optional[bool] = None) -> bool:
    """Play a short cue sound.

    macOS: plays a system sound via `afplay`.
    Others: falls back to terminal bell (print("\a")) if not in dry-run.
    Returns True if action was performed (or simulated in dry-run).
    """
    if not enabled:
        return False

    if _is_dry_run(dry_run):
        return True

    if is_mac() and shutil.which("afplay"):
        path = f"/System/Library/Sounds/{sound}.aiff"
        if not os.path.exists(path):
            path = "/System/Library/Sounds/Glass.aiff"
        try:
            subprocess.run(["afplay", path], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception:
            return False
    else:
        try:
            # Terminal bell as a minimal cue
            print("\a", end="", flush=True)
            return True
        except Exception:
            return False

