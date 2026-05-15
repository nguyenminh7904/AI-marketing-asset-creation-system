import json
from app.config import settings
from app.services.llm_providers.base import LLMProvider


class GeminiTextProvider(LLMProvider):
    name = "gemini_text"

    def generate(self, product_name, visual_prompt, content_prompt, tone, campaign_context=None) -> dict:
        if not settings.GEMINI_API_KEY:
            raise RuntimeError("Missing GEMINI_API_KEY")

        from google import genai

        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        name = product_name or "pre-owned fashion product"
        campaign_context = campaign_context or {}

        prompt = f'''
You are a senior fashion retail marketer and social commerce copywriter.

Product name: {name}
Campaign context JSON:
{json.dumps(campaign_context, ensure_ascii=False, indent=2)}
Visual concept: {visual_prompt}
User task: {content_prompt}
Tone: {tone}

Write campaign-ready marketing content for a small fashion seller.
Use the requested language from the campaign context.
Use the copy framework from the campaign context when possible.
Keep claims realistic and avoid unsupported promises.

Return ONLY valid JSON:
{{
  "description": "...",
  "caption": "...",
  "hashtags": ["#tag1", "#tag2", "#tag3"],
  "channel_outputs": {{
    "seo_title": "...",
    "product_description": "...",
    "instagram_caption": "...",
    "facebook_ad": "...",
    "tiktok_script": "...",
    "shopee_description": "...",
    "email_subject": "...",
    "cta_suggestions": ["...", "..."],
    "hashtags": ["#tag1", "#tag2", "#tag3"]
  }}
}}
'''

        response = client.models.generate_content(
            model=settings.GEMINI_TEXT_MODEL,
            contents=prompt,
        )

        raw = response.text.strip().replace("```json", "").replace("```", "").strip()
        data = json.loads(raw)

        return {
            "provider": self.name,
            "description": data.get("description", ""),
            "caption": data.get("caption", ""),
            "hashtags": data.get("hashtags", []),
            "channel_outputs": data.get("channel_outputs", {}),
        }
