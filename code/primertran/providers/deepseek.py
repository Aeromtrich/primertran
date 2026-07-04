from __future__ import annotations

from collections.abc import Iterator

from openai import APIConnectionError, APIStatusError, APITimeoutError, OpenAI

from primertran.providers.base import BaseProvider, ProviderError


class DeepSeekProvider(BaseProvider):
    def __init__(self, *, api_key: str, base_url: str, timeout: float = 60.0) -> None:
        self.client = OpenAI(api_key=api_key, base_url=base_url, timeout=timeout)

    def translate(self, *, system_prompt: str, user_prompt: str, model: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
            )
        except APITimeoutError as exc:
            raise ProviderError("本次请求超时，可稍后重试。") from exc
        except APIConnectionError as exc:
            raise ProviderError("网络请求失败，请检查网络或稍后重试。") from exc
        except APIStatusError as exc:
            raise ProviderError(_status_message(exc.status_code)) from exc
        except Exception as exc:
            raise ProviderError("翻译请求失败，请稍后重试。") from exc

        message = response.choices[0].message.content if response.choices else ""
        return (message or "").strip()

    def translate_stream(self, *, system_prompt: str, user_prompt: str, model: str) -> Iterator[str]:
        try:
            stream = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
                stream=True,
            )
            for chunk in stream:
                if not chunk.choices:
                    continue
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except APITimeoutError as exc:
            raise ProviderError("本次请求超时，可稍后重试。") from exc
        except APIConnectionError as exc:
            raise ProviderError("网络请求失败，请检查网络或稍后重试。") from exc
        except APIStatusError as exc:
            raise ProviderError(_status_message(exc.status_code)) from exc
        except Exception as exc:
            raise ProviderError("翻译请求失败，请稍后重试。") from exc


def _status_message(status_code: int) -> str:
    if status_code in {401, 403}:
        return "API Key 无效或无权限，请使用 /key 更新。"
    if status_code == 404:
        return "模型名可能不正确，请使用 /model 重新选择。"
    if status_code == 429:
        return "请求频率受限或余额不足，请检查 DeepSeek 账户。"
    if 500 <= status_code < 600:
        return "DeepSeek 服务暂时不可用，请稍后重试。"
    return f"请求失败，HTTP 状态码 {status_code}。"
