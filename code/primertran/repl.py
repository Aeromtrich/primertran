from __future__ import annotations

import os
from getpass import getpass

from prompt_toolkit import PromptSession
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.text import Text

from primertran.agent import TranslationInputError, TranslatorAgent
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

BANNER = r"""
╭────────────────────────────────────────────────────────╮
│                                                        │
│   ██████╗ ██████╗ ██╗███╗   ███╗███████╗██████╗      │
│   ██╔══██╗██╔══██╗██║████╗ ████║██╔════╝██╔══██╗     │
│   ██████╔╝██████╔╝██║██╔████╔██║█████╗  ██████╔╝     │
│   ██╔═══╝ ██╔══██╗██║██║╚██╔╝██║██╔══╝  ██╔══██╗     │
│   ██║     ██║  ██║██║██║ ╚═╝ ██║███████╗██║  ██║     │
│   ╚═╝     ╚═╝  ╚═╝╚═╝╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝     │
│                                                        │
│                    PrimerTran                         │
│              English -> Chinese Agent                 │
│                                                        │
╰────────────────────────────────────────────────────────╯
""".strip("\n")


def run_repl() -> None:
    config = load_config()
    show_banner(config)

    if not config.has_api_key:
        configure_first_run(config)

    session = PromptSession()
    while True:
        try:
            raw = session.prompt("en> ")
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

        translate_and_print(config, text)


def show_banner(config: AppConfig) -> None:
    console.print(Text(BANNER, style="bold cyan"))
    console.print()
    console.print(f"[bold]Model[/bold]  {config.model}")
    console.print(f"[bold]Style[/bold]  {config.style}")
    console.print("[bold]Type[/bold]   /help for commands")
    console.print()


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
        os.system("cls" if os.name == "nt" else "clear")
        show_banner(config)
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
    help_text = """\
/help      查看帮助和可用命令
/exit      退出 PrimerTran
/quit      退出 PrimerTran
/clear     清屏，并重新显示 Banner
/key       设置或更新当前 provider 的 API Key
/provider  查看或切换模型服务商
/model     查看或切换当前模型
/style     切换输出风格
/config    查看当前配置摘要
/reset     重置本地配置
/multi     粘贴多行英文内容，使用 /end 结束
"""
    console.print(Panel(help_text, title="PrimerTran Commands", border_style="cyan"))


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


def translate_and_print(config: AppConfig, text: str) -> None:
    if not config.has_api_key:
        console.print("[yellow]未配置 API Key，请先使用 /key 设置。[/yellow]")
        return

    agent = TranslatorAgent(config)
    try:
        with console.status("正在翻译...", spinner="dots"):
            output = agent.translate(text)
    except TranslationInputError as exc:
        console.print(f"[yellow]{exc}[/yellow]")
    except ProviderError as exc:
        console.print(f"[red]{exc}[/red]")
    else:
        console.print()
        console.print(output)
        console.print()


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
