import importlib
import sys

sys.path.append(".")

import app.config as config


def test_defaults_to_groq_when_provider_not_set(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.setenv("GROQ_API_KEY", "test-groq-key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic-key")

    reloaded = importlib.reload(config)
    provider = reloaded.get_llm_provider_config()

    assert provider["provider"] == "groq"
    assert provider["api_key"] == "test-groq-key"
    assert provider["model"] == "llama-3.3-70b-versatile"


def test_prefers_anthropic_when_requested(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    monkeypatch.setenv("GROQ_API_KEY", "test-groq-key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic-key")

    reloaded = importlib.reload(config)
    provider = reloaded.get_llm_provider_config()

    assert provider["provider"] == "anthropic"
    assert provider["api_key"] == "test-anthropic-key"
    assert provider["model"] == "claude-sonnet-4-6"
