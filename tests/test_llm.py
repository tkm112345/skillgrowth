from app import llm
from app.models import Settings


def _settings(**overrides) -> Settings:
    return Settings(
        openai_base_url="https://api.openai.com/v1",
        openai_api_key="key",
        llm_model="gpt-4o-mini",
        llm_vision_model="gpt-4o-mini",
        **overrides,
    )


def test_career_consult_reply_includes_custom_instructions(monkeypatch):
    seen = {}

    def fake_complete(settings, **kwargs):
        seen["system_prompt"] = kwargs["messages"][0]["content"]

        class Choice:
            message = type("M", (), {"content": "ok"})()

        class Resp:
            choices = [Choice()]

        return Resp()

    monkeypatch.setattr(llm, "_complete", fake_complete)

    settings = _settings(consult_custom_instructions="Always answer in a blunt, no-nonsense tone.")
    llm.career_consult_reply([{"role": "user", "content": "hi"}], "career data here", "en", settings)

    assert "Always answer in a blunt, no-nonsense tone." in seen["system_prompt"]


def test_career_consult_reply_omits_custom_instructions_block_when_empty(monkeypatch):
    seen = {}

    def fake_complete(settings, **kwargs):
        seen["system_prompt"] = kwargs["messages"][0]["content"]

        class Choice:
            message = type("M", (), {"content": "ok"})()

        class Resp:
            choices = [Choice()]

        return Resp()

    monkeypatch.setattr(llm, "_complete", fake_complete)

    settings = _settings(consult_custom_instructions="")
    llm.career_consult_reply([{"role": "user", "content": "hi"}], "career data here", "en", settings)

    assert "__CUSTOM_INSTRUCTIONS__" not in seen["system_prompt"]
    assert "追加の指示" not in seen["system_prompt"]
