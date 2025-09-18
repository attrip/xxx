import os

from src.lib.speech import speak, chime, is_mac


def test_speak_dry_run_env(monkeypatch):
    monkeypatch.setenv("SPEECH_DRY_RUN", "1")
    assert speak("hello", enabled=True) is True


def test_chime_dry_run_env(monkeypatch):
    monkeypatch.setenv("SPEECH_DRY_RUN", "1")
    assert chime(enabled=True) is True


def test_speak_disabled():
    assert speak("hello", enabled=False) is False


def test_chime_disabled():
    assert chime(enabled=False) is False

