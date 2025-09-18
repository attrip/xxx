# Architecture Notes

- CLI in `src/app/main.py` for interactive or one-shot prompt building.
- Core logic in `src/lib/prompt_builder.py` with a tiny API: `build_prompt(mode, data)`.
- HTML examples are static and load directly from local filesystem or via `make web`.
- Scripts include a minimal local web server to open examples.
- Tests mirror `src/` under `tests/` and can be run with `make test`.
