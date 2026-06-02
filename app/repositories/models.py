from sqlalchemy import Column, String, Text, DateTime, Float, ForeignKey
from datetime import datetime
from app.database import Base


class Asset(Base):
    __tablename__ = "assets"

    id = Column(String, primary_key=True, index=True)
    product_name = Column(String, nullable=True)
    campaign_name = Column(String, nullable=True)
    brand_name = Column(String, nullable=True)
    product_condition = Column(Text, nullable=True)
    key_product_facts = Column(Text, nullable=True)
    target_audience = Column(Text, nullable=True)
    customer_persona = Column(Text, nullable=True)
    platform = Column(String, nullable=True)
    marketing_objective = Column(String, nullable=True)
    funnel_stage = Column(String, nullable=True)
    copy_framework = Column(String, nullable=True)
    selling_points = Column(Text, nullable=True)
    price = Column(String, nullable=True)
    offer = Column(String, nullable=True)
    language = Column(String, nullable=True)
    compliance_notes = Column(Text, nullable=True)
    scene_direction = Column(Text, nullable=True)
    identity_preservation = Column(Text, nullable=True)
    claim_safety = Column(Text, nullable=True)
    campaign_brief_json = Column(Text, nullable=True)
    prompt_controls_json = Column(Text, nullable=True)
    review_checklist_json = Column(Text, nullable=True)

    status = Column(String, index=True, default="pending_review")

    product_image_path = Column(Text, nullable=False)
    reference_image_path = Column(Text, nullable=True)
    best_image_path = Column(Text, nullable=True)
    selected_variant_id = Column(String, nullable=True)
    variants_json = Column(Text, nullable=True)

    best_variant_id = Column(String, nullable=True)
    best_score = Column(Float, nullable=True)

    visual_provider_used = Column(String, nullable=True)
    llm_provider_used = Column(String, nullable=True)

    visual_prompt = Column(Text, nullable=True)
    content_prompt = Column(Text, nullable=True)
    tone = Column(Text, nullable=True)

    description = Column(Text, nullable=True)
    caption = Column(Text, nullable=True)
    hashtags = Column(Text, nullable=True)
    channel_outputs_json = Column(Text, nullable=True)
    quality_report_json = Column(Text, nullable=True)

    reviewer_note = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    exported_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class AssetEvent(Base):
    __tablename__ = "asset_events"

    id = Column(String, primary_key=True, index=True)
    asset_id = Column(String, ForeignKey("assets.id"), index=True, nullable=False)
    event_type = Column(String, index=True, nullable=False)
    status = Column(String, nullable=True)
    note = Column(Text, nullable=True)
    payload_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
