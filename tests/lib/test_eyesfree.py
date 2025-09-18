from src.lib.eyesfree import parse_command, Command


def test_parse_regular_line():
    is_cmd, cmd = parse_command("hello")
    assert is_cmd is False
    assert cmd is None


def test_parse_basic_commands():
    for name in ["/undo", "/read", "/done", "/help"]:
        is_cmd, cmd = parse_command(name)
        assert is_cmd is True
        assert cmd and cmd.name == name[1:]


def test_parse_save_with_arg():
    is_cmd, cmd = parse_command("/save out.txt")
    assert is_cmd is True
    assert cmd and cmd.name == "save" and cmd.arg == "out.txt"
