from primertran.prompts import SYSTEM_PROMPT, build_user_prompt


def test_system_prompt_requires_chunked_processing() -> None:
    assert "长文本必须先切分" in SYSTEM_PROMPT
    assert "每个分片都必须独立套用用户指定的输出模板" in SYSTEM_PROMPT


def test_explain_prompt_applies_template_to_each_chunk() -> None:
    prompt = build_user_prompt("First sentence. Second sentence.", "explain")

    assert "每个分片都严格按下面模板输出" in prompt
    assert "原句：" in prompt
    assert "翻译：" in prompt
    assert "解释：" in prompt
    assert "First sentence. Second sentence." in prompt


def test_tech_prompt_uses_technical_chunk_template() -> None:
    prompt = build_user_prompt("Run npm install.", "tech")

    assert "技术语义分片" in prompt
    assert "技术解释：" in prompt
    assert "Run npm install." in prompt

