from __future__ import annotations

import argparse
from typing import List

from src.lib.prompt_builder import build_prompt
from src.lib.speech import speak, chime
from src.lib.eyesfree import parse_command
from src.lib.stt import transcribe_once, has_speech_recognition
from src.lib.session import run_session, SessionConfig


def runInteractive(say: bool = False, voice: str | None = None, rate: int | None = None, do_chime: bool = True, guide: bool = False, eyesfree: bool = False, save_path: str | None = None) -> None:
    print("xxx CLI — simple prompt builder")
    print("Type lines; blank line to finish.\n")
    if guide or eyesfree:
        speak("Interactive mode. Type your text. Press return on an empty line to finish.", voice=voice, rate=rate, enabled=say)
        chime(enabled=do_chime)
    lines: List[str] = []
    while True:
        try:
            line = input("> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line.strip():
            if eyesfree:
                speak("Use slash commands. Say slash done to finish.", voice=voice, rate=rate, enabled=say)
                continue
            break

        is_cmd, cmd = parse_command(line)
        if is_cmd and cmd:
            if cmd.name == "undo":
                if lines:
                    lines.pop()
                    speak("Undone.", voice=voice, rate=rate, enabled=say)
                else:
                    speak("Nothing to undo.", voice=voice, rate=rate, enabled=say)
                if do_chime:
                    chime(sound="Pop")
                continue
            if cmd.name == "read":
                text = "\n".join(lines)
                speak(text or "Nothing yet.", voice=voice, rate=rate, enabled=say)
                if do_chime:
                    chime()
                continue
            if cmd.name == "done":
                break
            if cmd.name == "help":
                help_text = "Commands: /undo, /read, /done, /save <path>."
                print(help_text)
                speak(help_text, voice=voice, rate=rate, enabled=say)
                continue
            if cmd.name == "save":
                path = cmd.arg
                if not path:
                    speak("Please provide a path.", voice=voice, rate=rate, enabled=say)
                else:
                    try:
                        with open(path, "w", encoding="utf-8") as f:
                            f.write("\n".join(lines))
                        speak("Saved.", voice=voice, rate=rate, enabled=say)
                    except Exception:
                        speak("Save failed.", voice=voice, rate=rate, enabled=say)
                if do_chime:
                    chime(sound="Submarine")
                continue

        lines.append(line)
        if do_chime:
            chime()

    prompt = build_prompt("chat", {"lines": lines})
    print("\n--- Prompt ---")
    print(prompt)
    speak("Prompt ready.", voice=voice, rate=rate, enabled=say)
    if say:
        speak(prompt, voice=voice, rate=rate, enabled=True)
    if save_path:
        try:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(prompt)
            speak("Saved.", voice=voice, rate=rate, enabled=say)
        except Exception:
            speak("Save failed.", voice=voice, rate=rate, enabled=say)


def main() -> None:
    parser = argparse.ArgumentParser(description="xxx CLI entry point")
    parser.add_argument(
        "mode",
        choices=["chat", "diary", "music", "image"],
        nargs="?",
        default="chat",
        help="Prompt type to build",
    )
    parser.add_argument("text", nargs=argparse.REMAINDER, help="Optional free text to seed")
    parser.add_argument("--speak", action="store_true", help="Read outputs aloud (macOS `say`)")
    parser.add_argument("--voice", help="Voice name for TTS (macOS)")
    parser.add_argument("--rate", type=int, help="Speech rate for TTS (words per minute)")
    parser.add_argument("--no-chime", dest="chime", action="store_false", help="Disable audio cues")
    parser.add_argument("--guide", action="store_true", help="Voice guidance in interactive mode")
    parser.add_argument("--eyesfree", action="store_true", help="Eyes-free mode: use /done to finish and voice cues")
    parser.add_argument("--save", help="Save the generated prompt to a file")
    parser.add_argument("--voicechat", action="store_true", help="Voice input per turn (mic → STT)")
    parser.add_argument("--lang", default="ja-JP", help="STT language (e.g., ja-JP, en-US)")
    parser.add_argument("--session-mins", type=int, help="Run a timed session for N minutes (e.g., 15)")
    parser.add_argument("--interval-sec", type=int, default=60, help="Prompt interval seconds during session")
    parser.set_defaults(chime=True)
    args = parser.parse_args()

    # Timed session mode takes precedence for chat
    if args.session_mins and args.mode == "chat":
        cfg = SessionConfig(
            minutes=args.session_mins,
            interval_sec=args.interval_sec,
            lang=args.lang,
            use_voice=(args.speak or True),
            voice_name=args.voice,
            rate=args.rate,
            use_voice_input=args.voicechat,
            save_path=args.save,
        )
        lines = run_session(cfg)
        prompt = build_prompt("chat", {"lines": lines})
        print(prompt)
        if args.save:
            try:
                with open(args.save, "w", encoding="utf-8") as f:
                    f.write(prompt)
                speak("保存しました。", voice=args.voice, rate=args.rate, enabled=True)
            except Exception:
                speak("保存に失敗しました。", voice=args.voice, rate=args.rate, enabled=True)
        return

    if not args.text and args.mode == "chat" and not args.voicechat:
        runInteractive(
            say=args.speak or args.eyesfree,
            voice=args.voice,
            rate=args.rate,
            do_chime=args.chime or args.eyesfree,
            guide=args.guide or args.eyesfree,
            eyesfree=args.eyesfree,
            save_path=args.save,
        )
        return

    if args.voicechat and args.mode == "chat":
        if not has_speech_recognition():
            print("SpeechRecognition not installed. Install with: pip install SpeechRecognition pyaudio (or sounddevice)")
            return
        speak(
            "Voice chat. Say your line after the chime. Say slash done to finish.",
            voice=args.voice,
            rate=args.rate,
            enabled=args.speak or True,
        )
        lines: List[str] = []
        while True:
            chime()
            text = transcribe_once(lang=args.lang)
            if not text:
                speak("No speech detected.", voice=args.voice, rate=args.rate, enabled=args.speak or True)
                continue
            is_cmd, cmd = parse_command(text)
            if is_cmd and cmd:
                if cmd.name == "undo":
                    if lines:
                        lines.pop()
                        speak("Undone.", voice=args.voice, rate=args.rate, enabled=True)
                    else:
                        speak("Nothing to undo.", voice=args.voice, rate=args.rate, enabled=True)
                    continue
                if cmd.name == "read":
                    speak("\n".join(lines) or "Nothing yet.", voice=args.voice, rate=args.rate, enabled=True)
                    continue
                if cmd.name == "done":
                    break
                if cmd.name == "save":
                    path = (cmd.arg or args.save)
                    if path:
                        try:
                            with open(path, "w", encoding="utf-8") as f:
                                f.write("\n".join(lines))
                            speak("Saved.", voice=args.voice, rate=args.rate, enabled=True)
                        except Exception:
                            speak("Save failed.", voice=args.voice, rate=args.rate, enabled=True)
                    else:
                        speak("Provide a path.", voice=args.voice, rate=args.rate, enabled=True)
                    continue
            lines.append(text)
            speak(text, voice=args.voice, rate=args.rate, enabled=args.speak or True)

        prompt = build_prompt("chat", {"lines": lines})
        print(prompt)
        if args.save:
            try:
                with open(args.save, "w", encoding="utf-8") as f:
                    f.write(prompt)
                speak("Saved.", voice=args.voice, rate=args.rate, enabled=True)
            except Exception:
                speak("Save failed.", voice=args.voice, rate=args.rate, enabled=True)
        speak(prompt, voice=args.voice, rate=args.rate, enabled=args.speak or True)
        return

    seed = " ".join(args.text).strip()
    payload = {"seed": seed} if seed else {}
    prompt = build_prompt(args.mode, payload)
    print(prompt)
    if args.save:
        try:
            with open(args.save, "w", encoding="utf-8") as f:
                f.write(prompt)
            speak("Saved.", voice=args.voice, rate=args.rate, enabled=args.speak or args.eyesfree)
        except Exception:
            speak("Save failed.", voice=args.voice, rate=args.rate, enabled=args.speak or args.eyesfree)
    speak(prompt, voice=args.voice, rate=args.rate, enabled=args.speak or args.eyesfree)


if __name__ == "__main__":
    main()
