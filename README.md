# xxx

A starter Python project scaffolded for CLI + simple HTML examples, following the provided repository guidelines.

## Quick start
- make run — run the CLI locally
- make test — run pytest
- make fmt && make lint — format and lint
- make web — serve examples locally and open in browser
- make export-html — export examples to dist/

## Structure
- src/app: CLI entry (main.py)
- src/lib: Core logic (prompt_builder.py)
- src/lib/speech.py: Minimal TTS/chime utilities for accessibility
 - src/lib/eyesfree.py: Slash-command parser for eyes-free mode
- examples/: Single-file HTML apps
- picture_diary/: Fixed local URLs (v1 and v2)
- scripts/: Helper scripts
- tests/: Pytest suites mirroring src/
- docs/: Architecture/design notes

## Accessibility / Eyes-closed mode
- One-shot reading: `make run -- --speak` (macOS `say`)
- Eyes-free interactive: `make run -- --eyesfree`
  - Use commands: `/undo`, `/read`, `/done`, `/save <path>`
  - Chimes after each line; help reads commands
- Choose voice/rate: `--voice Alex --rate 190`
- Audio cues: enabled by default; disable with `--no-chime`
- Save output: `--save out.txt` (also available via `/save out.txt` in interactive)
