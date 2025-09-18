from __future__ import annotations

from typing import Dict, List


def _join_lines(lines: List[str]) -> str:
    return "\n".join(s.strip() for s in lines if s is not None)


def build_prompt(mode: str, data: Dict) -> str:
    """Build a simple text prompt for different modes.

    - chat: join lines or seed
    - diary: format diary entry
    - music: format music request
    - image: format image description
    """
    mode = (mode or "").lower().strip()
    seed = str(data.get("seed", "")).strip() if data else ""

    if mode == "chat":
        lines = data.get("lines", []) if data else []
        if lines:
            return _join_lines(lines)
        return seed

    if mode == "diary":
        title = (data.get("title") or "Untitled").strip() if data else "Untitled"
        body = data.get("body") or seed or ""
        return f"[Diary]\nTitle: {title}\n{body}".strip()

    if mode == "music":
        genre = (data.get("genre") or "ambient").strip() if data else "ambient"
        bpm = data.get("bpm")
        bpm_part = f" @ {bpm} BPM" if bpm else ""
        mood = (data.get("mood") or seed or "calm").strip()
        return f"Music: {genre}{bpm_part}\nMood: {mood}".strip()

    if mode == "image":
        subject = (data.get("subject") or seed or "a scene").strip()
        style = (data.get("style") or "photorealistic").strip()
        return f"Image: {subject}\nStyle: {style}".strip()

    # Fallback
    return seed
