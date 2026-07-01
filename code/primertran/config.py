from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import tomlkit

CONFIG_DIR = Path.home() / ".primertran"
CONFIG_PATH = CONFIG_DIR / "config.toml"

DEFAULT_PROVIDER = "deepseek"
DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-v4-flash"
DEFAULT_STYLE = "explain"
DEFAULT_LANGUAGE = "zh-CN"

SUPPORTED_PROVIDERS = ("deepseek",)
SUPPORTED_MODELS = ("deepseek-v4-flash", "deepseek-v4-pro")
SUPPORTED_STYLES = ("explain", "simple", "tech")


@dataclass
class AppConfig:
    provider: str = DEFAULT_PROVIDER
    api_key: str = ""
    base_url: str = DEFAULT_BASE_URL
    model: str = DEFAULT_MODEL
    style: str = DEFAULT_STYLE
    language: str = DEFAULT_LANGUAGE

    @property
    def has_api_key(self) -> bool:
        return bool(self.api_key.strip())

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "AppConfig":
        return cls(
            provider=str(data.get("provider") or DEFAULT_PROVIDER),
            api_key=str(data.get("api_key") or ""),
            base_url=str(data.get("base_url") or DEFAULT_BASE_URL),
            model=str(data.get("model") or DEFAULT_MODEL),
            style=str(data.get("style") or DEFAULT_STYLE),
            language=str(data.get("language") or DEFAULT_LANGUAGE),
        )

    def to_mapping(self) -> dict[str, str]:
        return {
            "provider": self.provider,
            "api_key": self.api_key,
            "base_url": self.base_url,
            "model": self.model,
            "style": self.style,
            "language": self.language,
        }


def load_config(path: Path = CONFIG_PATH) -> AppConfig:
    if not path.exists():
        return AppConfig()
    try:
        document = tomlkit.parse(path.read_text(encoding="utf-8"))
    except Exception:
        return AppConfig()
    return AppConfig.from_mapping(dict(document))


def save_config(config: AppConfig, path: Path = CONFIG_PATH) -> None:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    document = tomlkit.document()
    for key, value in config.to_mapping().items():
        document[key] = value
    path.write_text(tomlkit.dumps(document), encoding="utf-8")
    path.chmod(0o600)


def reset_config(path: Path = CONFIG_PATH) -> None:
    if path.exists():
        path.unlink()


def mask_api_key(api_key: str) -> str:
    value = api_key.strip()
    if not value:
        return "<未设置>"
    if len(value) <= 8:
        return "****"
    prefix = value[:3]
    suffix = value[-4:]
    return f"{prefix}-****{suffix}" if not prefix.endswith("-") else f"{prefix}****{suffix}"
