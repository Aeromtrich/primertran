from pathlib import Path

from primertran.config import AppConfig
from primertran.repl import (
    BANNER,
    compact_preview,
    console,
    input_bottom_rule,
    is_long_or_multiline,
    prompt_rprompt,
    shorten_path,
    show_banner,
    summarize_input_display,
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


def test_input_bottom_rule_matches_horizontal_rule() -> None:
    rule = input_bottom_rule()

    assert set(rule) == {"─"}


def test_summarize_input_display_for_short_text() -> None:
    assert summarize_input_display("hello") is None


def test_summarize_input_display_for_long_text() -> None:
    assert summarize_input_display("a" * 500) == "500c"


def test_summarize_input_display_for_multiline_text() -> None:
    assert summarize_input_display("hello\nworld") == "11c"


def test_prompt_rprompt_contains_status_text() -> None:
    toolbar = prompt_rprompt(AppConfig(model="deepseek-v4-flash", style="explain"))
    rendered = toolbar.value if hasattr(toolbar, "value") else str(toolbar)

    assert "deepseek-v4-flash" in rendered
    assert "explain" in rendered
