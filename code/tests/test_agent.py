import pytest

from primertran.agent import MAX_INPUT_LENGTH, TranslationInputError, TranslatorAgent, looks_like_english
from primertran.config import AppConfig


def test_looks_like_english() -> None:
    assert looks_like_english("Gain hands-on experience with AWS CLI.")
    assert looks_like_english("请翻译 this command output")
    assert not looks_like_english("请输入中文内容")


def test_agent_rejects_non_english() -> None:
    agent = TranslatorAgent(AppConfig(api_key="sk-test"))

    with pytest.raises(TranslationInputError):
        agent.translate("这是中文")


def test_agent_rejects_long_input() -> None:
    agent = TranslatorAgent(AppConfig(api_key="sk-test"))

    with pytest.raises(TranslationInputError):
        agent.translate("a" * (MAX_INPUT_LENGTH + 1))
