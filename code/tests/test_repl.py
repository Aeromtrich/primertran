from pathlib import Path

from primertran.config import AppConfig
from primertran.repl import (
    BANNER_SUBTITLE,
    build_banner,
    compact_preview,
    console,
    exceeds_input_line,
    format_translation_line,
    input_bottom_rule,
    is_source_label,
    is_long_or_multiline,
    print_translation_output,
    print_submitted_input,
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


def test_show_banner_prints_compact_panel() -> None:
    with console.capture() as capture:
        show_banner(AppConfig(model="deepseek-v4-flash", style="explain"))

    output = capture.get()
    assert "PrimerTran" in output
    assert BANNER_SUBTITLE in output
    assert "deepseek-v4-flash" in output
    assert "Style  explain" in output


def test_build_banner_contains_session_info() -> None:
    banner = build_banner(AppConfig(model="deepseek-v4-flash", style="explain"))

    with console.capture() as capture:
        console.print(banner)

    output = capture.get()
    assert "PrimerTran" in output
    assert "deepseek-v4-flash" in output
    assert "/help" in output
    assert "Esc Esc clear" in output


def test_input_bottom_rule_matches_prompt_rule() -> None:
    rule = input_bottom_rule()

    assert set(rule) == {"·"}


def test_summarize_input_display_for_short_text() -> None:
    assert summarize_input_display("hello") is None


def test_summarize_input_display_for_long_text() -> None:
    assert summarize_input_display("a" * 500) == "500c"


def test_summarize_input_display_for_text_exceeding_one_line() -> None:
    assert summarize_input_display("a" * 55) == "55c"


def test_summarize_input_display_for_multiline_text() -> None:
    assert summarize_input_display("hello\nworld") == "11c"


def test_exceeds_input_line() -> None:
    assert exceeds_input_line("a" * 55)
    assert not exceeds_input_line("short text")


def test_print_submitted_input_outputs_full_text() -> None:
    with console.capture() as capture:
        print_submitted_input("first line\nsecond line")

    output = capture.get()
    assert "input · 22c" in output
    assert "› first line" in output
    assert "  second line" in output


def test_format_translation_line_styles_template_labels() -> None:
    assert format_translation_line("原句：").spans[0].style == "bold cyan"
    assert format_translation_line("翻译：").spans[0].style == "bold green"
    assert format_translation_line("解释：").spans[0].style == "bold yellow"
    assert format_translation_line("技术解释：").spans[0].style == "bold yellow"


def test_is_source_label() -> None:
    assert is_source_label("原句：")
    assert is_source_label("原句：Hello")
    assert not is_source_label("翻译：")


def test_format_translation_line_avoids_white_styles() -> None:
    assert format_translation_line("translated body").spans[0].style == "blue"
    assert format_translation_line("- explanation").spans[0].style == "magenta"


def test_print_translation_output_keeps_text_visible() -> None:
    with console.capture() as capture:
        print_translation_output("原句：\nHello\n翻译：\n你好\n原句：\nWorld")

    output = capture.get()
    assert "原句：" in output
    assert "Hello" in output
    assert "翻译：" in output
    assert "你好" in output
    assert "World" in output
    assert "─" in output


def test_prompt_rprompt_contains_status_text() -> None:
    toolbar = prompt_rprompt(AppConfig(model="deepseek-v4-flash", style="explain"))
    rendered = toolbar.value if hasattr(toolbar, "value") else str(toolbar)

    assert "deepseek-v4-flash" in rendered
    assert "explain" in rendered
    assert "Esc Esc clear" in rendered
