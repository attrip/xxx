from __future__ import annotations

import os
from typing import Optional


def _dry_text() -> Optional[str]:
    if os.getenv("STT_DRY_RUN", "0") == "1":
        return os.getenv("STT_DRY_RUN_TEXT", "")
    return None


def has_speech_recognition() -> bool:
    try:
        import speech_recognition  # type: ignore

        return True
    except Exception:
        return False


def transcribe_once(lang: str = "ja-JP", timeout: float = 3.0, phrase_time_limit: float = 6.0) -> str:
    """Capture microphone audio and transcribe once.

    - Dry run: set STT_DRY_RUN=1 and optionally STT_DRY_RUN_TEXT to bypass audio.
    - If SpeechRecognition is unavailable, returns empty string.
    - Uses Google recognizer when available; offline engines are optional.
    """
    dry = _dry_text()
    if dry is not None:
        return dry

    try:
        import speech_recognition as sr  # type: ignore
    except Exception:
        return ""

    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.3)
            audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
    except Exception:
        return ""

    # Try Google (online); if it fails, return empty string
    try:
        return r.recognize_google(audio, language=lang)
    except Exception:
        return ""

