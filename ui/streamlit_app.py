from collections import Counter
from urllib.parse import quote

import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000"

DEFAULT_VISUAL_PROMPT = """Use the uploaded product image as the exact product identity.
Use the uploaded reference picture as the target composition and visual style.
Keep the same product design, color, logo, collar, sleeves, fabric texture and visible details.
Generate a realistic product marketing photo with natural lighting, shadows, and product focus.
Match the reference image format, camera angle, perspective, lighting, and composition.
Do not add a person. Do not change the product identity. Do not crop out the product."""

DEFAULT_CONTENT_PROMPT = (
    "Create campaign-ready Vietnamese marketing copy for social commerce, ecommerce listing, "
    "and short-form video promotion."
)

CAMPAIGN_TEMPLATES = {
    "Luxury Handbag Resale": {
        "campaign_name": "Quiet Luxury Handbag Drop",
        "product_name": "Pre-owned Italian Leather Handbag",
        "brand_name": "Atelier Rewear",
        "price": "8,900,000 VND",
        "platform": "Instagram",
        "marketing_objective": "conversion",
        "funnel_stage": "consideration",
        "copy_framework": "AIDA",
        "language": "Vietnamese",
        "tone": "quiet luxury, elegant, trusted, product-selling",
        "offer": "Limited one-piece drop. Private message to reserve.",
        "target_audience": (
            "Women aged 24-38 who like quiet luxury, premium secondhand fashion, "
            "and investment-worthy accessories."
        ),
        "customer_persona": (
            "A young professional who wants a polished everyday handbag, values quality leather, "
            "and prefers curated resale over mass-market fast fashion."
        ),
        "selling_points": (
            "Premium leather texture, timeless silhouette, versatile styling, curated pre-owned value, "
            "limited availability."
        ),
        "compliance_notes": (
            "Do not claim official brand partnership. Be transparent that the item is pre-owned. "
            "Avoid saying flawless unless condition is verified."
        ),
        "visual_prompt": """Use the uploaded product image as the exact handbag identity.
Use the uploaded reference picture as the target luxury composition and visual style.
Preserve the same shape, hardware, stitching, leather texture, color, logo placement, and visible condition details.
Create a realistic premium product photograph on a marble or neutral stone surface with soft window light.
Use subtle shadows, refined styling props, and negative space suitable for a luxury resale campaign.
Do not change the bag identity. Do not add a model. Do not over-polish away real condition details.""",
        "content_prompt": (
            "Create Vietnamese luxury resale copy for Instagram, Facebook, Shopee, and TikTok. "
            "Emphasize craftsmanship, timeless styling, trust, and limited availability."
        ),
    },
    "Luxury Watch Collector Drop": {
        "campaign_name": "Collector Watch Feature",
        "product_name": "Pre-owned Luxury Dress Watch",
        "brand_name": "Timepiece Archive",
        "price": "18,500,000 VND",
        "platform": "Facebook",
        "marketing_objective": "conversion",
        "funnel_stage": "consideration",
        "copy_framework": "FAB",
        "language": "Vietnamese",
        "tone": "refined, trustworthy, collector-focused, premium",
        "offer": "Appointment-based viewing. Serious buyers only.",
        "target_audience": (
            "Collectors and professionals aged 28-45 who value classic watch design, authenticity, "
            "and long-term ownership."
        ),
        "customer_persona": (
            "A finance or business professional looking for a subtle statement watch with strong resale appeal."
        ),
        "selling_points": (
            "Elegant dial, polished case, refined strap, collectible styling, careful product presentation."
        ),
        "compliance_notes": (
            "Do not imply official certification unless documents are available. Avoid investment-return claims."
        ),
        "visual_prompt": """Use the uploaded product image as the exact watch identity.
Preserve the same dial, hands, indices, case shape, strap, crown, and visible condition.
Create a realistic luxury product photograph on dark walnut, slate, or cream leather with controlled studio light.
Show the watch clearly with premium reflections, accurate scale, and elegant shadows.
Do not change brand marks, dial layout, or material finish. Do not add a wrist model.""",
        "content_prompt": (
            "Create Vietnamese collector-focused copy for a luxury watch listing, including trust-building language, "
            "feature-benefit structure, and clear CTA."
        ),
    },
    "Silk Scarf Editorial": {
        "campaign_name": "Silk Scarf Editorial Story",
        "product_name": "Vintage Silk Scarf",
        "brand_name": "Maison Archive",
        "price": "2,400,000 VND",
        "platform": "TikTok",
        "marketing_objective": "engagement",
        "funnel_stage": "awareness",
        "copy_framework": "AIDA",
        "language": "Vietnamese + English",
        "tone": "editorial, graceful, artistic, aspirational",
        "offer": "Drop available this weekend only.",
        "target_audience": (
            "Style-led women aged 20-34 who enjoy vintage luxury, soft accessories, and editorial styling."
        ),
        "customer_persona": (
            "A creative student or young professional who uses accessories to make simple outfits feel distinctive."
        ),
        "selling_points": (
            "Silk texture, vintage pattern, multiple styling use cases, lightweight luxury, giftable item."
        ),
        "compliance_notes": "Do not describe the item as new. Mention vintage/pre-owned condition clearly.",
        "visual_prompt": """Use the uploaded product image as the exact scarf identity.
Preserve the same pattern, color palette, border details, texture, and visible condition.
Create an editorial flat-lay luxury image with the scarf softly folded on a neutral surface.
Use tasteful props such as a perfume bottle, book, or pearl accessory only if they do not cover the scarf.
Keep the textile pattern visible and commercially clear. Do not add a person.""",
        "content_prompt": (
            "Create bilingual Vietnamese and English social content for a vintage silk scarf campaign, "
            "including Instagram caption, TikTok hook, and ecommerce listing copy."
        ),
    },
    "Premium Leather Loafers": {
        "campaign_name": "Premium Leather Loafer Listing",
        "product_name": "Pre-owned Leather Loafers",
        "brand_name": "The Gentle Wardrobe",
        "price": "3,800,000 VND",
        "platform": "Shopee",
        "marketing_objective": "conversion",
        "funnel_stage": "conversion",
        "copy_framework": "PAS",
        "language": "Vietnamese",
        "tone": "classic, practical, premium, trustworthy",
        "offer": "Ready to ship. One pair only.",
        "target_audience": (
            "Men aged 24-40 who need versatile premium shoes for office, smart casual, and weekend outfits."
        ),
        "customer_persona": (
            "A young office worker upgrading his wardrobe with durable leather footwear without paying full retail."
        ),
        "selling_points": (
            "Genuine leather look, timeless loafer shape, office-to-weekend styling, practical resale value."
        ),
        "compliance_notes": "Do not hide creases or wear marks. Describe condition accurately in the listing.",
        "visual_prompt": """Use the uploaded product image as the exact loafer identity.
Preserve the same leather tone, stitching, sole shape, silhouette, creases, and visible condition.
Create a premium ecommerce product photograph on a clean neutral background with natural shadows.
Show both shoes clearly with accurate shape and enough empty space for platform thumbnails.
Do not change color, material, or condition. Do not add a person.""",
        "content_prompt": (
            "Create Vietnamese conversion-focused copy for a Shopee luxury resale listing, including pain-point, "
            "benefit, condition transparency, and CTA."
        ),
    },
}

EVALUATION_RUBRIC = [
    {
        "criterion": "Product identity preservation",
        "weight": 20,
        "excellent": "Logo, material, shape, color, and visible condition remain faithful to the input.",
    },
    {
        "criterion": "Luxury visual quality",
        "weight": 20,
        "excellent": "Lighting, surface, styling, shadows, and composition feel premium and realistic.",
    },
    {
        "criterion": "Marketing message fit",
        "weight": 15,
        "excellent": "Copy matches audience, platform, funnel stage, brand voice, and campaign objective.",
    },
    {
        "criterion": "Commercial readiness",
        "weight": 15,
        "excellent": "Asset can be used for a real listing or social post with minimal editing.",
    },
    {
        "criterion": "Human review usefulness",
        "weight": 10,
        "excellent": "Reviewer can compare variants, edit content, choose best output, and approve clearly.",
    },
    {
        "criterion": "Trust and compliance",
        "weight": 10,
        "excellent": "Claims are transparent, condition is not exaggerated, and no false partnership is implied.",
    },
    {
        "criterion": "System reliability",
        "weight": 10,
        "excellent": "Provider fallback, error handling, storage, export, and audit trail work predictably.",
    },
]

STATUS_OPTIONS = [
    "generated",
    "pending_review",
    "needs_revision",
    "revised",
    "approved",
    "rejected",
    "exported",
    "failed",
]

CHANNEL_FIELDS = [
    ("seo_title", "SEO Title", 80),
    ("product_description", "Product Description", 160),
    ("instagram_caption", "Instagram Caption", 140),
    ("facebook_ad", "Facebook Ad", 130),
    ("tiktok_script", "TikTok Script", 180),
    ("shopee_description", "Shopee Description", 160),
    ("email_subject", "Email Subject", 70),
]


st.set_page_config(
    page_title="AI Product Studio",
    page_icon=":material/campaign:",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.2rem; padding-bottom: 2rem;}
    div[data-testid="stMetric"] {
        background: #f7f7f3;
        border: 1px solid #deded6;
        padding: 0.75rem 0.9rem;
        border-radius: 8px;
    }
    div[data-testid="stTabs"] button {font-weight: 600;}
    .workspace-title {
        font-size: 2rem;
        font-weight: 760;
        letter-spacing: 0;
        margin-bottom: 0.2rem;
    }
    .workspace-subtitle {
        color: #5f6368;
        margin-bottom: 1rem;
    }
    .pill {
        display: inline-block;
        border: 1px solid #d7d7cf;
        border-radius: 999px;
        padding: 0.15rem 0.55rem;
        margin-right: 0.25rem;
        background: #fbfbf8;
        font-size: 0.78rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def api_get(path: str, **params):
    response = requests.get(f"{API_URL}{path}", params=params or None, timeout=20)
    response.raise_for_status()
    return response.json()


def file_url(path: str | None) -> str | None:
    if not path:
        return None
    return f"{API_URL}/files?path={quote(path, safe='')}"


def fetch_assets(status: str | None = None):
    try:
        params = {"status": status} if status else {}
        return api_get("/assets", **params)
    except Exception:
        return []


def post_generation(files, data):
    return requests.post(f"{API_URL}/generate", files=files, data=data, timeout=420)


def patch_review(asset_id: str, payload: dict):
    response = requests.patch(f"{API_URL}/assets/{asset_id}/review", json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def option_index(options: list[str], value: str) -> int:
    return options.index(value) if value in options else 0


def render_header():
    st.markdown('<div class="workspace-title">AI Product Studio</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="workspace-subtitle">Campaign brief, image generation, quality review, content editing, and export in one workspace.</div>',
        unsafe_allow_html=True,
    )


def render_health_sidebar():
    with st.sidebar:
        st.header("Workspace")
        try:
            health = api_get("/health")
            st.success("API online")
            st.caption(health["app"])
            st.write("Visual chain:", health["visual_provider_chain"])
            st.write("LLM chain:", health["llm_provider_chain"])
            st.write("Gemini key:", "loaded" if health["has_gemini_key"] else "not loaded")
            st.write("Replicate key:", "loaded" if health["has_replicate_key"] else "not loaded")
            st.write("Gemini image models:", health.get("gemini_image_model_chain") or health.get("gemini_image_model"))
            for warning in health.get("configuration_warnings", []):
                st.warning(warning)
        except Exception:
            st.error("API offline. Run the backend first.")

        assets = fetch_assets()
        counts = Counter(asset["status"] for asset in assets)
        st.divider()
        st.metric("Assets", len(assets))
        st.metric("Approved", counts.get("approved", 0))
        st.metric("Needs revision", counts.get("needs_revision", 0))


def render_quality_report(report: dict):
    if not report:
        st.info("No quality report available.")
        return

    st.write(report.get("summary", "Quality report generated."))
    scorecard = report.get("scorecard") or {}
    metric_cols = st.columns(3)
    for index, (key, value) in enumerate(scorecard.items()):
        with metric_cols[index % 3]:
            st.metric(key.replace("_", " ").title(), round(value, 4) if isinstance(value, float) else value)

    recommendations = report.get("recommendations") or []
    if recommendations:
        st.write("Recommendations")
        for item in recommendations:
            st.write(f"- {item}")


def render_channel_outputs(channel_outputs: dict):
    if not channel_outputs:
        st.info("No channel content available.")
        return

    tabs = st.tabs(["Listing", "Social", "Video", "CTA"])
    with tabs[0]:
        st.text_area("SEO Title", value=channel_outputs.get("seo_title", ""), height=70, disabled=True)
        st.text_area("Product Description", value=channel_outputs.get("product_description", ""), height=180, disabled=True)
        st.text_area("Shopee Description", value=channel_outputs.get("shopee_description", ""), height=160, disabled=True)
    with tabs[1]:
        st.text_area("Instagram Caption", value=channel_outputs.get("instagram_caption", ""), height=160, disabled=True)
        st.text_area("Facebook Ad", value=channel_outputs.get("facebook_ad", ""), height=140, disabled=True)
        st.write(" ".join(channel_outputs.get("hashtags", [])))
    with tabs[2]:
        st.text_area("TikTok Script", value=channel_outputs.get("tiktok_script", ""), height=220, disabled=True)
    with tabs[3]:
        st.text_area("Email Subject", value=channel_outputs.get("email_subject", ""), height=70, disabled=True)
        for cta in channel_outputs.get("cta_suggestions", []):
            st.markdown(f'<span class="pill">{cta}</span>', unsafe_allow_html=True)


def render_generation_result(result: dict):
    st.success(
        f"Generated with visual provider {result.get('visual_provider_used')} and LLM provider {result.get('llm_provider_used')}"
    )
    if result.get("error_message"):
        st.error(result["error_message"])

    image_col, report_col = st.columns([1.05, 1.2])
    with image_col:
        st.subheader("Selected Asset")
        if result.get("best_image_path"):
            st.image(file_url(result["best_image_path"]), use_container_width=True)
        st.caption(f"Best variant: {result.get('best_variant_id')}")
    with report_col:
        st.subheader("Quality Report")
        render_quality_report(result.get("quality_report") or {})

    st.subheader("Campaign Copy")
    render_channel_outputs(result.get("channel_outputs") or {})

    st.subheader("Variant Comparison")
    variants = result.get("variants") or []
    cols = st.columns(3)
    for index, variant in enumerate(variants):
        with cols[index % 3]:
            label = variant["variant_id"]
            if label == result.get("best_variant_id"):
                label += " - selected"
            st.markdown(f"**{label}**")
            st.caption(f"Provider: {variant.get('provider')}")
            st.image(file_url(variant["image_path"]), use_container_width=True)
            st.json(variant.get("scores", {}))


def render_create_tab():
    st.subheader("Create Campaign")
    template_name = st.selectbox(
        "Campaign Template",
        list(CAMPAIGN_TEMPLATES.keys()),
        help="Choose a luxury-item campaign starter, then adjust any field before generation.",
    )
    template = CAMPAIGN_TEMPLATES[template_name]
    template_key = template_name.lower().replace(" ", "_")

    with st.form("generate_campaign_form"):
        upload_col, brief_col = st.columns([0.95, 1.25])

        with upload_col:
            product_image = st.file_uploader(
                "Product Image",
                type=["jpg", "jpeg", "png", "webp"],
                key="product_image",
            )
            reference_image = st.file_uploader(
                "Reference Image",
                type=["jpg", "jpeg", "png", "webp"],
                key="reference_image",
            )
            num_variants = st.slider("Variants", min_value=1, max_value=6, value=3)
            if product_image:
                st.image(product_image, caption="Product input", use_container_width=True)

        with brief_col:
            c1, c2 = st.columns(2)
            campaign_name = c1.text_input(
                "Campaign Name",
                value=template["campaign_name"],
                key=f"{template_key}_campaign_name",
            )
            product_name = c2.text_input(
                "Product Name",
                value=template["product_name"],
                key=f"{template_key}_product_name",
            )
            brand_name = c1.text_input(
                "Brand / Shop",
                value=template["brand_name"],
                key=f"{template_key}_brand_name",
            )
            price = c2.text_input("Price", value=template["price"], key=f"{template_key}_price")
            platform_options = ["Instagram", "Facebook", "TikTok", "Shopee", "Website"]
            objective_options = ["conversion", "awareness", "engagement", "retention"]
            funnel_options = ["awareness", "consideration", "conversion", "loyalty"]
            framework_options = ["AIDA", "PAS", "FAB", "4P"]
            language_options = ["Vietnamese", "English", "Vietnamese + English"]
            platform = c1.selectbox(
                "Main Platform",
                platform_options,
                index=option_index(platform_options, template["platform"]),
                key=f"{template_key}_platform",
            )
            marketing_objective = c2.selectbox(
                "Objective",
                objective_options,
                index=option_index(objective_options, template["marketing_objective"]),
                key=f"{template_key}_objective",
            )
            funnel_stage = c1.selectbox(
                "Funnel Stage",
                funnel_options,
                index=option_index(funnel_options, template["funnel_stage"]),
                key=f"{template_key}_funnel",
            )
            copy_framework = c2.selectbox(
                "Copy Framework",
                framework_options,
                index=option_index(framework_options, template["copy_framework"]),
                key=f"{template_key}_framework",
            )
            language = c1.selectbox(
                "Output Language",
                language_options,
                index=option_index(language_options, template["language"]),
                key=f"{template_key}_language",
            )
            tone = c2.text_input("Brand Voice", value=template["tone"], key=f"{template_key}_tone")
            offer = st.text_input("Offer / Promotion", value=template["offer"], key=f"{template_key}_offer")

        target_audience = st.text_area(
            "Target Audience",
            value=template["target_audience"],
            height=80,
            key=f"{template_key}_target_audience",
        )
        customer_persona = st.text_area(
            "Customer Persona",
            value=template["customer_persona"],
            height=80,
            key=f"{template_key}_customer_persona",
        )
        selling_points = st.text_area(
            "Selling Points",
            value=template["selling_points"],
            height=80,
            key=f"{template_key}_selling_points",
        )
        compliance_notes = st.text_area(
            "Brand / Compliance Notes",
            value=template["compliance_notes"],
            height=70,
            key=f"{template_key}_compliance_notes",
        )
        visual_prompt = st.text_area(
            "Visual Direction",
            value=template["visual_prompt"],
            height=180,
            key=f"{template_key}_visual_prompt",
        )
        content_prompt = st.text_area(
            "Content Direction",
            value=template["content_prompt"],
            height=90,
            key=f"{template_key}_content_prompt",
        )

        submitted = st.form_submit_button("Generate Campaign Asset", type="primary", use_container_width=True)

    if not submitted:
        return

    if not product_image:
        st.error("Upload a product image before generating.")
        return

    files = {
        "product_image": (
            product_image.name,
            product_image.getvalue(),
            product_image.type,
        )
    }
    if reference_image:
        files["reference_image"] = (
            reference_image.name,
            reference_image.getvalue(),
            reference_image.type,
        )

    data = {
        "campaign_name": campaign_name,
        "product_name": product_name,
        "brand_name": brand_name,
        "target_audience": target_audience,
        "customer_persona": customer_persona,
        "platform": platform,
        "marketing_objective": marketing_objective,
        "funnel_stage": funnel_stage,
        "copy_framework": copy_framework,
        "selling_points": selling_points,
        "price": price,
        "offer": offer,
        "language": language,
        "compliance_notes": compliance_notes,
        "visual_prompt": visual_prompt,
        "content_prompt": content_prompt,
        "tone": tone,
        "num_variants": num_variants,
    }

    with st.spinner("Generating asset, copy, and quality report..."):
        response = post_generation(files=files, data=data)

    if response.status_code != 200:
        st.error(response.text)
        return

    render_generation_result(response.json())


def render_asset_review(asset: dict):
    with st.container(border=True):
        top_cols = st.columns([0.9, 1.45])
        with top_cols[0]:
            if asset.get("best_image_path"):
                st.image(file_url(asset["best_image_path"]), use_container_width=True)
            st.metric("Best Score", round(asset.get("best_score") or 0, 4))
            st.caption(f"Visual: {asset.get('visual_provider_used') or 'unknown'}")
            st.caption(f"LLM: {asset.get('llm_provider_used') or 'unknown'}")

        with top_cols[1]:
            st.markdown(f"### {asset.get('campaign_name') or asset.get('product_name') or 'Untitled Campaign'}")
            st.markdown(
                f'<span class="pill">{asset.get("status")}</span>'
                f'<span class="pill">{asset.get("platform") or "platform not set"}</span>'
                f'<span class="pill">{asset.get("marketing_objective") or "objective not set"}</span>',
                unsafe_allow_html=True,
            )
            st.write(asset.get("caption") or "")
            st.caption(" ".join(asset.get("hashtags") or []))

            with st.expander("Campaign Brief", expanded=False):
                st.write("Product:", asset.get("product_name"))
                st.write("Brand:", asset.get("brand_name"))
                st.write("Audience:", asset.get("target_audience"))
                st.write("Persona:", asset.get("customer_persona"))
                st.write("Selling points:", asset.get("selling_points"))
                st.write("Offer:", asset.get("offer"))

            with st.expander("Quality Report", expanded=False):
                render_quality_report(asset.get("quality_report") or {})

    variants = asset.get("variants") or []
    best_options = [variant["variant_id"] for variant in variants]
    current_best = asset.get("best_variant_id")
    if current_best not in best_options and best_options:
        current_best = best_options[0]

    with st.expander(f"Edit Review - {asset['id']}", expanded=False):
        if variants:
            variant_cols = st.columns(3)
            for index, variant in enumerate(variants):
                with variant_cols[index % 3]:
                    st.caption(f"{variant['variant_id']} | {variant.get('provider')}")
                    st.image(file_url(variant["image_path"]), use_container_width=True)
                    st.write("Final score:", variant.get("scores", {}).get("final_score"))

        channel_outputs = dict(asset.get("channel_outputs") or {})

        with st.form(f"review_form_{asset['id']}"):
            status_index = STATUS_OPTIONS.index(asset["status"]) if asset["status"] in STATUS_OPTIONS else 0
            status = st.selectbox("Workflow Status", STATUS_OPTIONS, index=status_index)
            best_variant_id = st.selectbox(
                "Selected Best Variant",
                best_options or [asset.get("best_variant_id") or ""],
                index=(best_options.index(current_best) if current_best in best_options else 0),
            )
            description = st.text_area("Product Description", value=asset.get("description") or "", height=130)
            caption = st.text_area("Main Caption", value=asset.get("caption") or "", height=120)
            hashtags_text = st.text_input("Hashtags", value=" ".join(asset.get("hashtags") or []))

            st.write("Channel Outputs")
            for field_key, label, height in CHANNEL_FIELDS:
                channel_outputs[field_key] = st.text_area(
                    label,
                    value=str(channel_outputs.get(field_key, "")),
                    height=height,
                    key=f"{asset['id']}_{field_key}",
                )
            ctas = st.text_input(
                "CTA Suggestions",
                value=" | ".join(channel_outputs.get("cta_suggestions", [])),
                key=f"{asset['id']}_ctas",
            )
            channel_outputs["cta_suggestions"] = [item.strip() for item in ctas.split("|") if item.strip()]
            channel_outputs["hashtags"] = [item.strip() for item in hashtags_text.split() if item.strip()]

            reviewer_note = st.text_area(
                "Reviewer Note",
                value=asset.get("reviewer_note") or "",
                height=90,
            )

            action_cols = st.columns(3)
            save_clicked = action_cols[0].form_submit_button("Save Review")
            revision_clicked = action_cols[1].form_submit_button("Needs Revision")
            approve_clicked = action_cols[2].form_submit_button("Approve", type="primary")

        if save_clicked or revision_clicked or approve_clicked:
            next_status = status
            if revision_clicked:
                next_status = "needs_revision"
            if approve_clicked:
                next_status = "approved"

            payload = {
                "status": next_status,
                "reviewer_note": reviewer_note,
                "description": description,
                "caption": caption,
                "hashtags": [item.strip() for item in hashtags_text.split() if item.strip()],
                "channel_outputs": channel_outputs,
                "best_variant_id": best_variant_id,
            }
            try:
                patch_review(asset["id"], payload)
                st.success("Review saved.")
                st.rerun()
            except Exception as exc:
                st.error(f"Review update failed: {exc}")

    event_col, export_col = st.columns([1.3, 1])
    with event_col:
        show_audit = st.toggle("Show Audit Trail", value=False, key=f"audit_{asset['id']}")
        if show_audit:
            try:
                events = api_get(f"/assets/{asset['id']}/events")
                with st.container(border=True):
                    for event in events:
                        st.caption(f"{event['created_at']} - {event['event_type']} - {event.get('status') or ''}")
                        if event.get("note"):
                            st.write(event["note"])
            except Exception:
                st.info("Audit trail unavailable.")
    with export_col:
        st.link_button("Download Campaign ZIP", f"{API_URL}/assets/{asset['id']}/export", use_container_width=True)


def render_review_tab():
    st.subheader("Review Board")
    status_filter = st.selectbox(
        "Filter by status",
        ["all"] + STATUS_OPTIONS,
        index=0,
        key="review_status_filter",
    )
    assets = fetch_assets(None if status_filter == "all" else status_filter)
    if not assets:
        st.info("No assets found for this filter.")
        return

    for asset in assets:
        render_asset_review(asset)


def render_library_tab():
    st.subheader("Asset Library")
    assets = fetch_assets()
    if not assets:
        st.info("No generated assets yet.")
        return

    counts = Counter(asset["status"] for asset in assets)
    metric_cols = st.columns(4)
    metric_cols[0].metric("Total Assets", len(assets))
    metric_cols[1].metric("Generated", counts.get("generated", 0))
    metric_cols[2].metric("Approved", counts.get("approved", 0))
    metric_cols[3].metric("Exported", counts.get("exported", 0))

    rows = []
    for asset in assets:
        rows.append({
            "campaign": asset.get("campaign_name"),
            "product": asset.get("product_name"),
            "status": asset.get("status"),
            "platform": asset.get("platform"),
            "objective": asset.get("marketing_objective"),
            "score": asset.get("best_score"),
            "created_at": asset.get("created_at"),
        })
    st.dataframe(rows, use_container_width=True, hide_index=True)


def render_evaluation_tab():
    st.subheader("Product Evaluation Framework")
    st.write(
        "Use this rubric to evaluate luxury-item campaigns generated by the system. "
        "It is designed for a marketing-major graduation project: product quality, "
        "commercial usability, trust, and human review are all measured."
    )

    rubric_rows = []
    for item in EVALUATION_RUBRIC:
        rubric_rows.append({
            "Criterion": item["criterion"],
            "Weight": f"{item['weight']}%",
            "Excellent Standard": item["excellent"],
        })
    st.dataframe(rubric_rows, use_container_width=True, hide_index=True)

    st.markdown("### Score A Campaign")
    st.caption("Score each dimension from 1 to 5. The final result is weighted to 100 points.")
    total = 0.0
    score_cols = st.columns(2)
    for index, item in enumerate(EVALUATION_RUBRIC):
        with score_cols[index % 2]:
            score = st.slider(
                item["criterion"],
                min_value=1,
                max_value=5,
                value=4,
                key=f"eval_{item['criterion']}",
            )
            total += (score / 5) * item["weight"]

    st.metric("Weighted Evaluation Score", f"{total:.1f} / 100")

    if total >= 85:
        st.success("Evaluation result: production-ready candidate.")
    elif total >= 70:
        st.info("Evaluation result: strong prototype, needs targeted improvement.")
    else:
        st.warning("Evaluation result: needs revision before real campaign use.")

    st.markdown("### Suggested Study Design")
    st.write("- Test at least 3 luxury product categories: handbag, watch, and scarf or shoes.")
    st.write("- Generate 3 variants per product and ask reviewers to choose the strongest asset.")
    st.write("- Compare raw product image vs AI-generated campaign asset for perceived quality and purchase intent.")
    st.write("- Collect reviewer scores for visual quality, trust, copy relevance, and readiness to publish.")
    st.write("- Report average score, best-variant selection rate, revision rate, and approval rate.")


render_header()
render_health_sidebar()

tab_create, tab_review, tab_library, tab_evaluation = st.tabs(
    ["Create Campaign", "Review Board", "Asset Library", "Evaluation"]
)

with tab_create:
    render_create_tab()

with tab_review:
    render_review_tab()

with tab_library:
    render_library_tab()

with tab_evaluation:
    render_evaluation_tab()
