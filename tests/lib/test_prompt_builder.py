from src.lib.prompt_builder import build_prompt


def test_chat_seed_only():
    assert build_prompt("chat", {"seed": "hello"}) == "hello"


def test_chat_lines_join():
    assert build_prompt("chat", {"lines": ["hello", "world"]}) == "hello\nworld"


def test_diary():
    out = build_prompt("diary", {"title": "My Day", "body": "It was fine."})
    assert out.startswith("[Diary]\nTitle: My Day")
    assert "It was fine." in out


def test_music():
    out = build_prompt("music", {"genre": "psytrance", "bpm": 145, "mood": "hypnotic"})
    assert "Music: psytrance @ 145 BPM" in out
    assert "Mood: hypnotic" in out


def test_image():
    out = build_prompt("image", {"subject": "cat", "style": "cartoon"})
    assert out == "Image: cat\nStyle: cartoon"
