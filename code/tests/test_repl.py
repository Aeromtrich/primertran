from pathlib import Path

from primertran.repl import compact_preview, is_long_or_multiline, shorten_path


def test_long_or_multiline_detection() -> None:
    assert is_long_or_multiline("hello\nworld")
    assert is_long_or_multiline("a" * 500)
    assert not is_long_or_multiline("short text")


def test_compact_preview_removes_line_breaks() -> None:
    preview = compact_preview("first line\n\nsecond line")

    assert preview == "first line second line"


def test_shorten_path_keeps_short_path() -> None:
    assert shorten_path(Path("/tmp/project"), max_length=20) == "/tmp/project"
