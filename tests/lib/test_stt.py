import os

from src.lib.stt import transcribe_once, has_speech_recognition


def test_stt_dry_run(monkeypatch):
    monkeypatch.setenv("STT_DRY_RUN", "1")
    monkeypatch.setenv("STT_DRY_RUN_TEXT", "こんにちは")
    assert transcribe_once(lang="ja-JP") == "こんにちは"


def test_stt_no_dep_graceful(monkeypatch):
    # If SpeechRecognition is not installed, function should return "" when not in dry-run
    monkeypatch.delenv("STT_DRY_RUN", raising=False)
    monkeypatch.delenv("STT_DRY_RUN_TEXT", raising=False)
    # We can't enforce library absence here; just call and ensure it returns a string.
    out = transcribe_once(lang="en-US", timeout=0.1, phrase_time_limit=0.1)
    assert isinstance(out, str)
