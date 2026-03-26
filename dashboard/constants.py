"""
Centrale AI-configuratie: providers, modellen en tiers.

Dit is de single source of truth voor alle AI-gerelateerde configuratie
in het project. Alle imports van PROVIDER_CONFIG en SUGGESTED_MODELS
moeten naar dit bestand verwijzen.
"""

PROVIDER_CONFIG = {
    "gemini": {"prefix": "gemini/", "env_key": "GEMINI_API_KEY"},
    "anthropic": {"prefix": "anthropic/", "env_key": "ANTHROPIC_API_KEY"},
    "openai": {"prefix": "openai/", "env_key": "OPENAI_API_KEY"},
}

SUGGESTED_MODELS = {
    "gemini": [
        {"id": "gemini-3.1-pro-preview", "label": "Gemini 3.1 Pro", "tier": "flagship"},
        {"id": "gemini-3-flash-preview", "label": "Gemini 3 Flash", "tier": "pro"},
        {"id": "gemini-3.1-flash-lite-preview", "label": "Gemini 3.1 Flash Lite", "tier": "fast"},
    ],
    "anthropic": [
        {"id": "claude-opus-4-6", "label": "Claude Opus 4.6", "tier": "flagship"},
        {"id": "claude-sonnet-4-6", "label": "Claude Sonnet 4.6", "tier": "pro"},
        {"id": "claude-haiku-4-5", "label": "Claude Haiku 4.5", "tier": "fast"},
    ],
    "openai": [
        {"id": "gpt-5.4", "label": "GPT-5.4", "tier": "flagship"},
        {"id": "gpt-5.4-mini", "label": "GPT-5.4 Mini", "tier": "pro"},
        {"id": "gpt-5.4-nano", "label": "GPT-5.4 Nano", "tier": "fast"},
        {"id": "o3-mini", "label": "o3 Mini", "tier": "reasoning"},
    ],
}

# Convenience defaults
DEFAULT_GEMINI_MODEL = "gemini-3-flash-preview"
DEFAULT_GEMINI_FLAGSHIP = "gemini-3.1-pro-preview"
DEFAULT_GEMINI_FAST = "gemini-3.1-flash-lite-preview"
