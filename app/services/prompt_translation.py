# app/services/prompt_translation.py

import os
import requests
import logging

logger = logging.getLogger(__name__)


def translate_visual_direction_to_english(custom_direction: str) -> str:
    """
    Translate Vietnamese extra art direction into English visual instructions
    for image editing providers.

    If Gemini fails, return the original input so the pipeline does not break.
    """
    custom_direction = (custom_direction or "").strip()

    if not custom_direction:
        return ""

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    model = os.getenv("GEMINI_TEXT_MODEL", "gemini-2.5-flash-lite").strip()

    if not api_key:
        logger.warning("GEMINI_API_KEY not found. Using original custom direction.")
        return custom_direction

    system_prompt = f"""
You are a prompt translation assistant for an AI product image editing system.

Task:
Translate the user's Vietnamese visual art direction into clear English instructions for an AI image editing model.

Important rules:
1. Keep only instructions about background, surface, lighting, shadow, camera angle, composition, mood, and campaign style.
2. Do not add any new product details.
3. Do not allow changes to product identity.
4. If the user asks to change the product logo, color, shape, material, text, label, pattern, damage, or visible condition, rewrite that part as: "Keep the product identity unchanged."
5. Do not include explanation.
6. Do not include markdown.
7. Return only the English prompt.

Vietnamese user direction:
{custom_direction}
"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": system_prompt}]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 512
        }
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()

        translated = (
            data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
            .strip()
        )

        if not translated:
            logger.warning("Gemini translation returned empty output. Using original custom direction.")
            return custom_direction

        logger.info("Custom direction translated successfully.")
        return translated

    except Exception as e:
        logger.warning("Custom direction translation failed: %s", str(e))
        return custom_direction