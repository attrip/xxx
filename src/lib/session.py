from __future__ import annotations

import time
from dataclasses import dataclass
from typing import List, Optional

from src.lib.eyesfree import parse_command
from src.lib.speech import speak, chime
from src.lib.stt import transcribe_once, has_speech_recognition


@dataclass
class SessionConfig:
    minutes: int = 15
    interval_sec: int = 60
    lang: str = "ja-JP"
    use_voice: bool = True
    voice_name: Optional[str] = None
    rate: Optional[int] = None
    use_voice_input: bool = False
    save_path: Optional[str] = None


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S")


def run_session(cfg: SessionConfig) -> List[str]:
    """Run a time‑boxed session returning the captured lines.

    Accepts voice (STT) and typed input. Supports commands:
    /pause /resume /skip /read /undo /save <path> /done
    """
    lines: List[str] = []
    start = time.monotonic()
    end_at = start + max(1, cfg.minutes) * 60
    next_mark = start
    paused = False

    speak("セッションを開始します。準備ができたら呼吸に注意を向けてください。", voice=cfg.voice_name, rate=cfg.rate, enabled=cfg.use_voice)
    chime()

    def capture_turn() -> Optional[str]:
        if cfg.use_voice_input and has_speech_recognition():
            return transcribe_once(lang=cfg.lang)
        try:
            return input("> ")
        except (EOFError, KeyboardInterrupt):
            return "/done"

    while time.monotonic() < end_at:
        now = time.monotonic()
        if not paused and now >= next_mark:
            # Gentle prompt at each interval
            chime()
            speak("そのまま、いま気づいていることをどうぞ。必要ならスラッシュ・ドーンで終了です。", voice=cfg.voice_name, rate=cfg.rate, enabled=cfg.use_voice)
            next_mark = now + cfg.interval_sec

        text = capture_turn()
        if text is None:
            continue
        if not text.strip():
            # ignore empty in session
            continue

        is_cmd, cmd = parse_command(text)
        if is_cmd and cmd:
            name = cmd.name
            if name == "pause":
                paused = True
                speak("一時停止します。再開はスラッシュ・リジューム。", voice=cfg.voice_name, rate=cfg.rate, enabled=cfg.use_voice)
                continue
            if name == "resume":
                paused = False
                next_mark = time.monotonic()  # prompt soon after resume
                speak("再開します。", voice=cfg.voice_name, rate=cfg.rate, enabled=cfg.use_voice)
                continue
            if name == "skip":
                next_mark = time.monotonic()  # trigger next prompt
                chime()
                continue
            if name == "read":
                speak("\n".join(lines) or "まだ何もありません。", voice=cfg.voice_name, rate=cfg.rate, enabled=cfg.use_voice)
                continue
            if name == "undo":
                if lines:
                    lines.pop()
                    speak("取り消しました。", voice=cfg.voice_name, rate=cfg.rate, enabled=cfg.use_voice)
                else:
                    speak("取り消すものはありません。", voice=cfg.voice_name, rate=cfg.rate, enabled=cfg.use_voice)
                continue
            if name == "save":
                path = cmd.arg or cfg.save_path
                if path:
                    try:
                        with open(path, "w", encoding="utf-8") as f:
                            f.write("\n".join(lines))
                        speak("保存しました。", voice=cfg.voice_name, rate=cfg.rate, enabled=cfg.use_voice)
                    except Exception:
                        speak("保存に失敗しました。", voice=cfg.voice_name, rate=cfg.rate, enabled=cfg.use_voice)
                else:
                    speak("保存先を指定してください。", voice=cfg.voice_name, rate=cfg.rate, enabled=cfg.use_voice)
                continue
            if name == "done":
                break
            # Unknown -> help
            speak("使えるコマンドは、ポーズ、リジューム、スキップ、リード、アンドゥ、セーブ、ドーンです。", voice=cfg.voice_name, rate=cfg.rate, enabled=cfg.use_voice)
            continue

        # Regular content line with timestamp
        stamped = f"[{_now_iso()}] {text}"
        lines.append(stamped)
        # Short confirm only in voice mode
        speak("受け取りました。", voice=cfg.voice_name, rate=cfg.rate, enabled=cfg.use_voice)

    chime()
    speak("セッションを終了します。おつかれさまでした。", voice=cfg.voice_name, rate=cfg.rate, enabled=cfg.use_voice)
    return lines

