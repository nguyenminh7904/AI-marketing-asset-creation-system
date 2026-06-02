from __future__ import annotations

import json
import os
from collections import Counter
from io import BytesIO
from pathlib import Path
from uuid import uuid4
from urllib.parse import quote

import requests
import streamlit as st
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageEnhance


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env", override=False)

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")
STORAGE_DIR = Path("storage")
OUTPUT_DIR = STORAGE_DIR / "output"
DEMO_IMAGE_PATH = OUTPUT_DIR / "demo_latest.jpg"
DEMO_REFERENCE_PATH = OUTPUT_DIR / "demo_reference_latest.png"

PLATFORMS = ["Instagram", "Facebook", "Shopee", "TikTok", "Website", "Email"]
OBJECTIVES = ["Awareness", "Engagement", "Conversion", "Retargeting"]
FUNNEL_STAGES = ["TOFU", "MOFU", "BOFU"]
TONE_OPTIONS = ["premium", "elegant", "trendy", "minimalist", "persuasive", "informative"]
LANGUAGE_OPTIONS = ["English", "Vietnamese", "Bilingual"]
COPY_FRAMEWORKS = ["AIDA", "PAS", "FAB", "Short Social Caption", "Ecommerce Listing"]
ASPECT_RATIOS = ["1:1", "4:5", "9:16", "16:9"]
IDENTITY_LEVELS = ["strict", "balanced", "creative"]
REFERENCE_USAGE_OPTIONS = [
    "Overall composition",
    "Scene layout",
    "Lighting style",
    "Background mood",
    "Product pose / display style",
]
VISUAL_MODEL_CHOICES = [
    ("Auto (full chain)", ""),
    ("Replicate FLUX", "replicate_flux"),
    ("Cloudflare FLUX", "cloudflare_flux"),
    ("Cloudflare Inpaint", "cloudflare_inpaint"),
    ("Original fallback", "original"),
    ("Mock / demo", "mock"),
]

CAMPAIGN_PRESETS = {
    "luxury_instagram": {
        "label": "Luxury Instagram Post",
        "description": "Quiet luxury visuals for a polished product showcase.",
        "platform": "Instagram",
        "campaign_objective": "Conversion",
        "funnel_stage": "MOFU",
        "tone": "elegant",
        "scene_template": "luxury_studio",
        "background_style": "Warm neutral studio backdrop with soft tonal depth",
        "lighting_style": "Broad diffused key light with subtle fill",
        "camera_angle": "Straight-on hero angle with slight editorial elevation",
        "color_palette": "Ivory, sand, muted taupe, charcoal accents",
        "mood": "Quiet luxury",
        "copy_framework": "AIDA",
        "identity_preservation": "strict",
        "surface_environment": "Matte travertine pedestal",
        "props_include": "None",
        "props_avoid": "Hands, people, duplicate items, distracting branding",
        "aspect_ratio": "4:5",
        "image_style": "Commercial editorial photography",
        "output_language": "English",
    },
    "clean_ecommerce": {
        "label": "Clean E-commerce Listing",
        "description": "Simple listing-friendly layout with product clarity first.",
        "platform": "Website",
        "campaign_objective": "Conversion",
        "funnel_stage": "BOFU",
        "tone": "minimalist",
        "scene_template": "ecommerce_clean",
        "background_style": "Seamless white or pale neutral sweep",
        "lighting_style": "Even high-key illumination",
        "camera_angle": "Front-facing product inspection angle",
        "color_palette": "White, soft gray, neutral beige",
        "mood": "Precise and trustworthy",
        "copy_framework": "Ecommerce Listing",
        "identity_preservation": "strict",
        "surface_environment": "White seamless sweep",
        "props_include": "None",
        "props_avoid": "Props, clutter, shadows that obscure the item",
        "aspect_ratio": "1:1",
        "image_style": "Clean catalog photography",
        "output_language": "English",
    },
    "premium_facebook": {
        "label": "Premium Facebook Ad",
        "description": "Persuasive ad visual with clean lifestyle context.",
        "platform": "Facebook",
        "campaign_objective": "Engagement",
        "funnel_stage": "MOFU",
        "tone": "persuasive",
        "scene_template": "lifestyle_interior",
        "background_style": "Soft interior environment with blurred depth",
        "lighting_style": "Natural window light and gentle ambient fill",
        "camera_angle": "Natural eye-level perspective",
        "color_palette": "Stone, cream, warm wood, muted green",
        "mood": "Warm and aspirational",
        "copy_framework": "PAS",
        "identity_preservation": "balanced",
        "surface_environment": "Modern interior surface with subtle texture",
        "props_include": "Lifestyle props that support the product",
        "props_avoid": "Overcrowded props, competing products, watermarks",
        "aspect_ratio": "4:5",
        "image_style": "Premium lifestyle advertising",
        "output_language": "English",
    },
    "minimal_studio": {
        "label": "Minimal Studio Shot",
        "description": "Minimal campaign visual with a clean modern feel.",
        "platform": "Instagram",
        "campaign_objective": "Awareness",
        "funnel_stage": "TOFU",
        "tone": "minimalist",
        "scene_template": "social_hero",
        "background_style": "Bold but clean campaign backdrop",
        "lighting_style": "Directional hero lighting with readable contrast",
        "camera_angle": "Dynamic but product-centric perspective",
        "color_palette": "Monochrome with one accent color",
        "mood": "Confident and modern",
        "copy_framework": "Short Social Caption",
        "identity_preservation": "balanced",
        "surface_environment": "Minimal studio surface",
        "props_include": "None or a single accent object",
        "props_avoid": "Busy props, clutter, extra text",
        "aspect_ratio": "1:1",
        "image_style": "Modern studio campaign photo",
        "output_language": "English",
    },
    "seasonal_campaign": {
        "label": "Seasonal Campaign",
        "description": "A festive but premium visual for launches or holiday moments.",
        "platform": "Instagram",
        "campaign_objective": "Awareness",
        "funnel_stage": "TOFU",
        "tone": "trendy",
        "scene_template": "seasonal_campaign",
        "background_style": "Seasonal backdrop with controlled accent colors",
        "lighting_style": "Soft launch lighting with a polished highlight",
        "camera_angle": "Editorial hero shot",
        "color_palette": "Warm ivory, muted gold, deep green, soft red accents",
        "mood": "Celebratory but premium",
        "copy_framework": "AIDA",
        "identity_preservation": "balanced",
        "surface_environment": "Seasonal display surface with premium styling",
        "props_include": "Seasonal accents only",
        "props_avoid": "Holiday clutter, fake labels, extra products",
        "aspect_ratio": "4:5",
        "image_style": "Seasonal editorial advertising",
        "output_language": "English",
    },
    "product_launch": {
        "label": "Product Launch Visual",
        "description": "High-energy launch visual for a new product spotlight.",
        "platform": "TikTok",
        "campaign_objective": "Engagement",
        "funnel_stage": "TOFU",
        "tone": "trendy",
        "scene_template": "social_hero",
        "background_style": "Bold but clean campaign backdrop",
        "lighting_style": "Directional hero lighting with readable contrast",
        "camera_angle": "Dynamic but product-centric perspective",
        "color_palette": "Monochrome with one accent color",
        "mood": "Confident and modern",
        "copy_framework": "PAS",
        "identity_preservation": "creative",
        "surface_environment": "Launch-stage hero surface",
        "props_include": "One or two launch accents",
        "props_avoid": "Clutter, text overlays, unrelated objects",
        "aspect_ratio": "9:16",
        "image_style": "Launch campaign content",
        "output_language": "English",
    },
}

SCENE_TEMPLATES = {
    "luxury_studio": {
        "title": "Luxury Studio",
        "description": "Clean premium set with restrained materials and editorial lighting.",
        "background_style": "Warm neutral studio backdrop with soft tonal depth",
        "lighting_style": "Broad diffused key light with subtle fill",
        "camera_angle": "Straight-on hero angle with slight editorial elevation",
        "surface_environment": "Matte stone or satin tabletop",
        "props_include": "Minimal props kept far behind the hero area",
        "props_avoid": "Clutter, people, hands, text overlays, duplicate products",
        "color_palette": "Ivory, sand, muted taupe, charcoal accents",
        "mood": "Quiet luxury",
        "image_style": "Commercial editorial photography",
    },
    "lifestyle_interior": {
        "title": "Lifestyle Interior",
        "description": "Tasteful home setting with context that feels lived-in but controlled.",
        "background_style": "Soft interior environment with blurred depth",
        "lighting_style": "Natural window light and gentle ambient fill",
        "camera_angle": "Natural eye-level perspective",
        "surface_environment": "Neutral shelf, sofa side table, or wooden plane",
        "props_include": "Subtle decor in the background only",
        "props_avoid": "Busy rooms, visible branding, people, hands, competing products",
        "color_palette": "Stone, cream, warm wood, muted green",
        "mood": "Warm and aspirational",
        "image_style": "Lifestyle commercial photography",
    },
    "ecommerce_clean": {
        "title": "Ecommerce Clean",
        "description": "Plain clean background for product inspection and listing clarity.",
        "background_style": "Seamless white or pale neutral sweep",
        "lighting_style": "Even high-key illumination",
        "camera_angle": "Front-facing product inspection angle",
        "surface_environment": "Flat catalog surface with a soft grounding shadow",
        "props_include": "None unless needed for scale and kept outside the product silhouette",
        "props_avoid": "Props covering the product, labels, watermarks, extra text",
        "color_palette": "White, soft gray, neutral beige",
        "mood": "Precise and trustworthy",
        "image_style": "Ecommerce catalog photography",
    },
    "seasonal_campaign": {
        "title": "Seasonal Campaign",
        "description": "A more expressive scene for launches, gifting, and campaign moments.",
        "background_style": "Seasonal backdrop with controlled accent colors",
        "lighting_style": "Soft launch lighting with a polished highlight",
        "camera_angle": "Editorial hero shot",
        "surface_environment": "Styled pedestal or campaign surface",
        "props_include": "Seasonal accents kept far behind the product",
        "props_avoid": "Confetti, busy ornaments, competing products, people, text",
        "color_palette": "Warm ivory, muted gold, deep green, soft red accents",
        "mood": "Celebratory but premium",
        "image_style": "Campaign key visual",
    },
    "social_hero": {
        "title": "Social Hero Shot",
        "description": "Punchy composition optimized for short-form social attention.",
        "background_style": "Bold but clean campaign backdrop",
        "lighting_style": "Directional hero lighting with readable contrast",
        "camera_angle": "Dynamic but product-centric perspective",
        "surface_environment": "Simple modern plane or stage",
        "props_include": "One or two supporting elements far from the hero area",
        "props_avoid": "Visual noise, labels, extra products, people, hands",
        "color_palette": "Monochrome with one accent color",
        "mood": "Confident and modern",
        "image_style": "Social media hero image",
    },
}

REVIEW_CHECKLIST = [
    "Product identity preserved",
    "Color/material unchanged",
    "Logo/hardware unchanged",
    "Reference photo did not override product identity",
    "No misleading details added",
    "Copy does not make unsupported claims",
    "Ready for business use",
]


def init_state() -> None:
    st.session_state.setdefault("demo_mode", False)
    st.session_state.setdefault("demo_assets", [])
    st.session_state.setdefault("latest_result", None)
    st.session_state.setdefault("selected_review_asset_id", None)
    st.session_state.setdefault("sample_brief_loaded", False)
    st.session_state.setdefault("campaign_preset", "luxury_instagram")
    st.session_state.setdefault("visual_model_choice", "Auto (full chain)")
    st.session_state.setdefault("use_campaign_preset", True)
    st.session_state.setdefault("custom_scene_prompt", "")
    st.session_state.setdefault("reference_usage", ["Overall composition"])
    st.session_state.setdefault("num_variants", 3)


def build_visual_provider_chain(choice_label: str) -> str | None:
    selected_value = dict(VISUAL_MODEL_CHOICES).get(choice_label, "")
    if not selected_value:
        return None

    chain = [selected_value]
    for _, provider_name in VISUAL_MODEL_CHOICES:
        if provider_name and provider_name not in chain:
            chain.append(provider_name)
    return ",".join(chain)


def preset_defaults(preset_key: str) -> dict:
    return CAMPAIGN_PRESETS.get(preset_key, CAMPAIGN_PRESETS["luxury_instagram"])


def apply_preset(preset_key: str) -> None:
    preset = preset_defaults(preset_key)
    st.session_state["campaign_preset"] = preset_key
    st.session_state["use_campaign_preset"] = True
    st.session_state.update(
        {
            "platform": preset["platform"],
            "campaign_objective": preset["campaign_objective"],
            "funnel_stage": preset.get("funnel_stage", "MOFU"),
            "tone": preset["tone"],
            "scene_template": preset["scene_template"],
            "background_style": preset["background_style"],
            "lighting_style": preset["lighting_style"],
            "camera_angle": preset["camera_angle"],
            "color_palette": preset["color_palette"],
            "mood": preset["mood"],
            "copy_framework": preset["copy_framework"],
            "identity_preservation": preset["identity_preservation"],
            "surface_environment": preset.get("surface_environment", ""),
            "props_include": preset.get("props_include", ""),
            "props_avoid": preset.get("props_avoid", ""),
            "aspect_ratio": preset.get("aspect_ratio", "4:5"),
            "image_style": preset.get("image_style", ""),
            "output_language": preset.get("output_language", "English"),
        }
    )


def api_get(path: str, **params):
    response = requests.get(f"{API_URL}{path}", params=params or None, timeout=20)
    response.raise_for_status()
    return response.json()


def api_patch(path: str, payload: dict):
    response = requests.patch(f"{API_URL}{path}", json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def api_post_generation(files: dict, data: dict):
    return requests.post(f"{API_URL}/generate", files=files, data=data, timeout=420)


def backend_available() -> bool:
    try:
        api_get("/health")
        return True
    except Exception:
        return False


def safe_assets() -> list[dict]:
    if st.session_state.get("demo_mode"):
        return st.session_state.get("demo_assets", [])
    try:
        return api_get("/assets")
    except Exception:
        return st.session_state.get("demo_assets", [])


def safe_assets_by_status(status: str | None) -> list[dict]:
    if st.session_state.get("demo_mode"):
        assets = st.session_state.get("demo_assets", [])
        return [asset for asset in assets if status is None or asset.get("status") == status]
    try:
        return api_get("/assets", status=status) if status else api_get("/assets")
    except Exception:
        assets = st.session_state.get("demo_assets", [])
        return [asset for asset in assets if status is None or asset.get("status") == status]


def file_url(path: str | None) -> str | None:
    if not path:
        return None
    # Normalize Windows backslashes to forward slashes for URL encoding
    normalized_path = path.replace("\\", "/")
    if st.session_state.get("demo_mode"):
        return normalized_path
    return f"{API_URL}/files?path={quote(normalized_path, safe='')}"


def variant_quality_status(score: int) -> str:
    if score >= 80:
        return "Ready for review"
    if score >= 60:
        return "Usable with inspection"
    return "Needs regeneration"


def selected_variant_id(asset: dict) -> str | None:
    return asset.get("selected_variant_id") or asset.get("best_variant_id")


def selected_variant_image_path(asset: dict) -> str | None:
    return asset.get("selected_image_path") or asset.get("best_image_path")


def selected_variant_number(asset: dict) -> int | None:
    if asset.get("selected_variant_number"):
        return asset["selected_variant_number"]
    variants = asset.get("variants") or []
    chosen_id = selected_variant_id(asset)
    for index, variant in enumerate(variants, start=1):
        if variant.get("variant_id") == chosen_id:
            return index
    return None


def variant_score_value(variant: dict) -> int:
    score = variant.get("display_score")
    if score is None:
        score = status_score((variant.get("scores") or {}).get("final_score"))
    return status_score(score)


def asset_effective_score(asset: dict) -> int:
    score = asset.get("selected_score")
    if score is None:
        score = asset.get("best_score") or (asset.get("quality_report") or {}).get("scorecard", {}).get("final_score")
    return status_score(score)


def asset_variant_count(asset: dict) -> int:
    return len(asset.get("variants") or [])


def variant_direction_label(variant: dict) -> str:
    return variant.get("variant_direction") or "Creative variant"


def variant_notes(variant: dict) -> str:
    notes = variant.get("notes") or []
    if isinstance(notes, list):
        return " ".join(str(note) for note in notes[:2] if note)
    return str(notes)


def apply_variant_selection_to_result(result: dict, variant: dict) -> dict:
    updated = dict(result)
    updated["selected_variant_id"] = variant.get("variant_id")
    updated["selected_variant_number"] = next(
        (index + 1 for index, item in enumerate(result.get("variants") or []) if item.get("variant_id") == variant.get("variant_id")),
        None,
    )
    updated["selected_image_path"] = variant.get("image_path")
    updated["selected_score"] = variant_score_value(variant) / 100
    updated["best_image_path"] = variant.get("image_path")
    updated["best_variant_id"] = variant.get("variant_id")
    return updated


def save_selected_variant(asset_id: str, variant: dict, result: dict) -> dict:
    if st.session_state.get("demo_mode"):
        assets = st.session_state.get("demo_assets", [])
        updated_asset = None
        for asset in assets:
            if asset.get("id") == asset_id:
                asset["selected_variant_id"] = variant.get("variant_id")
                asset["selected_variant_number"] = next(
                    (index + 1 for index, item in enumerate(asset.get("variants") or []) if item.get("variant_id") == variant.get("variant_id")),
                    None,
                )
                asset["selected_image_path"] = variant.get("image_path")
                asset["selected_score"] = variant.get("display_score") or variant_score_value(variant)
                asset["best_image_path"] = variant.get("image_path")
                asset["best_variant_id"] = variant.get("variant_id")
                updated_asset = asset
                break
        if updated_asset is None:
            updated_asset = result
        st.session_state["demo_assets"] = assets
        return apply_variant_selection_to_result(result, variant)

    api_patch(f"/assets/{asset_id}/selection", {"selected_variant_id": variant.get("variant_id")})
    return apply_variant_selection_to_result(result, variant)


def status_score(score: float | int | None) -> int:
    if score is None:
        return 0
    value = float(score)
    if value <= 1.0:
        value *= 100
    return max(0, min(100, int(round(value))))


def asset_status_label(asset: dict) -> str:
    status = (asset.get("status") or "").lower()
    if status in {"approved", "exported"}:
        return "Ready for review"
    score = status_score(asset.get("best_score") or (asset.get("quality_report") or {}).get("scorecard", {}).get("final_score"))
    if score >= 80:
        return "Ready for review"
    if score >= 60:
        return "Usable with inspection"
    return "Needs regeneration"


def score_color(score: int) -> str:
    if score >= 80:
        return "#1b7f4d"
    if score >= 60:
        return "#8a6d1d"
    return "#9e2f2f"


def asset_reference_usage(asset: dict) -> str:
    prompt_controls = asset.get("prompt_controls") or {}
    reference_usage = prompt_controls.get("reference_usage") or asset.get("reference_usage") or []
    if isinstance(reference_usage, list):
        return format_list_phrase(reference_usage)
    if isinstance(reference_usage, str) and reference_usage.strip():
        return reference_usage
    return "Overall composition"


def load_sample_brief() -> None:
    st.session_state.sample_brief_loaded = True
    apply_preset("luxury_instagram")
    st.session_state.update(
        {
            "product_name": "Vintage Leather Crossbody Bag",
            "brand_name": "North Lane Resale",
            "product_category": "Luxury resale handbag",
            "product_condition": "Pre-owned, excellent visible condition",
            "key_product_facts": "Genuine leather, gold-tone hardware, structured silhouette, visible brand stamp",
            "price": "USD 220",
            "offer": "Free shipping this week",
            "target_audience": "Fashion-conscious resale buyers",
            "output_language": "English",
            "use_campaign_preset": True,
            "custom_scene_prompt": "",
            "reference_usage": ["Overall composition"],
            "surface_environment": "Matte travertine pedestal",
            "props_include": "None",
            "props_avoid": "Hands, people, duplicate bags, visible logos not on product",
            "aspect_ratio": "4:5",
            "image_style": "Commercial editorial photography",
            "negative_prompt": "No fake logos, no new text, no watermark, no added damage",
        }
    )


def provider_label(chain_value: str | None, default_label: str) -> str:
    if not chain_value:
        return default_label
    first = chain_value.split(",")[0].strip()
    return first or default_label


def format_list_phrase(values: list[str] | None) -> str:
    items = [value.strip() for value in values or [] if value and value.strip()]
    if not items:
        return "Overall composition"
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + f", and {items[-1]}"


def system_status() -> dict:
    backend_ok = False
    backend_health: dict = {}
    try:
        backend_health = api_get("/health")
        backend_ok = True
    except Exception:
        backend_ok = False

    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    cloudflare_key = os.getenv("CLOUDFLARE_API_TOKEN", "").strip()
    visual_provider = os.getenv("VISUAL_PROVIDER") or provider_label(os.getenv("VISUAL_PROVIDER_CHAIN"), "cloudflare")
    text_provider = os.getenv("TEXT_PROVIDER") or provider_label(os.getenv("LLM_PROVIDER_CHAIN"), "gemini")
    return {
        "backend": "Connected" if backend_ok else "Not connected",
        "gemini": "Detected" if gemini_key else "Missing",
        "cloudflare": "Detected" if cloudflare_key else "Missing",
        "visual_provider": visual_provider,
        "text_provider": text_provider,
        "demo_mode": "On" if st.session_state.get("demo_mode") else "Off",
        "health": backend_health,
    }


def build_visual_prompt(inputs: dict) -> str:
    scene = SCENE_TEMPLATES[inputs["scene_template"]]
    preset = preset_defaults(inputs.get("campaign_preset", "luxury_instagram"))
    product_name = inputs.get("product_name") or "the uploaded product"
    product_condition = inputs.get("product_condition") or "Seller-provided condition only"
    key_product_facts = inputs.get("key_product_facts") or "Only verified facts from the brief"
    custom_scene_prompt = (inputs.get("custom_scene_prompt") or "").strip()
    use_campaign_preset = bool(inputs.get("use_campaign_preset", True))
    reference_usage = format_list_phrase(inputs.get("reference_usage"))
    scene_direction_lines = []
    if use_campaign_preset:
        scene_direction_lines.extend([
            f"Campaign preset: {preset['label']}",
            preset["description"],
            f"Preset scene direction: {SCENE_TEMPLATES[preset['scene_template']]['title']}",
            f"Preset background style: {preset['background_style']}",
            f"Preset lighting style: {preset['lighting_style']}",
            f"Preset camera angle: {preset['camera_angle']}",
            f"Preset mood: {preset['mood']}",
        ])
    if custom_scene_prompt:
        if scene_direction_lines:
            scene_direction_lines.append("Custom scene instruction:")
        scene_direction_lines.append(custom_scene_prompt)
    if not scene_direction_lines:
        scene_direction_lines.extend([
            f"Scene template: {scene['title']}",
            scene["description"],
            f"Background style: {inputs.get('background_style') or scene['background_style']}",
            f"Lighting style: {inputs.get('lighting_style') or scene['lighting_style']}",
            f"Camera angle: {inputs.get('camera_angle') or scene['camera_angle']}",
            f"Surface / environment: {inputs.get('surface_environment') or scene['surface_environment']}",
            f"Props to include: {inputs.get('props_include') or scene['props_include']}",
            f"Props to avoid: {inputs.get('props_avoid') or scene['props_avoid']}",
            f"Color palette: {inputs.get('color_palette') or scene['color_palette']}",
            f"Mood: {inputs.get('mood') or scene['mood']}",
            f"Image style: {inputs.get('image_style') or scene['image_style']}",
        ])
    lines = [
        "Layer 1 - Product Identity Lock",
        "Highest priority:",
        f"Preserve {product_name} exactly. Do not change product shape, color, material, logo, label, hardware, stitching, pattern, visible wear, visible condition, size ratio, or product structure.",
        f"Product condition note: {product_condition}",
        f"Verified product facts: {key_product_facts}",
        "",
        "Layer 2 - Scene Template",
        *scene_direction_lines,
        f"Aspect ratio: {inputs.get('aspect_ratio') or '1:1'}",
        f"Identity preservation level: {inputs.get('identity_preservation') or 'balanced'}",
        "",
        "Layer 3 - Campaign Context",
        f"Platform: {inputs.get('platform')}",
        f"Campaign objective: {inputs.get('campaign_objective')}",
        f"Funnel stage: {inputs.get('funnel_stage')}",
        f"Target audience: {inputs.get('target_audience')}",
        f"Tone of voice: {inputs.get('tone')}",
        f"Campaign mood: {inputs.get('mood') or scene['mood']}",
        f"Campaign preset selected: {preset['label']}",
        "",
        "Layer 4 - Professional Visual Direction",
        "Apply the selected scene direction as a business-ready marketing brief, not raw prompt engineering.",
        "Keep the product centered, readable, and premium.",
        "",
        "Layer 5 - Negative Constraints",
        inputs.get("negative_prompt") or "No fake logos, no new text, no watermark, no people or hands unless explicitly requested, no duplicate product, no added scratches, no added damage, no misleading packaging, no object covering the product, no change to product condition.",
    ]
    if inputs.get("reference_photo_present"):
        lines.extend([
            "",
            "Layer 6 - Optional Reference Photo Guidance",
            f"If a reference image is provided, use it only as visual inspiration for {reference_usage}. The product identity must come from the product photo. Do not copy the product, brand, logo, color, text, label, or unique details from the reference image.",
            "The reference photo can guide scene layout, lighting, background mood, pose, display style, and composition, but it must never replace or override the product photo.",
        ])
    return "\n".join(lines)


def build_copy_prompt(inputs: dict) -> str:
    return "\n".join(
        [
            "Generate marketing copy for the campaign asset.",
            f"Platform: {inputs.get('platform')}",
            f"Target audience: {inputs.get('target_audience')}",
            f"Campaign objective: {inputs.get('campaign_objective')}",
            f"Funnel stage: {inputs.get('funnel_stage')}",
            f"Product facts: {inputs.get('key_product_facts')}",
            f"Offer: {inputs.get('offer')}",
            f"Tone: {inputs.get('tone')}",
            f"Copywriting framework: {inputs.get('copy_framework')}",
            f"Language: {inputs.get('output_language')}",
            "",
            "The output should include headline, short caption, product description, CTA, hashtags if social, ecommerce bullet points if Shopee or website, and claim-safety notes.",
            "Avoid unsupported claims such as authentic, new, limited edition, or official unless the brief explicitly provides them.",
        ]
    )


def build_campaign_payload(inputs: dict) -> dict:
    scene = SCENE_TEMPLATES[inputs["scene_template"]]
    preset = preset_defaults(inputs.get("campaign_preset", "luxury_instagram"))
    campaign_brief = {
        "campaign_preset": inputs.get("campaign_preset"),
        "campaign_preset_label": preset["label"],
        "product_name": inputs.get("product_name"),
        "brand_name": inputs.get("brand_name"),
        "product_category": inputs.get("product_category"),
        "product_condition": inputs.get("product_condition"),
        "key_product_facts": inputs.get("key_product_facts"),
        "price": inputs.get("price"),
        "offer": inputs.get("offer"),
        "platform": inputs.get("platform"),
        "campaign_objective": inputs.get("campaign_objective"),
        "funnel_stage": inputs.get("funnel_stage"),
        "target_audience": inputs.get("target_audience"),
        "tone": inputs.get("tone"),
        "output_language": inputs.get("output_language"),
        "copy_framework": inputs.get("copy_framework"),
        "custom_scene_prompt": inputs.get("custom_scene_prompt"),
        "num_variants": inputs.get("num_variants"),
    }
    prompt_controls = {
        "use_campaign_preset": inputs.get("use_campaign_preset", True),
        "scene_template": scene["title"],
        "scene_template_key": inputs.get("scene_template"),
        "background_style": inputs.get("background_style"),
        "lighting_style": inputs.get("lighting_style"),
        "camera_angle": inputs.get("camera_angle"),
        "surface_environment": inputs.get("surface_environment"),
        "props_include": inputs.get("props_include"),
        "props_avoid": inputs.get("props_avoid"),
        "color_palette": inputs.get("color_palette"),
        "mood": inputs.get("mood"),
        "aspect_ratio": inputs.get("aspect_ratio"),
        "image_style": inputs.get("image_style"),
        "identity_preservation": inputs.get("identity_preservation"),
        "negative_prompt": inputs.get("negative_prompt"),
        "custom_scene_prompt": inputs.get("custom_scene_prompt"),
        "reference_usage": inputs.get("reference_usage"),
        "reference_photo_present": bool(inputs.get("reference_photo_present")),
        "num_variants": inputs.get("num_variants"),
    }
    claim_safety = {
        "safe_claims": [
            "Describe only visible product facts and seller-provided facts.",
            f"Align the copy with {inputs.get('platform')} and {inputs.get('campaign_objective')}.",
        ],
        "risky_claims": ["authentic", "new", "official", "limited edition"],
        "missing_product_information": ["authenticity proof", "material verification", "condition grading if not supplied"],
        "recommended_seller_verification": ["Confirm product condition before publishing", "Verify any brand or authenticity claim with seller records"],
    }
    return {
        "campaign_brief": campaign_brief,
        "prompt_controls": prompt_controls,
        "claim_safety": claim_safety,
        "review_checklist": {label: False for label in REVIEW_CHECKLIST},
        "visual_prompt": build_visual_prompt(inputs),
        "content_prompt": build_copy_prompt(inputs),
        "scene": scene,
    }


def make_demo_visual(product_bytes: bytes | None, title: str, variant_index: int, variant_direction: str) -> str:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / f"demo_variant_{variant_index + 1}.jpg"
    palette = [
        (241, 236, 229),
        (236, 240, 244),
        (244, 238, 232),
        (237, 242, 236),
    ][variant_index % 4]
    canvas = Image.new("RGB", (1600, 1200), (241, 236, 229))
    draw = ImageDraw.Draw(canvas)
    for y in range(canvas.height):
        blend = y / max(1, canvas.height - 1)
        color = (int(palette[0] - blend * 12), int(palette[1] - blend * 18), int(palette[2] - blend * 20))
        draw.line((0, y, canvas.width, y), fill=color)

    if product_bytes:
        with Image.open(BytesIO(product_bytes)) as source:
            product = source.convert("RGBA")
        product.thumbnail((920, 920), Image.Resampling.LANCZOS)
        x = (canvas.width - product.width) // 2
        y = 230
        shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        shadow_draw.ellipse([x + 80, y + product.height - 10, x + product.width - 40, y + product.height + 85], fill=(0, 0, 0, 90))
        composed = Image.alpha_composite(canvas.convert("RGBA"), shadow)
        composed.alpha_composite(product, (x, y))
        result = composed.convert("RGB")
    else:
        result = canvas

    draw = ImageDraw.Draw(result)
    draw.rounded_rectangle([58, 56, 400, 120], radius=24, fill=(25, 35, 29))
    draw.text((82, 74), f"DEMO VARIANT {variant_index + 1}", fill=(255, 255, 255))
    draw.text((64, 1070), title, fill=(47, 43, 39))
    draw.text((64, 1110), variant_direction, fill=(90, 82, 74))
    result = ImageEnhance.Contrast(result).enhance(1.03)
    result.save(output_path, quality=88, optimize=True)
    return str(output_path)


def save_demo_reference(reference_bytes: bytes | None, title: str) -> str | None:
    if not reference_bytes:
        return None
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = DEMO_REFERENCE_PATH
    with Image.open(BytesIO(reference_bytes)) as source:
        source.convert("RGB").save(output_path, format="PNG", optimize=True, compress_level=9)
    return str(output_path)


def build_demo_result(inputs: dict, product_image: bytes | None, reference_image: bytes | None = None) -> dict:
    scene = SCENE_TEMPLATES[inputs["scene_template"]]
    num_variants = max(1, min(4, int(inputs.get("num_variants") or 3)))
    reference_path = save_demo_reference(reference_image, f"{inputs.get('product_name') or 'Reference'} | {scene['title']}")
    claim_safety = build_campaign_payload(inputs)["claim_safety"]
    variant_directions = [
        "Create a clean, balanced campaign visual with strong product clarity.",
        "Create a more premium, luxury-oriented version while keeping product identity unchanged.",
        "Create a more social-commerce-friendly version with stronger visual appeal and clear product focus.",
        "Create a more ecommerce-ready version with simple background and strong product visibility.",
    ][:num_variants]
    variants = []
    base_score = 88 if inputs.get("identity_preservation") == "strict" else 80
    for index in range(num_variants):
        score = max(58, base_score - index * 4)
        image_path = make_demo_visual(
            product_image,
            f"{inputs.get('product_name') or 'Campaign Asset'} | {scene['title']}",
            index,
            variant_directions[index],
        )
        quality_status = variant_quality_status(score)
        variants.append(
            {
                "variant_id": f"v{index + 1}",
                "image_path": image_path,
                "provider": "demo_mode",
                "variant_direction": variant_directions[index],
                "scores": {"final_score": round(score / 100, 4)},
                "technical_diagnostics": {"demo_variant": True},
                "quality_status": quality_status,
                "notes": ["Demo variant for comparison.", quality_status],
                "display_score": score,
                "is_recommended": index == 0,
                "is_selected": False,
            }
        )
    recommended = max(variants, key=lambda item: item["display_score"]) if variants else None
    copy_data = {
        "headline": f"{inputs.get('product_name') or 'Featured product'} | {inputs.get('campaign_objective')} campaign",
        "short_caption": f"{inputs.get('brand_name') or 'The shop'} presents a refined {scene['title']} asset.",
        "product_description": f"{inputs.get('product_name') or 'The product'} is framed for {inputs.get('target_audience')} with a {inputs.get('tone')} tone.",
        "cta": inputs.get("offer") or "Message to buy",
        "hashtags": ["#campaignready", "#productpromotion", "#socialcommerce"],
        "ecommerce_bullets": [inputs.get("key_product_facts") or "Verified product facts only", inputs.get("product_condition") or "Condition reviewed by seller"],
        "claim_safety": claim_safety,
    }
    quality_report = {
        "summary": "Demo-generated asset for presentation stability.",
        "scorecard": {"final_score": round((recommended or variants[0])["display_score"] / 100, 4)},
        "claim_safety": claim_safety,
        "disclaimer": "This result is demo-generated and should be treated as presentation material until live API generation is available.",
    }
    asset_id = f"demo-{uuid4().hex[:10]}"
    return {
        "id": asset_id,
        "asset_id": asset_id,
        "status": "generated",
        "product_image_path": None,
        "reference_image_path": reference_path,
        "reference_usage": inputs.get("reference_usage"),
        "campaign_preset": inputs.get("campaign_preset"),
        "best_image_path": recommended["image_path"] if recommended else variants[0]["image_path"],
        "visual_provider_used": "demo_mode",
        "llm_provider_used": "demo_mode",
        "best_score": round((recommended or variants[0])["display_score"] / 100, 4),
        "display_score": (recommended or variants[0])["display_score"],
        "selected_variant_id": None,
        "selected_variant_number": None,
        "selected_image_path": None,
        "selected_score": None,
        "recommended_variant_id": recommended["variant_id"] if recommended else None,
        "recommended_image_path": recommended["image_path"] if recommended else None,
        "variant_count": num_variants,
        "variants": variants,
        "quality_report": quality_report,
        "description": copy_data["product_description"],
        "caption": copy_data["short_caption"],
        "hashtags": copy_data["hashtags"],
        "channel_outputs": {
            "seo_title": f"{inputs.get('product_name') or 'Campaign asset'} | Demo",
            "product_description": copy_data["product_description"],
            "instagram_caption": copy_data["short_caption"],
            "facebook_ad": copy_data["product_description"],
            "tiktok_script": f"Show the original, then the {scene['title']} demo visual.",
            "shopee_description": "\n".join(copy_data["ecommerce_bullets"]),
            "email_subject": f"New campaign asset: {inputs.get('product_name') or 'Featured product'}",
            "cta_suggestions": [copy_data["cta"], "Request details", "Review the campaign asset"],
            "hashtags": copy_data["hashtags"],
            "claim_safety": claim_safety,
            "ecommerce_bullets": copy_data["ecommerce_bullets"],
        },
        "review_checklist": {label: False for label in REVIEW_CHECKLIST},
        "claim_safety": claim_safety,
        "source": "demo",
    }


def normalize_backend_result(result: dict) -> dict:
    quality = result.get("quality_report") or {}
    score = status_score((quality.get("scorecard") or {}).get("final_score") or result.get("best_score"))
    claim_safety = result.get("claim_safety") or (result.get("channel_outputs") or {}).get("claim_safety") or {}
    return {**result, "best_score": round(score / 100, 4), "display_score": score, "claim_safety": claim_safety, "source": "live"}


def format_timestamp(value: str | None) -> str:
    return value or "Not set"


def render_header() -> None:
    st.markdown(
        """
        <div class="hero-shell">
            <div class="eyebrow">AI Marketing Asset Creation System</div>
            <div class="hero-title">Turn one product image into a campaign-ready marketing package.</div>
            <div class="hero-subtitle">Pick a preset, upload a product image, and generate a polished campaign asset in a guided flow built for non-technical marketing users.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("### System Status")
        status = system_status()
        if status["backend"] == "Connected":
            st.success("Backend connected")
        else:
            st.warning("Backend not connected")
        st.caption(f"Gemini key: {status['gemini']}")
        st.caption(f"Cloudflare key: {status['cloudflare']}")
        st.caption(f"Visual provider: {status['visual_provider']}")
        st.caption(f"Text provider: {status['text_provider']}")
        st.caption(f"Demo mode: {status['demo_mode']}")
        if status["health"]:
            health = status["health"]
            st.caption(f"Visual chain: {health.get('visual_provider_chain')}")
            st.caption(f"Copy chain: {health.get('llm_provider_chain')}")
            for warning in health.get("configuration_warnings", []):
                st.warning(warning)

        st.selectbox(
            "Visual model",
            [label for label, _ in VISUAL_MODEL_CHOICES],
            index=[label for label, _ in VISUAL_MODEL_CHOICES].index(st.session_state.get("visual_model_choice", "Auto (full chain)")) if st.session_state.get("visual_model_choice", "Auto (full chain)") in [label for label, _ in VISUAL_MODEL_CHOICES] else 0,
            key="visual_model_choice",
        )

        st.markdown("### Quick Actions")
        st.toggle("Demo mode", value=st.session_state.get("demo_mode", False), key="demo_mode")
        if st.button("Load sample campaign brief", use_container_width=True):
            load_sample_brief()
            st.rerun()

        if not backend_available() or st.session_state.get("demo_mode"):
            st.info("The workspace can still be used in demo mode or with offline fallback.")
        st.caption(f"Selected model: {st.session_state.get('visual_model_choice', 'Auto (full chain)')}")

        assets = safe_assets()
        counts = Counter(asset.get("status") for asset in assets)
        stat_cols = st.columns(2)
        stat_cols[0].metric("Assets", len(assets))
        stat_cols[1].metric("Approved", counts.get("approved", 0))


def render_status_chip(text: str, color: str = "#2f3a33") -> None:
    st.markdown(
        f'<span style="display:inline-block;padding:0.32rem 0.7rem;border-radius:999px;background:{color};color:#fff;font-size:0.76rem;font-weight:650;letter-spacing:0.02em;">{text}</span>',
        unsafe_allow_html=True,
    )


def render_quality_report(report: dict | None) -> None:
    report = report or {}
    if not report:
        st.info("No quality report available.")
        return
    score = status_score((report.get("scorecard") or {}).get("final_score"))
    st.metric("Quality score", f"{score} / 100")
    st.caption(report.get("summary") or "Quality report available.")
    if report.get("claim_safety"):
        st.json(report["claim_safety"])
    if report.get("disclaimer"):
        st.caption(report["disclaimer"])


def render_copy_section(channel_outputs: dict, key_prefix: str = "copy") -> None:
    claim_safety = channel_outputs.get("claim_safety") or {}
    tabs = st.tabs(["Headline", "Caption", "Description", "CTA", "Channel Copy", "Claim Safety"])
    with tabs[0]:
        st.text_area("Headline", value=channel_outputs.get("seo_title") or channel_outputs.get("headline") or "", height=80, disabled=True, key=f"{key_prefix}_headline")
    with tabs[1]:
        st.text_area("Short caption", value=channel_outputs.get("instagram_caption") or channel_outputs.get("short_caption") or "", height=110, disabled=True, key=f"{key_prefix}_caption")
    with tabs[2]:
        st.text_area("Product description", value=channel_outputs.get("product_description") or channel_outputs.get("description") or "", height=150, disabled=True, key=f"{key_prefix}_description")
    with tabs[3]:
        ctas = channel_outputs.get("cta_suggestions") or []
        st.write(" | ".join(ctas) if ctas else channel_outputs.get("cta", ""))
        ecommerce_bullets = channel_outputs.get("ecommerce_bullets") or []
        if ecommerce_bullets:
            st.caption("Ecommerce bullets")
            for bullet in ecommerce_bullets:
                st.write(f"- {bullet}")
    with tabs[4]:
        cols = st.columns(2)
        with cols[0]:
            st.text_area("Facebook Ad", value=channel_outputs.get("facebook_ad") or "", height=120, disabled=True, key=f"{key_prefix}_facebook_ad")
            st.text_area("Shopee Description", value=channel_outputs.get("shopee_description") or "", height=120, disabled=True, key=f"{key_prefix}_shopee_description")
        with cols[1]:
            st.text_area("TikTok Script", value=channel_outputs.get("tiktok_script") or "", height=150, disabled=True, key=f"{key_prefix}_tiktok_script")
            st.text_area("Email Subject", value=channel_outputs.get("email_subject") or "", height=80, disabled=True, key=f"{key_prefix}_email_subject")
        hashtags = channel_outputs.get("hashtags") or []
        if hashtags:
            st.write(" ".join(hashtags))
    with tabs[5]:
        if claim_safety:
            st.json(claim_safety)
        else:
            st.info("No claim-safety notes available.")


def render_generation_result(result: dict) -> None:
    if not result:
        return
    score = result.get("display_score") or asset_effective_score(result)
    status_label = result.get("display_status") or asset_status_label(result)
    live_label = "Live-generated" if result.get("source") == "live" else "Demo-generated"
    variants = result.get("variants") or []
    recommended_variant_id_value = result.get("recommended_variant_id") or result.get("best_variant_id")
    active_image_path = selected_variant_image_path(result) or result.get("best_image_path")

    st.markdown("### Generated campaign asset")
    render_status_chip(live_label, "#21403a")
    st.write("")
    image_col, detail_col = st.columns([1.05, 0.95], gap="large")
    with image_col:
        if active_image_path:
            st.image(file_url(active_image_path), use_container_width=True)
    with detail_col:
        st.markdown(f"**Score:** {score} / 100")
        st.markdown(f"**Status:** {status_label}")
        if result.get("selected_variant_id"):
            st.caption(f"Selected variant: Variant {result.get('selected_variant_number') or selected_variant_number(result) or '?'}")
        elif recommended_variant_id_value:
            st.caption(f"Recommended variant: Variant {next((index + 1 for index, variant in enumerate(variants) if variant.get('variant_id') == recommended_variant_id_value), 1)}")
        if result.get("visual_provider_used"):
            st.caption(f"Visual provider: {result['visual_provider_used']}")
        if result.get("llm_provider_used"):
            st.caption(f"Copy provider: {result['llm_provider_used']}")
        if result.get("reference_image_path"):
            st.caption(f"Reference-guided: {asset_reference_usage(result)}")
        render_status_chip("Usable with inspection" if score >= 60 else "Needs regeneration", score_color(score))
        if result.get("source") == "demo":
            st.info("This asset is demo-generated for presentation stability.")
        elif result.get("quality_report"):
            st.caption((result.get("quality_report") or {}).get("summary", ""))
    render_copy_section(result.get("channel_outputs") or {}, key_prefix=f"studio_{result.get('id', 'latest')}")

    if variants:
        st.markdown("### Variant Comparison")
        cols = st.columns(2 if len(variants) > 1 else 1, gap="large")
        for index, variant in enumerate(variants):
            with cols[index % len(cols)]:
                with st.container(border=True):
                    variant_score = variant_score_value(variant)
                    is_recommended = bool(variant.get("is_recommended") or variant.get("variant_id") == recommended_variant_id_value)
                    if variant.get("image_path"):
                        st.image(file_url(variant["image_path"]), use_container_width=True)
                    st.markdown(f"**Variant {index + 1}**")
                    st.markdown(f"Quality Score: {variant_score} / 100")
                    st.caption(variant.get("quality_status") or variant_quality_status(variant_score))
                    st.caption(variant_direction_label(variant))
                    notes = variant_notes(variant)
                    if notes:
                        st.caption(notes)
                    if is_recommended:
                        render_status_chip("Recommended", "#7d6c54")
                    current_selected = selected_variant_id(result)
                    if current_selected == variant.get("variant_id"):
                        st.success("Selected for Review")
                    elif st.button("Select This Variant", key=f"select_{result.get('asset_id')}_{variant.get('variant_id')}", use_container_width=True):
                        try:
                            updated_result = save_selected_variant(result.get("asset_id") or result.get("id") or "", variant, result)
                            st.session_state["latest_result"] = updated_result
                            st.rerun()
                        except Exception as exc:
                            st.error(f"Could not save selected variant: {exc}")


def render_studio_tab() -> None:
    st.markdown("## Studio")
    st.caption("A guided workflow for non-technical marketing users.")
    if st.session_state.get("sample_brief_loaded"):
        st.info("Sample campaign brief loaded.")

    st.markdown("### 1. Choose a campaign preset")
    preset_keys = list(CAMPAIGN_PRESETS.keys())
    preset_rows = [preset_keys[i:i + 3] for i in range(0, len(preset_keys), 3)]
    for row in preset_rows:
        cols = st.columns(len(row), gap="medium")
        for col, preset_key in zip(cols, row):
            preset = CAMPAIGN_PRESETS[preset_key]
            with col:
                selected = st.session_state.get("campaign_preset") == preset_key
                with st.container(border=True):
                    st.markdown(f"**{preset['label']}**")
                    st.caption(preset["description"])
                    if selected:
                        st.success("Selected")
                    if st.button("Use preset", key=f"preset_{preset_key}", use_container_width=True):
                        apply_preset(preset_key)
                        st.rerun()

    st.checkbox(
        "Use campaign preset",
        help="Keep this on for the guided flow. Turn it off if you want the custom scene prompt to drive the scene instead.",
        key="use_campaign_preset",
    )
    if st.session_state.get("use_campaign_preset", True):
        st.success("Guided preset mode is on. The selected preset will shape the scene unless you override it with a custom scene prompt.")
    else:
        st.warning("Guided preset mode is off. The custom scene prompt and manual scene fields will take priority over the preset style.")

    use_campaign_preset = bool(st.session_state.get("use_campaign_preset", True))
    num_variants = st.session_state.get("num_variants", 3)

    with st.form("studio_form", clear_on_submit=False):
        main_col, preview_col = st.columns([1.08, 0.92], gap="large")
        with main_col:
            st.markdown("### 2. Upload your product")
            product_image = st.file_uploader("Upload product image", type=["jpg", "jpeg", "png", "webp"], label_visibility="collapsed")
            if product_image:
                st.image(product_image, caption="Uploaded product image", use_container_width=True)
            reference_image = st.file_uploader(
                "Reference Style Photo — optional",
                type=["jpg", "jpeg", "png", "webp"],
                help="Upload a reference image if you want the AI to follow a specific scene, pose, lighting, display style, or composition. The product identity will still come from your product photo.",
            )
            if reference_image:
                st.image(reference_image, caption="Reference style photo", use_container_width=True)
                st.info("Current visual provider may not fully support image reference conditioning. The reference photo is saved and used as prompt guidance where supported.")
            reference_usage = st.multiselect(
                "Use reference photo for",
                options=REFERENCE_USAGE_OPTIONS,
                help="Choose what the reference photo should guide. The product photo still controls the item identity.",
                key="reference_usage",
            )
            product_name = st.text_input("Product name", value=st.session_state.get("product_name", ""), placeholder="Enter the product name")
            campaign_name_input = st.text_input("Campaign name (optional)", value=st.session_state.get("campaign_name_input", ""), placeholder="Give this campaign a custom name to distinguish it")
            st.session_state["campaign_name_input"] = campaign_name_input
            preset = preset_defaults(st.session_state.get("campaign_preset", "luxury_instagram"))
            scene_keys = list(SCENE_TEMPLATES.keys())
            active_scene_key = preset["scene_template"] if use_campaign_preset else st.session_state.get("scene_template", preset["scene_template"])
            if active_scene_key not in SCENE_TEMPLATES:
                active_scene_key = preset["scene_template"]
            active_scene = SCENE_TEMPLATES[active_scene_key]
            scene_template_value = active_scene_key if use_campaign_preset else st.session_state.get("scene_template", active_scene_key)
            background_style_value = preset["background_style"] if use_campaign_preset else st.session_state.get("background_style", active_scene["background_style"])
            lighting_style_value = preset["lighting_style"] if use_campaign_preset else st.session_state.get("lighting_style", active_scene["lighting_style"])
            camera_angle_value = preset["camera_angle"] if use_campaign_preset else st.session_state.get("camera_angle", active_scene["camera_angle"])
            surface_environment_value = active_scene["surface_environment"] if use_campaign_preset else st.session_state.get("surface_environment", active_scene["surface_environment"])
            props_include_value = active_scene["props_include"] if use_campaign_preset else st.session_state.get("props_include", active_scene["props_include"])
            props_avoid_value = active_scene["props_avoid"] if use_campaign_preset else st.session_state.get("props_avoid", active_scene["props_avoid"])
            color_palette_value = preset["color_palette"] if use_campaign_preset else st.session_state.get("color_palette", preset["color_palette"])
            mood_value = preset["mood"] if use_campaign_preset else st.session_state.get("mood", preset["mood"])
            aspect_ratio_value = preset.get("aspect_ratio", "4:5") if use_campaign_preset else st.session_state.get("aspect_ratio", preset.get("aspect_ratio", "4:5"))
            image_style_value = active_scene["image_style"] if use_campaign_preset else st.session_state.get("image_style", active_scene["image_style"])
            identity_preservation_value = preset["identity_preservation"] if use_campaign_preset else st.session_state.get("identity_preservation", preset["identity_preservation"])

            with st.expander("Advanced Settings", expanded=False):
                brand_name = st.text_input("Brand / seller name", value=st.session_state.get("brand_name", ""))
                product_category = st.text_input("Product category", value=st.session_state.get("product_category", ""))
                product_condition = st.text_input("Product condition", value=st.session_state.get("product_condition", ""))
                key_product_facts = st.text_area("Key product facts", value=st.session_state.get("key_product_facts", ""), height=92)
                target_audience = st.text_input("Target audience", value=st.session_state.get("target_audience", ""), placeholder="Who should this campaign speak to?")
                price = st.text_input("Optional price / offer", value=st.session_state.get("price", ""))
                offer = st.text_input("Offer", value=st.session_state.get("offer", ""))
                platform = st.selectbox("Platform", PLATFORMS, index=PLATFORMS.index(st.session_state.get("platform", preset["platform"])) if st.session_state.get("platform", preset["platform"]) in PLATFORMS else 0)
                campaign_objective = st.selectbox("Campaign objective", OBJECTIVES, index=OBJECTIVES.index(st.session_state.get("campaign_objective", preset["campaign_objective"])) if st.session_state.get("campaign_objective", preset["campaign_objective"]) in OBJECTIVES else 2)
                funnel_stage = st.selectbox("Funnel stage", FUNNEL_STAGES, index=FUNNEL_STAGES.index(st.session_state.get("funnel_stage", "MOFU")) if st.session_state.get("funnel_stage") in FUNNEL_STAGES else 1)
                tone = st.selectbox("Tone of voice", TONE_OPTIONS, index=TONE_OPTIONS.index(st.session_state.get("tone", preset["tone"])) if st.session_state.get("tone", preset["tone"]) in TONE_OPTIONS else 1)
                output_language = st.selectbox("Output language", LANGUAGE_OPTIONS, index=LANGUAGE_OPTIONS.index(st.session_state.get("output_language", "English")) if st.session_state.get("output_language") in LANGUAGE_OPTIONS else 0)
                copy_framework = st.selectbox("Copywriting framework", COPY_FRAMEWORKS, index=COPY_FRAMEWORKS.index(st.session_state.get("copy_framework", preset["copy_framework"])) if st.session_state.get("copy_framework", preset["copy_framework"]) in COPY_FRAMEWORKS else 0)
                scene_template = st.selectbox("Scene template", scene_keys, format_func=lambda key: SCENE_TEMPLATES[key]["title"], index=scene_keys.index(scene_template_value) if scene_template_value in SCENE_TEMPLATES else 0, disabled=use_campaign_preset)
                st.caption(SCENE_TEMPLATES[scene_template]["description"])
                background_style = st.text_input("Background style", value=background_style_value, disabled=use_campaign_preset)
                lighting_style = st.text_input("Lighting style", value=lighting_style_value, disabled=use_campaign_preset)
                camera_angle = st.text_input("Camera angle", value=camera_angle_value, disabled=use_campaign_preset)
                surface_environment = st.text_input("Surface / environment", value=surface_environment_value, disabled=use_campaign_preset)
                props_include = st.text_input("Props to include", value=props_include_value, disabled=use_campaign_preset)
                props_avoid = st.text_input("Props to avoid", value=props_avoid_value, disabled=use_campaign_preset)
                color_palette = st.text_input("Color palette", value=color_palette_value, disabled=use_campaign_preset)
                mood = st.text_input("Mood", value=mood_value, disabled=use_campaign_preset)
                aspect_ratio = st.selectbox("Aspect ratio", ASPECT_RATIOS, index=ASPECT_RATIOS.index(aspect_ratio_value) if aspect_ratio_value in ASPECT_RATIOS else 1, disabled=use_campaign_preset)
                image_style = st.text_input("Image style", value=image_style_value, disabled=use_campaign_preset)
                identity_preservation = st.selectbox("Identity preservation level", IDENTITY_LEVELS, index=IDENTITY_LEVELS.index(identity_preservation_value) if identity_preservation_value in IDENTITY_LEVELS else 1, disabled=use_campaign_preset)
                negative_prompt = st.text_area(
                    "Negative prompt / things to avoid",
                    value=st.session_state.get("negative_prompt", "No fake logos, no new text, no watermark, no people or hands unless explicitly requested, no duplicate product, no added scratches, no added damage, no misleading packaging, no object covering the product, no change to product condition."),
                    height=92,
                )

            with st.expander("Advanced Custom Prompt", expanded=False):
                custom_scene_prompt = st.text_area(
                    "Custom scene prompt",
                    value=st.session_state.get("custom_scene_prompt", ""),
                    height=140,
                    placeholder="Describe how you want the scene to change: background, lighting, props, camera angle, display style, and mood.",
                    help="This instruction is optional and always stays below the product identity lock.",
                    key="custom_scene_prompt",
                )

        with preview_col:
            st.markdown("### Your chosen preset")
            preset = preset_defaults(st.session_state.get("campaign_preset", "luxury_instagram"))
            st.markdown(f"**{preset['label']}**")
            st.caption(preset["description"])
            st.caption("Mode: Guided preset" if st.session_state.get("use_campaign_preset", True) else "Mode: Custom scene")
            if use_campaign_preset:
                st.info("Scene controls are locked to the preset values above.")
            num_variants = st.selectbox("Number of variants", [1, 2, 3, 4], index=[1, 2, 3, 4].index(st.session_state.get("num_variants", 3)) if st.session_state.get("num_variants", 3) in [1, 2, 3, 4] else 2, help="Generate between 1 and 4 options for comparison.")
            st.write(
                f"Platform: {preset['platform']}\n\n"
                f"Objective: {preset['campaign_objective']}\n\n"
                f"Tone: {preset['tone']}\n\n"
                f"Scene: {SCENE_TEMPLATES[preset['scene_template']]['title']}"
            )
            st.markdown("### 3. Generate")
            submit = st.form_submit_button("Generate Marketing Asset", type="primary", use_container_width=True)

    scene = SCENE_TEMPLATES[scene_template]

    if not submit and st.session_state.get("latest_result"):
        render_generation_result(st.session_state["latest_result"])
        return
    if not submit:
        return

    inputs = {
        "product_name": product_name,
        "brand_name": brand_name,
        "product_category": product_category,
        "product_condition": product_condition,
        "key_product_facts": key_product_facts,
        "price": price,
        "offer": offer,
        "platform": platform,
        "campaign_objective": campaign_objective,
        "funnel_stage": funnel_stage,
        "target_audience": target_audience,
        "tone": tone,
        "output_language": output_language,
        "copy_framework": copy_framework,
        "scene_template": scene_template,
        "background_style": background_style,
        "lighting_style": lighting_style,
        "camera_angle": camera_angle,
        "surface_environment": surface_environment,
        "props_include": props_include,
        "props_avoid": props_avoid,
        "color_palette": color_palette,
        "mood": mood,
        "aspect_ratio": aspect_ratio,
        "image_style": image_style,
        "identity_preservation": identity_preservation,
        "negative_prompt": negative_prompt,
        "use_campaign_preset": use_campaign_preset,
        "custom_scene_prompt": custom_scene_prompt,
        "reference_usage": reference_usage,
        "reference_photo_present": bool(reference_image),
        "num_variants": num_variants,
    }
    payload_parts = build_campaign_payload(inputs)
    st.session_state["campaign_preset"] = st.session_state.get("campaign_preset", "luxury_instagram")
    st.session_state["num_variants"] = num_variants

    if st.session_state.get("demo_mode"):
        progress = st.status("Preparing campaign brief", expanded=True)
        progress.write("Building prompt controls")
        progress.write("Generating visual and copy")
        progress.write("Checking quality and safety")
        reference_bytes = reference_image.getvalue() if reference_image else None
        result = build_demo_result(inputs, product_image.getvalue() if product_image else None, reference_bytes)
        st.session_state["latest_result"] = result
        st.session_state.setdefault("demo_assets", []).insert(
            0,
            {
                "id": result["id"],
                "product_name": product_name,
                "campaign_name": st.session_state.get("campaign_name_input") or f"{brand_name or 'Campaign'} | {scene['title']}",
                "brand_name": brand_name,
                "platform": platform,
                "marketing_objective": campaign_objective.lower(),
                "funnel_stage": funnel_stage.lower(),
                "status": "generated",
                "best_image_path": result["best_image_path"],
                "product_image_path": None,
                "best_score": result["best_score"],
                "visual_provider_used": result["visual_provider_used"],
                "llm_provider_used": result["llm_provider_used"],
                "quality_report": result["quality_report"],
                "channel_outputs": result["channel_outputs"],
                "hashtags": result["hashtags"],
                "reviewer_note": "",
                "created_at": None,
                "updated_at": None,
                "review_checklist": result["review_checklist"],
                "claim_safety": result["claim_safety"],
                "reference_image_path": result.get("reference_image_path"),
                "reference_usage": result.get("reference_usage"),
                "source": "demo",
            },
        )
        progress.update(label="Generation complete", state="complete")
        render_generation_result(result)
        st.success("Demo asset created. Open Review to inspect and approve it.")
        return

    if not product_image:
        st.error("Please upload a product image before generating.")
        return

    files = {"product_image": (product_image.name, product_image.getvalue(), product_image.type)}
    if reference_image:
        files["reference_image"] = (reference_image.name, reference_image.getvalue(), reference_image.type)
    data = {
        "product_name": product_name,
        "campaign_name": st.session_state.get("campaign_name_input") or f"{brand_name or 'Campaign'} | {scene['title']}",
        "campaign_preset": st.session_state.get("campaign_preset"),
        "brand_name": brand_name,
        "product_condition": product_condition,
        "key_product_facts": key_product_facts,
        "target_audience": target_audience,
        "customer_persona": "",
        "platform": platform,
        "marketing_objective": campaign_objective.lower(),
        "funnel_stage": funnel_stage.lower(),
        "copy_framework": copy_framework,
        "selling_points": key_product_facts,
        "price": price,
        "offer": offer,
        "language": output_language,
        "compliance_notes": json.dumps(payload_parts["claim_safety"], ensure_ascii=False),
        "scene_direction": json.dumps(payload_parts["scene"], ensure_ascii=False),
        "identity_preservation": identity_preservation,
        "claim_safety": json.dumps(payload_parts["claim_safety"], ensure_ascii=False),
        "use_campaign_preset": str(use_campaign_preset).lower(),
        "custom_scene_prompt": custom_scene_prompt,
        "reference_usage": ", ".join(reference_usage) if reference_usage else "Overall composition",
        "campaign_brief_json": json.dumps(payload_parts["campaign_brief"], ensure_ascii=False),
        "prompt_controls_json": json.dumps(payload_parts["prompt_controls"], ensure_ascii=False),
        "review_checklist_json": json.dumps(payload_parts["review_checklist"], ensure_ascii=False),
        "visual_prompt": payload_parts["visual_prompt"],
        "content_prompt": payload_parts["content_prompt"],
        "tone": tone,
        "num_variants": num_variants,
    }

    try:
        progress = st.status("Preparing campaign brief", expanded=True)
        progress.write("Building prompt controls")
        progress.write("Generating visual and copy")
        progress.write("Checking quality and safety")
        with st.spinner("Generating campaign asset..."):
            response = api_post_generation(files=files, data=data)
        if response.status_code != 200:
            raise requests.HTTPError(response.text, response=response)
        result = normalize_backend_result(response.json())
        st.session_state["latest_result"] = result
        progress.update(label="Generation complete", state="complete")
        render_generation_result(result)
        st.success("Asset generated. Send it to Review when ready.")
    except Exception as exc:
        st.warning(f"Live generation failed, so a demo fallback was created instead: {exc}")
        progress.update(label="Live generation failed, using demo fallback", state="error")
        result = build_demo_result(inputs, product_image.getvalue() if product_image else None, reference_image.getvalue() if reference_image else None)
        st.session_state["latest_result"] = result
        render_generation_result(result)


def update_demo_review(asset_id: str, payload: dict) -> dict:
    assets = st.session_state.get("demo_assets", [])
    for asset in assets:
        if asset.get("id") == asset_id:
            asset.update(payload)
            return asset
    return payload


def render_review_tab() -> None:
    st.markdown("## Review")
    st.caption("Compare original and generated assets side by side, then approve, revise, or reject.")
    assets = safe_assets_by_status(None)
    if not assets:
        st.info("No assets found yet.")
        return

    asset_lookup = {asset.get("id"): asset for asset in assets if asset.get("id")}
    asset_ids = [asset.get("id") for asset in assets if asset.get("id")]
    default_asset_id = st.session_state.get("selected_review_asset_id") or asset_ids[0]
    selected_asset_id = st.selectbox(
        "Select asset",
        asset_ids,
        index=asset_ids.index(default_asset_id) if default_asset_id in asset_ids else 0,
        format_func=lambda asset_id: asset_lookup.get(asset_id, {}).get("campaign_name") or asset_lookup.get(asset_id, {}).get("product_name") or asset_id,
    )
    selected = asset_lookup[selected_asset_id]
    st.session_state["selected_review_asset_id"] = selected_asset_id

    score = asset_effective_score(selected)
    variants = selected.get("variants") or []
    if len(variants) > 1 and not selected.get("selected_variant_id"):
        st.warning("Select a variant in Studio before sending this campaign to Review.")
        return

    col_left, col_right = st.columns(2, gap="large")
    with col_left:
        st.markdown("**Original Product Photo**")
        if selected.get("product_image_path"):
            st.image(file_url(selected["product_image_path"]), use_container_width=True)
        else:
            st.info("No stored original image for this asset.")
    with col_right:
        st.markdown("**Selected Generated Variant**")
        selected_image = selected_variant_image_path(selected)
        if selected_image:
            st.image(file_url(selected_image), use_container_width=True)
        else:
            st.info("No selected generated variant available.")

    if selected.get("reference_image_path"):
        with st.expander("Reference Photo Used", expanded=False):
            st.caption(f"Reference photo was used for: {asset_reference_usage(selected)}")
            st.image(file_url(selected["reference_image_path"]), use_container_width=True)

    st.caption(
        f"Selected variant: Variant {selected_variant_number(selected) or 1} | Quality score: {score} / 100 | "
        f"{('Manually selected' if selected.get('selected_variant_id') else 'Recommended')}")

    st.markdown("### Human Review Checklist")
    checklist_cols = st.columns(2)
    checklist_state: dict[str, bool] = {}
    existing_checklist = selected.get("review_checklist") or {}
    for index, label in enumerate(REVIEW_CHECKLIST):
        with checklist_cols[index % 2]:
            checklist_state[label] = st.checkbox(label, value=bool(existing_checklist.get(label, False)), key=f"review_{selected_asset_id}_{index}")

    with st.form(f"review_form_{selected_asset_id}"):
        identity_confirmed = st.checkbox(
            "I confirmed the product identity against the original image",
            value=bool(
                existing_checklist.get("Product identity preserved", False)
                and existing_checklist.get("Color/material unchanged", False)
                and existing_checklist.get("Logo/hardware unchanged", False)
                and existing_checklist.get("Reference photo did not override product identity", False)
            ),
            key=f"identity_confirmed_{selected_asset_id}",
        )
        reviewer_note = st.text_area("Reviewer notes", value=selected.get("reviewer_note") or "", height=100, key=f"reviewer_note_{selected_asset_id}")
        st.metric("Asset score", f"{score} / 100")
        action_cols = st.columns(3)
        approve = action_cols[0].form_submit_button("Approve", type="primary")
        revision = action_cols[1].form_submit_button("Request revision")
        reject = action_cols[2].form_submit_button("Reject")

    if approve or revision or reject:
        next_status = "approved" if approve else "needs_revision" if revision else "rejected"
        if approve and not identity_confirmed:
            st.error("To approve this asset, confirm that you checked the generated visual against the original product image.")
            return
        payload = {
            "status": next_status,
            "identity_verified": bool(identity_confirmed),
            "reviewer_note": reviewer_note,
            "review_checklist": checklist_state,
            "description": selected.get("description"),
            "caption": selected.get("caption"),
            "hashtags": selected.get("hashtags") or [],
            "channel_outputs": selected.get("channel_outputs") or {},
            "selected_variant_id": selected.get("selected_variant_id") or selected.get("best_variant_id"),
        }
        try:
            if st.session_state.get("demo_mode"):
                update_demo_review(selected_asset_id, {"status": next_status, "reviewer_note": reviewer_note, "review_checklist": checklist_state})
                st.success("Demo review saved.")
            else:
                api_patch(f"/assets/{selected_asset_id}/review", payload)
                st.success("Review saved.")
            st.rerun()
        except Exception as exc:
            st.error(f"Could not save review: {exc}")

    if selected.get("status") in {"approved", "exported"} and not st.session_state.get("demo_mode"):
        st.link_button("Export campaign package", f"{API_URL}/assets/{selected_asset_id}/export", use_container_width=True)
    elif selected.get("status") in {"approved", "exported"}:
        st.caption("Demo mode does not create downloadable export packages.")

    with st.expander("Copy and claim-safety review", expanded=False):
        render_copy_section(selected.get("channel_outputs") or {}, key_prefix=f"review_{selected_asset_id}")


def render_library_tab() -> None:
    st.markdown("## Library")
    assets = safe_assets()
    if not assets:
        st.info("Campaign assets will appear here after generation.")
        return

    counts = Counter(asset.get("status") for asset in assets)
    metric_cols = st.columns(4)
    metric_cols[0].metric("Campaigns", len(assets))
    metric_cols[1].metric("Approved", counts.get("approved", 0))
    metric_cols[2].metric("Pending review", counts.get("pending_review", 0) + counts.get("generated", 0))
    metric_cols[3].metric("Exported", counts.get("exported", 0))

    cards = st.columns(2)
    for index, asset in enumerate(assets):
        with cards[index % 2]:
            score = asset_effective_score(asset)
            variant_count = asset_variant_count(asset)
            with st.container(border=True):
                if selected_variant_image_path(asset):
                    st.image(file_url(selected_variant_image_path(asset)), use_container_width=True)
                st.markdown(f"### {asset.get('campaign_name') or asset.get('product_name') or 'Untitled campaign'}")
                st.caption(f"{asset.get('platform') or 'Platform not set'} | {asset.get('marketing_objective') or 'Objective not set'}")
                st.caption(f"Campaign preset: {asset.get('campaign_preset') or 'Not set'}")
                st.caption(f"Selected variant: Variant {selected_variant_number(asset) or 1} of {variant_count or 1}")
                st.caption(f"Quality score: {score} / 100")
                st.caption(f"Review status: {asset.get('status') or 'unknown'}")
                st.caption(f"Export status: {'Exported' if asset.get('exported_at') else 'Not exported'}")
                if asset.get("reference_image_path"):
                    st.caption(f"Reference-guided | {asset_reference_usage(asset)}")
                st.caption(f"Created: {format_timestamp(asset.get('created_at'))}")
                if asset.get("id"):
                    if st.button("Open in Review", key=f"review_open_{asset['id']}"):
                        st.session_state["selected_review_asset_id"] = asset["id"]
                        st.rerun()
                        st.switch_to_query_params(tab="Review")
                        st.rerun()
                    if not st.session_state.get("demo_mode") and asset.get("status") in {"approved", "exported"}:
                        st.link_button("Export", f"{API_URL}/assets/{asset['id']}/export")
                with st.expander("View all generated variants", expanded=False):
                    for variant_index, variant in enumerate(asset.get("variants") or [], start=1):
                        st.caption(
                            f"Variant {variant_index} | {variant.get('quality_status') or variant_quality_status(variant_score_value(variant))} | {variant_direction_label(variant)}"
                        )
                        if variant.get("image_path"):
                            st.image(file_url(variant["image_path"]), use_container_width=True)

    with st.expander("Admin Debug View", expanded=False):
        st.dataframe(
            [
                {
                    "campaign": asset.get("campaign_name"),
                    "status": asset.get("status"),
                    "platform": asset.get("platform"),
                    "objective": asset.get("marketing_objective"),
                    "selected_variant": selected_variant_number(asset),
                    "variant_count": asset_variant_count(asset),
                    "score": asset_effective_score(asset),
                    "created_at": asset.get("created_at"),
                }
                for asset in assets
            ],
            use_container_width=True,
            hide_index=True,
        )


def render_evaluation_tab() -> None:
    st.markdown("## Evaluation")
    st.caption("A graduation-demo view of how well the assisted workflow is performing.")

    assets = safe_assets()
    counts = Counter(asset.get("status") for asset in assets)
    score_values = [asset_effective_score(asset) for asset in assets]
    variant_counts = [asset_variant_count(asset) for asset in assets]
    selected_assets = [asset for asset in assets if asset.get("selected_variant_id") or asset_variant_count(asset) <= 1]
    selected_scores = [asset_effective_score(asset) for asset in selected_assets]
    recommended_selected = sum(1 for asset in selected_assets if asset.get("selected_variant_id") and asset.get("selected_variant_id") == asset.get("best_variant_id"))
    average_score = round(sum(score_values) / len(score_values), 1) if score_values else 0.0
    publishable = counts.get("approved", 0) + counts.get("exported", 0)
    publishable_rate = round((publishable / len(assets)) * 100, 1) if assets else 0.0
    total_variants = sum(variant_counts)
    average_variants = round(total_variants / len(assets), 1) if assets else 0.0
    selected_average_score = round(sum(selected_scores) / len(selected_scores), 1) if selected_scores else 0.0
    recommended_selected_rate = round((recommended_selected / len(selected_assets)) * 100, 1) if selected_assets else 0.0
    approved_selected = sum(1 for asset in selected_assets if asset.get("status") == "approved")
    rejected_selected = sum(1 for asset in selected_assets if asset.get("status") == "rejected")
    most_common_issue = "Human review required" if assets else "No assets yet"
    for asset in assets:
        if asset.get("status") == "rejected":
            most_common_issue = "Rejected in human review"
            break
        if asset.get("status") == "needs_revision":
            most_common_issue = "Revision requested"

    metric_cols = st.columns(6)
    metric_cols[0].metric("Total campaigns generated", len(assets))
    metric_cols[1].metric("Total variants generated", total_variants)
    metric_cols[2].metric("Average variants per campaign", f"{average_variants}")
    metric_cols[3].metric("Selected variant average score", f"{selected_average_score} / 100")
    metric_cols[4].metric("Recommended variant selected rate", f"{recommended_selected_rate}%")
    metric_cols[5].metric("Approved selected variants", approved_selected)

    metric_cols_2 = st.columns(3)
    metric_cols_2[0].metric("Rejected selected variants", rejected_selected)
    metric_cols_2[1].metric("Exported packages", counts.get("exported", 0))
    metric_cols_2[2].metric("Average quality score", f"{average_score} / 100")

    st.metric("Publishable rate", f"{publishable_rate}%")
    st.metric("Most common issue", most_common_issue)
    st.info("The system generates multiple creative variants to support marketing decision-making. Users compare alternatives and manually select the most suitable asset before human review and export.")

    if assets:
        st.markdown("### Status distribution")
        st.bar_chart(dict(counts))
        st.markdown("### Score distribution")
        st.bar_chart({asset.get('campaign_name') or asset.get('product_name') or asset.get('id'): asset_effective_score(asset) for asset in assets})

    with st.expander("Evaluation notes", expanded=False):
        st.write("Human review, product fidelity, and claim safety remain the key decision points.")
        st.write("Demo mode uses mock results so the graduation presentation remains stable without external services.")


def render_about_tab() -> None:
    st.markdown("## Documentation / About")
    st.write("This workspace implements an AI-assisted campaign production flow for product promotion.")
    st.markdown("- Pick a campaign preset\n- Upload a product image\n- Generate visual and copy assets\n- Review and approve manually\n- Export a campaign package\n- Evaluate the workflow")
    st.markdown("### Included documentation")
    st.write("- README.md")
    st.write("- docs/evaluation_framework.md")
    st.write("- docs/update_summary.md")
    st.caption("Human review remains required for product identity and claim safety.")


def main() -> None:
    st.set_page_config(page_title="AI Marketing Asset Creation System", page_icon=":material/campaign:", layout="wide")
    st.markdown(
        """
        <style>
        .stApp {background: linear-gradient(180deg, #f6f1ea 0%, #faf8f4 100%); color: #1e201d;}
        .block-container {max-width: 1320px; padding-top: 1.4rem; padding-bottom: 2rem;}
        [data-testid="stSidebar"] {background: #f0ebe4; border-right: 1px solid #e4dccf;}
        .hero-shell {padding: 0.4rem 0 1.1rem 0;}
        .eyebrow {text-transform: uppercase; letter-spacing: .18em; font-size: .74rem; font-weight: 700; color: #7d6c54; margin-bottom: .8rem;}
        .hero-title {font-size: 2.75rem; line-height: 1.05; font-weight: 760; letter-spacing: -.05em; max-width: 900px; margin-bottom: .7rem;}
        .hero-subtitle {font-size: 1.02rem; color: #63594d; max-width: 900px;}
        div[data-testid="stMetric"] {background: #ffffff; border: 1px solid #eadfd1; padding: 0.8rem 0.9rem; border-radius: 16px;}
        div[data-testid="stForm"] {background: #fffdf9; border: 1px solid #eadfd1; border-radius: 22px; padding: 1rem 1.1rem;}
        div[data-testid="stTabs"] button {font-weight: 650; letter-spacing: .01em;}
        .stButton > button[kind="primary"], div[data-testid="stFormSubmitButton"] button[kind="primary"] {border-radius: 999px; min-height: 3rem; font-weight: 700; background: #1e5a43; border-color: #1e5a43;}
        .stButton > button, div[data-testid="stFormSubmitButton"] button {border-radius: 999px;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    init_state()
    render_header()
    render_sidebar()

    tab_studio, tab_review, tab_library, tab_evaluation, tab_about = st.tabs(["Studio", "Review", "Library", "Evaluation", "Documentation / About"])
    with tab_studio:
        render_studio_tab()
    with tab_review:
        render_review_tab()
    with tab_library:
        render_library_tab()
    with tab_evaluation:
        render_evaluation_tab()
    with tab_about:
        render_about_tab()


if __name__ == "__main__":
    main()