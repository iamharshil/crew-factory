"""Environment-backed LLM configuration for the software factory."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from crewai import LLM
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


class ConfigurationError(RuntimeError):
    """Raised when required provider credentials are not configured."""


@dataclass(frozen=True)
class LLMSettings:
    """Configured language models for each role in the factory."""

    product_manager: LLM
    tech_lead: LLM
    senior_developer: LLM
    qa_reviewer: LLM


def build_llm_settings() -> LLMSettings:
    """Build role-specific LLMs after validating all required API keys."""
    required_keys = (
        "ANTHROPIC_API_KEY",
        "OPENAI_API_KEY",
        "OPENROUTER_API_KEY",
        "GEMINI_API_KEY",
    )
    missing = [key for key in required_keys if not os.getenv(key)]
    if missing:
        names = ", ".join(missing)
        raise ConfigurationError(
            f"Missing required API key(s): {names}. "
            "Copy .env.example to .env and fill in each provider key."
        )

    return LLMSettings(
        product_manager=LLM(
            model="anthropic/claude-3-7-sonnet-latest",
            is_litellm=True,
            provider="litellm",
            api_key=os.environ["ANTHROPIC_API_KEY"],
            temperature=0.2,
        ),
        tech_lead=LLM(
            model="openai/gpt-4o",
            is_litellm=True,
            provider="litellm",
            api_key=os.environ["OPENAI_API_KEY"],
            temperature=0.1,
        ),
        senior_developer=LLM(
            model="openrouter/deepseek/deepseek-chat",
            is_litellm=True,
            provider="litellm",
            api_key=os.environ["OPENROUTER_API_KEY"],
            base_url="https://openrouter.ai/api/v1",
            temperature=0.1,
        ),
        qa_reviewer=LLM(
            model="gemini/gemini-2.0-flash",
            is_litellm=True,
            provider="litellm",
            api_key=os.environ["GEMINI_API_KEY"],
            temperature=0.1,
        ),
    )
