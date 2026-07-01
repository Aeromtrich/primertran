from __future__ import annotations

import re

from primertran.config import AppConfig
from primertran.prompts import SYSTEM_PROMPT, build_user_prompt
from primertran.providers import create_provider

MAX_INPUT_LENGTH = 8000


class TranslationInputError(ValueError):
    pass


class TranslatorAgent:
    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def translate(self, text: str) -> str:
        cleaned = text.strip()
        if not cleaned:
            raise TranslationInputError("请输入需要翻译的英文内容。")
        if len(cleaned) > MAX_INPUT_LENGTH:
            raise TranslationInputError("输入过长，请拆分为 8000 字符以内后再翻译。")
        if not looks_like_english(cleaned):
            raise TranslationInputError("请输入需要翻译的英文内容。")

        provider = create_provider(self.config)
        return provider.translate(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=build_user_prompt(cleaned, self.config.style),
            model=self.config.model,
        )


def looks_like_english(text: str) -> bool:
    letters = re.findall(r"[A-Za-z]", text)
    if not letters:
        return False
    cjk = re.findall(r"[\u4e00-\u9fff]", text)
    return len(letters) >= max(3, len(cjk))
