from primertran.config import AppConfig
from primertran.providers.base import BaseProvider, ProviderError
from primertran.providers.deepseek import DeepSeekProvider


def create_provider(config: AppConfig) -> BaseProvider:
    if config.provider == "deepseek":
        return DeepSeekProvider(api_key=config.api_key, base_url=config.base_url)
    raise ProviderError(f"暂不支持 provider: {config.provider}")


__all__ = ["BaseProvider", "ProviderError", "create_provider"]
