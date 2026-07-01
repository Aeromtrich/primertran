from primertran.config import AppConfig, load_config, mask_api_key, save_config


def test_mask_api_key() -> None:
    assert mask_api_key("") == "<未设置>"
    assert mask_api_key("short") == "****"
    assert mask_api_key("sk-1234567890") == "sk-****7890"


def test_save_and_load_config(tmp_path) -> None:
    path = tmp_path / "config.toml"
    config = AppConfig(api_key="sk-test", model="deepseek-v4-pro", style="tech")

    save_config(config, path)
    loaded = load_config(path)

    assert loaded.api_key == "sk-test"
    assert loaded.model == "deepseek-v4-pro"
    assert loaded.style == "tech"
    assert oct(path.stat().st_mode & 0o777) == "0o600"
