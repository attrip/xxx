from __future__ import annotations

import argparse
from typing import List

from src.lib.prompt_builder import build_prompt


def runInteractive() -> None:
    print("xxx CLI — simple prompt builder")
    print("Type lines; blank line to finish.\n")
    lines: List[str] = []
    while True:
        try:
            line = input("> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line.strip():
            break
        lines.append(line)

    prompt = build_prompt("chat", {"lines": lines})
    print("\n--- Prompt ---")
    print(prompt)


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
    args = parser.parse_args()

    if not args.text and args.mode == "chat":
        runInteractive()
        return

    seed = " ".join(args.text).strip()
    payload = {"seed": seed} if seed else {}
    prompt = build_prompt(args.mode, payload)
    print(prompt)


if __name__ == "__main__":
    main()
