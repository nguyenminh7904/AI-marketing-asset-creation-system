from loguru import logger

from app.config import settings
from app.services.llm_providers.gemini_text_provider import GeminiTextProvider
from app.services.llm_providers.mock_provider import MockLLMProvider


class LLMService:
    def __init__(self):
        self.providers = self._build_provider_chain()

    def _build_provider_chain(self):
        registry = {
            "gemini_text": GeminiTextProvider,
            "mock": MockLLMProvider,
        }

        providers = []
        for name in settings.LLM_PROVIDER_CHAIN.split(","):
            name = name.strip().lower()
            if name in registry:
                providers.append(registry[name]())

        if not providers:
            providers.append(MockLLMProvider())

        return providers

    def generate_product_content(
        self,
        product_name,
        visual_prompt,
        content_prompt,
        tone,
        campaign_context: dict | None = None,
    ) -> dict:
        errors = []

        for provider in self.providers:
            try:
                logger.info(f"Trying LLM provider | provider={provider.name}")
                content = provider.generate(
                    product_name,
                    visual_prompt,
                    content_prompt,
                    tone,
                    campaign_context=campaign_context or {},
                )
                return self._normalize_content(content)
            except Exception as exc:
                error = self._safe_error(exc)
                logger.warning(f"LLM provider failed | provider={provider.name} | error={error}")
                errors.append(f"{provider.name}: {error}")

        raise RuntimeError("All LLM providers failed: " + " | ".join(errors))

    def _normalize_content(self, content: dict) -> dict:
        hashtags = content.get("hashtags") or []
        if isinstance(hashtags, str):
            hashtags = [tag.strip() for tag in hashtags.split() if tag.strip()]

        channel_outputs = content.get("channel_outputs") or {}
        description = content.get("description") or channel_outputs.get("product_description") or ""
        caption = content.get("caption") or channel_outputs.get("instagram_caption") or ""

        if "product_description" not in channel_outputs:
            channel_outputs["product_description"] = description
        if "instagram_caption" not in channel_outputs:
            channel_outputs["instagram_caption"] = caption
        if "hashtags" not in channel_outputs:
            channel_outputs["hashtags"] = hashtags

        return {
            "provider": content.get("provider", "unknown"),
            "description": description,
            "caption": caption,
            "hashtags": hashtags,
            "channel_outputs": channel_outputs,
        }

    def _safe_error(self, exc: Exception) -> str:
        message = str(exc).replace("\n", " ").strip()
        if len(message) > 240:
            message = message[:240] + "..."
        return f"{type(exc).__name__}: {message}"
