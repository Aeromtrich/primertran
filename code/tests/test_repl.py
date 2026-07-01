from pathlib import Path

from primertran.config import AppConfig
from primertran.repl import (
    BANNER,
    compact_preview,
    console,
    input_prompt,
    is_long_or_multiline,
    shorten_path,
    show_banner,
)


def test_long_or_multiline_detection() -> None:
    assert is_long_or_multiline("hello\nworld")
    assert is_long_or_multiline("a" * 500)
    assert not is_long_or_multiline("short text")


def test_compact_preview_removes_line_breaks() -> None:
    preview = compact_preview("first line\n\nsecond line")

    assert preview == "first line second line"


def test_shorten_path_keeps_short_path() -> None:
    assert shorten_path(Path("/tmp/project"), max_length=20) == "/tmp/project"


def test_show_banner_prints_full_logo() -> None:
    with console.capture() as capture:
        show_banner(AppConfig(model="deepseek-v4-flash", style="explain"))

    output = capture.get()
    assert BANNER.splitlines()[0] in output
    assert "PrimerTran" in output
    assert "Model  deepseek-v4-flash" in output
    assert "Style  explain" in output


def test_input_prompt_starts_with_rule_and_prompt_marker() -> None:
    prompt = input_prompt()

    assert prompt[0][0] == "class:line"
    assert prompt[0][1].endswith("\n")
    assert set(prompt[0][1].strip()) == {"─"}
    assert prompt[1] == ("class:prompt", "› ")
