PYTHON ?= python3
export PYTHONPATH := .

.PHONY: run dev test fmt lint open-html web start export-html file-url open-v1 open-v2 open-dmi

run dev:
	$(PYTHON) -m src.app.main

test:
	pytest

fmt:
	black .

lint:
	ruff check .

open-html:
	@echo "Opening examples/psytrance_prompt_editor.html..."
	@([ "$(shell uname)" = "Darwin" ] && open examples/psytrance_prompt_editor.html) || (which xdg-open >/dev/null 2>&1 && xdg-open examples/psytrance_prompt_editor.html) || echo "Open the file manually: examples/psytrance_prompt_editor.html"

web:
	$(PYTHON) scripts/serve_web.py

start: export-html web

export-html:
	@mkdir -p dist
	@cp -R examples dist/
	@mkdir -p dist/picture_diary
	@cp -R picture_diary/src dist/picture_diary/
	@mkdir -p dist/picture_diary/v2
	@cp -R picture_diary/v2 dist/picture_diary/
	@echo "Exported to dist/"

file-url:
	@ABS_PATH=$$(cd dist && pwd); echo "file://$$ABS_PATH/examples/psytrance_prompt_editor.html"

open-v1:
	@([ "$(shell uname)" = "Darwin" ] && open picture_diary/src/index.html) || (which xdg-open >/dev/null 2>&1 && xdg-open picture_diary/src/index.html) || echo "Open: picture_diary/src/index.html"

open-v2:
	@([ "$(shell uname)" = "Darwin" ] && open picture_diary/v2/index.html) || (which xdg-open >/dev/null 2>&1 && xdg-open picture_diary/v2/index.html) || echo "Open: picture_diary/v2/index.html"

open-dmi:
	@([ "$(shell uname)" = "Darwin" ] && open examples/diary_music_image.html) || (which xdg-open >/dev/null 2>&1 && xdg-open examples/diary_music_image.html) || echo "Open: examples/diary_music_image.html"

open-partner:
	@([ "$(shell uname)" = "Darwin" ] && open examples/partner_voice_site.html) || (which xdg-open >/dev/null 2>&1 && xdg-open examples/partner_voice_site.html) || echo "Open: examples/partner_voice_site.html"

open-dev-agent:
	@echo "Tip: API needs localhost. Prefer: make web-dev-agent"
	@([ "$(shell uname)" = "Darwin" ] && open examples/dev_agent.html) || (which xdg-open >/dev/null 2>&1 && xdg-open examples/dev_agent.html) || echo "Open: examples/dev_agent.html"

web-dev-agent:
	OPEN_PATH=/examples/dev_agent.html $(PYTHON) scripts/serve_web.py

web-workbench:
	OPEN_PATH=/workbench/index.html $(PYTHON) scripts/serve_web.py

open-dev-remote:
	@([ "$(shell uname)" = "Darwin" ] && open examples/dev_agent_remote.html) || (which xdg-open >/dev/null 2>&1 && xdg-open examples/dev_agent_remote.html) || echo "Open: examples/dev_agent_remote.html"

web-simple-html:
	OPEN_PATH=/projects/simple_html/index.html $(PYTHON) scripts/serve_web.py
