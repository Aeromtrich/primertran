from __future__ import annotations

import os
import time
from collections.abc import Iterable
from getpass import getpass
from pathlib import Path
from textwrap import shorten

from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import HSplit, Layout, Window
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.dimension import Dimension
from prompt_toolkit.layout.processors import Processor, Transformation, TransformationInput
from prompt_toolkit.styles import Style
from prompt_toolkit.utils import get_cwidth
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.text import Text

from primertran.agent import MAX_INPUT_LENGTH, TranslationInputError, TranslatorAgent
from primertran.config import (
    CONFIG_PATH,
    AppConfig,
    load_config,
    mask_api_key,
    reset_config,
    save_config,
    SUPPORTED_MODELS,
    SUPPORTED_PROVIDERS,
    SUPPORTED_STYLES,
)
from primertran.providers import ProviderError

console = Console()
LONG_INPUT_PREVIEW = 180
LONG_INPUT_THRESHOLD = 500
MIN_INPUT_RULE_WIDTH = 40
INPUT_PROMPT = "› "
INPUT_SUMMARY_SUFFIX = "c"
INPUT_FRAME_HEIGHT = 4
OUTPUT_RULE_WIDTH = 28
BANNER_WIDTH = 72
DOG_MASCOT = (
    r" / \__",
    r"(    @\___",
    r" /         O",
    r"/   (_____/",
    r"/_____/   U",
)

BANNER_TITLE = "PrimerTran"
BANNER_SUBTITLE = "English -> Chinese Agent"


class CompactInputDisplayProcessor(Processor):
    def apply_transformation(self, ti: TransformationInput) -> Transformation:
        summary = summarize_input_display(ti.document.text)
        if summary is None:
            return Transformation(ti.fragments)

        fragments = [("class:input", summary)]
        summary_length = len(summary)
        source_length = len(ti.document.text)

        def source_to_display(position: int) -> int:
            if source_length == 0:
                return 0
            if position >= source_length:
                return summary_length
            return min(summary_length, position)

        def display_to_source(position: int) -> int:
            if summary_length == 0:
                return 0
            if position >= summary_length:
                return source_length
            return min(source_length, position)

        return Transformation(
            fragments,
            source_to_display=source_to_display,
            display_to_source=display_to_source,
        )


def run_repl() -> None:
    config = load_config()
    show_banner(config)

    if not config.has_api_key:
        configure_first_run(config)

    session = PromptSession(multiline=False, wrap_lines=False)
    while True:
        try:
            raw = prompt_with_frame(config)
        except (EOFError, KeyboardInterrupt):
            console.print("\n已退出 PrimerTran。")
            return

        text = raw.strip()
        if not text:
            continue
        if text.startswith("/"):
            should_continue = handle_command(text, config, session)
            if not should_continue:
                return
            continue

        text = prepare_input(text)
        if text:
            translate_and_print(config, text)


def show_banner(config: AppConfig, *, compact: bool = False) -> None:
    if compact:
        console.print(build_banner(config))
        console.print()
        return
    console.print(build_banner(config))
    console.print()


def build_banner(config: AppConfig) -> Panel:
    right_lines = [
        BANNER_TITLE,
        BANNER_SUBTITLE,
        f"model  {config.model}",
        f"style  {config.style}",
        "paste long text · Enter send",
        "Esc Esc clear · /help",
    ]

    body = Text()
    rows = max(len(DOG_MASCOT), len(right_lines))
    for index in range(rows):
        if index:
            body.append("\n")
        mascot = DOG_MASCOT[index] if index < len(DOG_MASCOT) else ""
        detail = right_lines[index] if index < len(right_lines) else ""
        body.append(f"{mascot:<14}", style="cyan")
        body.append("  ")
        style = "bold cyan" if index == 0 else "blue"
        if index >= 2:
            style = "magenta"
        body.append(detail, style=style)

    return Panel(
        body,
        border_style="red",
        padding=(0, 1),
        width=min(BANNER_WIDTH, max(console.width, MIN_INPUT_RULE_WIDTH)),
    )


def input_rule_width() -> int:
    return max(MIN_INPUT_RULE_WIDTH, console.width - 1)


def input_visible_width() -> int:
    return max(1, input_rule_width() - get_cwidth(INPUT_PROMPT))


def input_rule() -> str:
    return "─" * input_rule_width()


def input_bottom_rule() -> str:
    return input_rule()


def prompt_with_frame(config: AppConfig) -> str:
    buffer = Buffer()
    bindings = KeyBindings()

    @bindings.add("enter")
    def _(event) -> None:
        event.app.exit(result=buffer.text)

    @bindings.add("c-c")
    def _(event) -> None:
        raise KeyboardInterrupt

    @bindings.add("c-d")
    def _(event) -> None:
        if not buffer.text:
            raise EOFError

    @bindings.add("escape", "escape")
    def _(event) -> None:
        buffer.reset()

    input_control = BufferControl(
        buffer=buffer,
        input_processors=[CompactInputDisplayProcessor()],
    )
    layout = Layout(
        HSplit(
            [
                Window(
                    content=FormattedTextControl([("class:line", input_rule())]),
                    height=Dimension.exact(1),
                    dont_extend_height=True,
                ),
                Window(
                    content=input_control,
                    height=Dimension.exact(1),
                    dont_extend_height=True,
                    wrap_lines=False,
                    get_line_prefix=lambda line_number, wrap_count: [("class:prompt", INPUT_PROMPT)],
                ),
                Window(
                    content=FormattedTextControl([("class:line", input_bottom_rule())]),
                    height=Dimension.exact(1),
                    dont_extend_height=True,
                ),
                Window(
                    content=FormattedTextControl(prompt_rprompt(config)),
                    height=Dimension.exact(1),
                    dont_extend_height=True,
                    style="class:meta",
                ),
            ]
        ),
        focused_element=input_control,
    )
    style = Style.from_dict(
        {
            "line": "ansiblack",
            "prompt": "ansicyan bold",
            "input": "ansimagenta bold",
            "meta": "ansiblue",
        }
    )
    app = Application(
        layout=layout,
        key_bindings=bindings,
        full_screen=False,
        mouse_support=False,
        style=style,
        erase_when_done=True,
    )
    return app.run()


def summarize_input_display(text: str) -> str | None:
    if not text:
        return None
    if "\n" in text or len(text) >= LONG_INPUT_THRESHOLD or exceeds_input_line(text):
        return f"{len(text)}{INPUT_SUMMARY_SUFFIX}"
    return None


def exceeds_input_line(text: str, max_width: int | None = None) -> bool:
    width = input_visible_width() if max_width is None else max_width
    return any(get_cwidth(line) > width for line in text.splitlines() or [text])


def configure_first_run(config: AppConfig) -> None:
    console.print("[yellow]未检测到 DeepSeek API Key。[/yellow]\n")
    console.print("PrimerTran 当前使用 DeepSeek。")
    config.api_key = getpass("请输入 DeepSeek API Key: ").strip()
    config.provider = "deepseek"
    config.base_url = "https://api.deepseek.com"
    config.model = choose_option("请选择默认模型：", SUPPORTED_MODELS, config.model)
    config.style = "explain"
    save_config(config)
    console.print("[green]配置完成，开始翻译。[/green]\n")


def handle_command(command: str, config: AppConfig, session: PromptSession) -> bool:
    name = command.split(maxsplit=1)[0].lower()
    if name in {"/exit", "/quit"}:
        console.print("已退出 PrimerTran。")
        return False
    if name == "/help":
        show_help()
    elif name == "/clear":
        reset_session(config)
    elif name == "/key":
        update_key(config)
    elif name == "/provider":
        update_provider(config)
    elif name == "/model":
        update_model(config)
    elif name == "/style":
        update_style(config)
    elif name == "/config":
        show_config(config)
    elif name == "/reset":
        do_reset(config)
    elif name == "/multi":
        text = read_multiline(session)
        if text.strip():
            translate_and_print(config, text)
    else:
        console.print("[yellow]未知命令。输入 /help 查看可用命令。[/yellow]")
    return True


def show_help() -> None:
    commands = [
        ("/help", "show commands"),
        ("/clear", "start a fresh session"),
        ("/key", "update API key"),
        ("/provider", "switch provider"),
        ("/model", "switch model"),
        ("/style", "switch output style"),
        ("/config", "show config"),
        ("/reset", "reset local config"),
        ("/multi", "multi-line input, finish with /end"),
        ("/exit", "quit"),
    ]

    console.print()
    console.print(Text("commands", style="magenta"))
    for command, description in commands:
        line = Text()
        line.append(f"{command:<10}", style="cyan")
        line.append(description, style="blue")
        console.print(line)
    console.print(Text("Enter send · Esc Esc clear · long input folds to character count", style="magenta"))


def reset_session(config: AppConfig) -> None:
    clear_terminal()
    show_banner(config)


def clear_terminal() -> None:
    os.system(clear_terminal_command())


def clear_terminal_command() -> str:
    return "cls" if os.name == "nt" else "clear"


def update_key(config: AppConfig) -> None:
    value = getpass("请输入 DeepSeek API Key: ").strip()
    if not value:
        console.print("[yellow]API Key 未更新。[/yellow]")
        return
    config.api_key = value
    save_config(config)
    console.print("[green]API Key 已更新。[/green]")


def update_provider(config: AppConfig) -> None:
    console.print(f"当前 provider: [bold]{config.provider}[/bold]")
    chosen = choose_option("请选择 provider：", SUPPORTED_PROVIDERS, config.provider)
    config.provider = chosen
    save_config(config)
    console.print("[green]Provider 已更新。[/green]")


def update_model(config: AppConfig) -> None:
    console.print(f"当前模型: [bold]{config.model}[/bold]")
    config.model = choose_option("请选择模型：", SUPPORTED_MODELS, config.model)
    save_config(config)
    console.print("[green]模型已更新。[/green]")


def update_style(config: AppConfig) -> None:
    console.print(f"当前风格: [bold]{config.style}[/bold]")
    config.style = choose_option("请选择输出风格：", SUPPORTED_STYLES, config.style)
    save_config(config)
    console.print("[green]输出风格已更新。[/green]")


def show_config(config: AppConfig) -> None:
    console.print(f"配置文件  {CONFIG_PATH}")
    console.print(f"Provider  {config.provider}")
    console.print(f"Base URL  {config.base_url}")
    console.print(f"Model     {config.model}")
    console.print(f"Style     {config.style}")
    console.print(f"Language  {config.language}")
    console.print(f"API Key   {mask_api_key(config.api_key)}")


def do_reset(config: AppConfig) -> None:
    if not Confirm.ask("确认重置本地配置？", default=False):
        console.print("[yellow]已取消。[/yellow]")
        return
    reset_config()
    fresh = AppConfig()
    config.provider = fresh.provider
    config.api_key = fresh.api_key
    config.base_url = fresh.base_url
    config.model = fresh.model
    config.style = fresh.style
    config.language = fresh.language
    console.print("[green]配置已重置。[/green]")


def read_multiline(session: PromptSession) -> str:
    console.print("粘贴多行英文内容，输入 /end 结束。")
    lines: list[str] = []
    while True:
        try:
            line = session.prompt("... ")
        except (EOFError, KeyboardInterrupt):
            console.print("\n[yellow]多行输入已取消。[/yellow]")
            return ""
        if line.strip() == "/end":
            return "\n".join(lines)
        lines.append(line)


def prepare_input(text: str) -> str:
    if len(text) > MAX_INPUT_LENGTH:
        console.print(f"[yellow]输入超过 {MAX_INPUT_LENGTH} 字符，请拆分后再翻译。[/yellow]")
        return ""
    print_submitted_input(text)
    return text


def print_submitted_input(text: str) -> None:
    console.print()
    console.print(Text(f"input · {len(text)}c", style="magenta"))
    for index, line in enumerate(text.splitlines() or [text]):
        prefix = "› " if index == 0 else "  "
        console.print(Text(f"{prefix}{line}", style="cyan"))


def is_long_or_multiline(text: str) -> bool:
    return "\n" in text or len(text) >= LONG_INPUT_THRESHOLD


def compact_preview(text: str) -> str:
    normalized = " ".join(part.strip() for part in text.splitlines() if part.strip())
    return shorten(normalized, width=LONG_INPUT_PREVIEW, placeholder=" ...")


def translate_and_print(config: AppConfig, text: str) -> None:
    if not config.has_api_key:
        console.print("[yellow]未配置 API Key，请先使用 /key 设置。[/yellow]")
        return

    agent = TranslatorAgent(config)
    started_at = time.perf_counter()
    try:
        console.print(Text(f"translating · {config.model}", style="magenta"))
        output = print_translation_stream(agent.translate_stream(text))
    except TranslationInputError as exc:
        console.print(f"[yellow]{exc}[/yellow]")
    except ProviderError as exc:
        console.print(f"[red]{exc}[/red]")
    else:
        if output:
            console.print()
        console.print(Text(f"done · {format_elapsed(time.perf_counter() - started_at)}", style="magenta"))
        console.print()


def prompt_rprompt(config: AppConfig) -> HTML:
    cwd = shorten_path(Path.cwd())
    return HTML(
        f"<style fg='ansibrightblack'>{config.model}</style>"
        f"<style fg='ansibrightblack'> · </style>"
        f"<style fg='ansibrightblack'>{cwd}</style>"
        f"<style fg='ansibrightblack'> · </style>"
        f"<style fg='ansibrightblack'>{config.style}</style>"
        f"<style fg='ansibrightblack'> · </style>"
        f"<style fg='ansiblue'>Enter send · Esc Esc clear</style>"
    )


def format_elapsed(seconds: float) -> str:
    if seconds < 10:
        return f"{seconds:.1f}s"
    return f"{seconds:.0f}s"


def print_translation_output(output: str) -> None:
    renderer = TranslationOutputRenderer()
    for line in output.splitlines():
        renderer.print_line(line)


def print_translation_stream(chunks: Iterable[str]) -> str:
    renderer = TranslationOutputRenderer()
    pending = ""
    output_parts: list[str] = []

    for chunk in chunks:
        if not chunk:
            continue
        output_parts.append(chunk)
        pending += chunk
        while "\n" in pending:
            line, pending = pending.split("\n", 1)
            renderer.print_line(line)

    if pending:
        renderer.print_line(pending)
    return "".join(output_parts)


class TranslationOutputRenderer:
    def __init__(self) -> None:
        self.seen_content = False

    def print_line(self, line: str) -> None:
        if is_source_label(line) and self.seen_content:
            console.print(Text("─" * OUTPUT_RULE_WIDTH, style="blue"))
        console.print(format_translation_line(line))
        if line.strip():
            self.seen_content = True


def format_translation_line(line: str) -> Text:
    stripped = line.strip()
    text = Text(line)
    if not stripped:
        return text
    if is_source_label(line):
        text.stylize("bold cyan")
    elif stripped in {"翻译：", "翻译:"} or stripped.startswith(("翻译：", "翻译:")):
        text.stylize("bold green")
    elif stripped in {"解释：", "解释:", "技术解释：", "技术解释:"} or stripped.startswith(
        ("解释：", "解释:", "技术解释：", "技术解释:")
    ):
        text.stylize("bold yellow")
    elif stripped.startswith(("- ", "* ")):
        text.stylize("magenta")
        text.stylize("yellow", 0, min(len(line), len(line) - len(line.lstrip()) + 1))
    else:
        text.stylize("blue")
    return text


def is_source_label(line: str) -> bool:
    stripped = line.strip()
    return stripped in {"原句：", "原句:"} or stripped.startswith(("原句：", "原句:"))


def shorten_path(path: Path, max_length: int = 56) -> str:
    text = str(path)
    if len(text) <= max_length:
        return text
    home = str(Path.home())
    if text.startswith(home):
        text = "~" + text[len(home) :]
    if len(text) <= max_length:
        return text
    return "..." + text[-(max_length - 3) :]


def choose_option(title: str, options: tuple[str, ...], current: str) -> str:
    console.print(title)
    for index, option in enumerate(options, start=1):
        marker = " 当前" if option == current else ""
        console.print(f"{index}. {option}{marker}")

    while True:
        value = Prompt.ask("请输入序号", default=str(options.index(current) + 1 if current in options else 1))
        try:
            index = int(value)
        except ValueError:
            console.print("[yellow]请输入有效序号。[/yellow]")
            continue
        if 1 <= index <= len(options):
            return options[index - 1]
        console.print("[yellow]请输入有效序号。[/yellow]")
