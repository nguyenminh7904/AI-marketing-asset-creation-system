from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class GenerationRequest(BaseModel):
    product_name: Optional[str] = None
    campaign_name: Optional[str] = None
    campaign_preset: Optional[str] = None
    brand_name: Optional[str] = None
    product_condition: Optional[str] = None
    key_product_facts: Optional[str] = None
    target_audience: Optional[str] = None
    customer_persona: Optional[str] = None
    platform: str = "Instagram"
    marketing_objective: str = "conversion"
    funnel_stage: str = "consideration"
    copy_framework: str = "AIDA"
    selling_points: Optional[str] = None
    price: Optional[str] = None
    offer: Optional[str] = None
    language: str = "Vietnamese"
    compliance_notes: Optional[str] = None
    scene_direction: Optional[str] = None
    identity_preservation: Optional[str] = None
    claim_safety: Optional[str] = None
    use_campaign_preset: bool = True
    custom_scene_prompt: Optional[str] = None
    reference_usage: Optional[str] = None
    visual_provider_chain: Optional[str] = None
    visual_prompt: str
    content_prompt: str
    tone: str = "premium, emotional, product-selling"
    num_variants: int = Field(default=3, ge=1, le=4)


class VariantResult(BaseModel):
    variant_id: str
    image_path: str
    provider: str
    scores: Dict[str, float]
    technical_diagnostics: Dict[str, Any] = Field(default_factory=dict)
    variant_direction: Optional[str] = None
    quality_status: Optional[str] = None
    notes: List[str] = Field(default_factory=list)
    display_score: Optional[int] = None
    is_recommended: bool = False
    is_selected: bool = False


class GenerationResult(BaseModel):
    asset_id: str
    status: str
    product_image_path: str
    reference_image_path: Optional[str] = None
    campaign_preset: Optional[str] = None
    reference_usage: Optional[str] = None
    custom_scene_prompt: Optional[str] = None
    use_campaign_preset: Optional[bool] = None
    best_image_path: str
    variants: List[VariantResult]
    best_variant_id: str
    recommended_variant_id: Optional[str] = None
    selected_variant_id: Optional[str] = None
    visual_provider_used: str
    llm_provider_used: str
    description: str
    caption: str
    hashtags: List[str]
    channel_outputs: Dict[str, Any] = Field(default_factory=dict)
    quality_report: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None


class ReviewRequest(BaseModel):
    status: str
    identity_verified: bool = False
    reviewer_note: Optional[str] = None
    review_checklist: Optional[Dict[str, bool]] = None
    description: Optional[str] = None
    caption: Optional[str] = None
    hashtags: Optional[List[str]] = None
    channel_outputs: Optional[Dict[str, Any]] = None
    best_variant_id: Optional[str] = None
    selected_variant_id: Optional[str] = None


class VariantSelectionRequest(BaseModel):
    selected_variant_id: str


class ImageEvaluationRequest(BaseModel):
    compared_with_original: bool = False
    product_fidelity: int = Field(ge=1, le=5)
    scene_quality: int = Field(ge=1, le=5)
    photorealism: int = Field(ge=1, le=5)
    prompt_adherence: int = Field(ge=1, le=5)
    publish_readiness: int = Field(ge=1, le=5)
    failure_modes: List[str] = Field(default_factory=list)
    reviewer_comment: Optional[str] = None
