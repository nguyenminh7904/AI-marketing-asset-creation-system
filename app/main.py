import json
import re
from collections import Counter
from io import BytesIO
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from PIL import Image, ImageDraw, ImageFont

from app.config import settings
from app.logging_config import setup_logging
from app.database import get_db, init_db
from app.core.schemas import GenerationRequest, ImageEvaluationRequest, ReviewRequest, VariantSelectionRequest
from app.core.status import APPROVED, EXPORTED, REVIEW_STATUSES
from app.core.pipeline import ProductPromotionPipeline
from app.repositories.asset_repository import AssetRepository
from app.services.export_service import ExportService


logger = setup_logging()
app = FastAPI(title=settings.APP_NAME)

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
IMAGE_EVALUATION_WEIGHTS = {
    "product_fidelity": 40,
    "scene_quality": 20,
    "photorealism": 15,
    "prompt_adherence": 10,
    "publish_readiness": 15,
}
IMAGE_FAILURE_MODES = {
    "introduced_damage_or_wear",
    "changed_logo_or_text",
    "changed_color_or_material",
    "altered_shape_or_hardware",
    "product_obscured_or_cropped",
    "unrealistic_scene_or_shadow",
    "scene_does_not_match_request",
}
IDENTITY_FAILURE_MODES = {
    "introduced_damage_or_wear",
    "changed_logo_or_text",
    "changed_color_or_material",
    "altered_shape_or_hardware",
    "product_obscured_or_cropped",
}


@app.on_event("startup")
def startup():
    init_db()
    logger.info("Application started")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "visual_provider_chain": settings.VISUAL_PROVIDER_CHAIN,
        "llm_provider_chain": settings.LLM_PROVIDER_CHAIN,
        "has_cloudflare_credentials": bool(settings.CLOUDFLARE_ACCOUNT_ID and settings.CLOUDFLARE_API_TOKEN),
        "has_gemini_key": bool(settings.GEMINI_API_KEY),
        "has_replicate_key": bool(settings.REPLICATE_API_TOKEN),
        "cloudflare_image_model": settings.CLOUDFLARE_IMAGE_MODEL,
        "cloudflare_inpaint_model": settings.CLOUDFLARE_INPAINT_MODEL,
        "cloudflare_image_size": f"{settings.CLOUDFLARE_IMAGE_WIDTH}x{settings.CLOUDFLARE_IMAGE_HEIGHT}",
        "google_imagen_model": settings.GOOGLE_IMAGEN_MODEL,
        "google_imagen_aspect_ratio": settings.GOOGLE_IMAGEN_ASPECT_RATIO,
        "replicate_flux_model_chain": settings.REPLICATE_FLUX_MODEL_CHAIN,
        "replicate_flux_reference_model_chain": settings.REPLICATE_FLUX_REFERENCE_MODEL_CHAIN,
        "replicate_flux_aspect_ratio": settings.REPLICATE_FLUX_ASPECT_RATIO,
        "gemini_text_model": settings.GEMINI_TEXT_MODEL,
        "gemini_text_model_chain": settings.GEMINI_TEXT_MODEL_CHAIN,
        "max_upload_mb": settings.MAX_UPLOAD_MB,
        "configuration_warnings": _configuration_warnings(),
    }


@app.post("/generate")
async def generate_asset(
    product_image: UploadFile = File(...),
    reference_image: UploadFile | None = File(None),
    product_name: str | None = Form(None),
    campaign_name: str | None = Form(None),
    campaign_preset: str | None = Form(None),
    brand_name: str | None = Form(None),
    product_condition: str | None = Form(None),
    key_product_facts: str | None = Form(None),
    target_audience: str | None = Form(None),
    customer_persona: str | None = Form(None),
    platform: str = Form("Instagram"),
    marketing_objective: str = Form("conversion"),
    funnel_stage: str = Form("consideration"),
    copy_framework: str = Form("AIDA"),
    selling_points: str | None = Form(None),
    price: str | None = Form(None),
    offer: str | None = Form(None),
    language: str = Form("Vietnamese"),
    compliance_notes: str | None = Form(None),
    scene_direction: str | None = Form(None),
    identity_preservation: str | None = Form(None),
    claim_safety: str | None = Form(None),
    use_campaign_preset: bool = Form(True),
    custom_scene_prompt: str | None = Form(None),
    reference_usage: str | None = Form(None),
    visual_provider_chain: str | None = Form(None),
    campaign_brief_json: str | None = Form(None),
    prompt_controls_json: str | None = Form(None),
    review_checklist_json: str | None = Form(None),
    visual_prompt: str = Form(...),
    content_prompt: str = Form(...),
    tone: str = Form("premium, emotional, product-selling"),
    num_variants: int = Form(2),
    db: Session = Depends(get_db),
):
    product_path = _save_upload(product_image, "product")

    reference_path = None
    if reference_image and reference_image.filename:
        reference_path = str(_save_upload(reference_image, "reference"))

    request = GenerationRequest(
        product_name=product_name,
        campaign_name=campaign_name,
        campaign_preset=campaign_preset,
        brand_name=brand_name,
        product_condition=product_condition,
        key_product_facts=key_product_facts,
        target_audience=target_audience,
        customer_persona=customer_persona,
        platform=platform,
        marketing_objective=marketing_objective,
        funnel_stage=funnel_stage,
        copy_framework=copy_framework,
        selling_points=selling_points,
        price=price,
        offer=offer,
        language=language,
        compliance_notes=compliance_notes,
        scene_direction=scene_direction,
        identity_preservation=identity_preservation,
        claim_safety=claim_safety,
        use_campaign_preset=use_campaign_preset,
        custom_scene_prompt=custom_scene_prompt,
        reference_usage=reference_usage,
        visual_provider_chain=visual_provider_chain,
        visual_prompt=visual_prompt,
        content_prompt=content_prompt,
        tone=tone,
        num_variants=num_variants,
    )

    result = ProductPromotionPipeline(visual_provider_chain=request.visual_provider_chain).run(
        product_image_path=str(product_path),
        reference_image_path=reference_path,
        request=request,
    )

    best_score = 0.0
    for variant in result.variants:
        if variant.variant_id == result.best_variant_id:
            best_score = variant.scores.get("final_score", 0.0)

    repo = AssetRepository(db)
    repo.create({
        "id": result.asset_id,
        "product_name": product_name,
        "campaign_name": campaign_name,
        "campaign_preset": campaign_preset,
        "brand_name": brand_name,
        "product_condition": product_condition,
        "key_product_facts": key_product_facts,
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
        "scene_direction": scene_direction,
        "identity_preservation": identity_preservation,
        "claim_safety": claim_safety,
        "custom_scene_prompt": custom_scene_prompt,
        "reference_usage": reference_usage,
        "use_campaign_preset": use_campaign_preset,
        "campaign_brief_json": campaign_brief_json,
        "prompt_controls_json": prompt_controls_json,
        "review_checklist_json": review_checklist_json,
        "status": result.status,
        "product_image_path": result.product_image_path,
        "reference_image_path": result.reference_image_path,
        "best_image_path": result.best_image_path,
        "variants_json": json.dumps([v.model_dump() for v in result.variants], ensure_ascii=False),
        "best_variant_id": result.best_variant_id,
        "best_score": best_score,
        "visual_provider_used": result.visual_provider_used,
        "llm_provider_used": result.llm_provider_used,
        "visual_prompt": visual_prompt,
        "content_prompt": content_prompt,
        "tone": tone,
        "description": result.description,
        "caption": result.caption,
        "hashtags": json.dumps(result.hashtags, ensure_ascii=False),
        "channel_outputs_json": json.dumps(result.channel_outputs, ensure_ascii=False),
        "quality_report_json": json.dumps(result.quality_report, ensure_ascii=False),
        "error_message": result.error_message,
    })

    return result.model_dump()


@app.patch("/assets/{asset_id}/selection")
def select_variant(asset_id: str, request: VariantSelectionRequest, db: Session = Depends(get_db)):
    selected_variant_id = request.selected_variant_id
    if not selected_variant_id:
        raise HTTPException(status_code=400, detail="selected_variant_id is required")

    repo = AssetRepository(db)
    asset = repo.get(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    variants = json.loads(asset.variants_json or "[]")
    if not any(variant.get("variant_id") == selected_variant_id for variant in variants):
        raise HTTPException(status_code=404, detail="Variant not found")

    asset.selected_variant_id = selected_variant_id
    asset.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(asset)
    repo.add_event(
        asset_id=asset.id,
        event_type="variant_selected",
        status=asset.status,
        payload={"selected_variant_id": selected_variant_id},
    )
    return repo.to_dict(asset)


@app.get("/assets")
def list_assets(status: str | None = None, db: Session = Depends(get_db)):
    repo = AssetRepository(db)
    return [repo.to_dict(asset) for asset in repo.list(status=status)]


@app.get("/assets/{asset_id}")
def get_asset(asset_id: str, db: Session = Depends(get_db)):
    repo = AssetRepository(db)
    asset = repo.get(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return repo.to_dict(asset)


@app.get("/assets/{asset_id}/events")
def get_asset_events(asset_id: str, db: Session = Depends(get_db)):
    repo = AssetRepository(db)
    if not repo.get(asset_id):
        raise HTTPException(status_code=404, detail="Asset not found")
    return [repo.event_to_dict(event) for event in repo.list_events(asset_id)]


@app.post("/assets/{asset_id}/evaluation")
def record_image_evaluation(
    asset_id: str,
    request: ImageEvaluationRequest,
    db: Session = Depends(get_db),
):
    repo = AssetRepository(db)
    asset = repo.get(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    if not request.compared_with_original:
        raise HTTPException(
            status_code=400,
            detail="Image-model evaluation requires comparison with the original product image.",
        )
    unknown_failures = set(request.failure_modes) - IMAGE_FAILURE_MODES
    if unknown_failures:
        raise HTTPException(
            status_code=400,
            detail="Unknown image evaluation failure mode: " + ", ".join(sorted(unknown_failures)),
        )

    payload = _build_image_evaluation(repo.to_dict(asset), request)
    event = repo.add_event(
        asset_id=asset_id,
        event_type="image_evaluation_recorded",
        status=asset.status,
        note=request.reviewer_comment,
        payload=payload,
    )
    return repo.event_to_dict(event)


@app.get("/evaluation/image-models")
def image_model_evaluation_summary(db: Session = Depends(get_db)):
    repo = AssetRepository(db)
    evaluations = [
        repo.event_to_dict(event)["payload"]
        for event in repo.list_events_by_type("image_evaluation_recorded")
    ]
    by_provider: dict[str, dict] = {}
    for item in evaluations:
        provider = item.get("provider") or "unknown"
        summary = by_provider.setdefault(
            provider,
            {
                "provider": provider,
                "samples": 0,
                "weighted_scores": [],
                "product_fidelity_scores": [],
                "identity_passes": 0,
                "publishable_outputs": 0,
                "failure_modes": Counter(),
            },
        )
        summary["samples"] += 1
        summary["weighted_scores"].append(item.get("weighted_score", 0))
        summary["product_fidelity_scores"].append(
            (item.get("ratings") or {}).get("product_fidelity", 0)
        )
        summary["identity_passes"] += int(bool(item.get("identity_pass")))
        summary["publishable_outputs"] += int(bool(item.get("publishable")))
        summary["failure_modes"].update(item.get("failure_modes") or [])

    models = []
    for summary in by_provider.values():
        samples = summary["samples"]
        failures = summary["failure_modes"].most_common(3)
        models.append(
            {
                "provider": summary["provider"],
                "samples": samples,
                "average_weighted_score": round(sum(summary["weighted_scores"]) / samples, 1),
                "average_product_fidelity": round(
                    sum(summary["product_fidelity_scores"]) / samples, 2
                ),
                "identity_pass_rate": round(summary["identity_passes"] / samples * 100, 1),
                "publishable_rate": round(summary["publishable_outputs"] / samples * 100, 1),
                "top_failure_modes": [name for name, _ in failures],
            }
        )

    return {
        "total_evaluations": len(evaluations),
        "models": sorted(models, key=lambda row: (-row["samples"], row["provider"])),
        "method": (
            "Human side-by-side evaluation. Product fidelity is weighted at 40%; any identity "
            "failure prevents an output from counting as publishable."
        ),
    }


@app.patch("/assets/{asset_id}/review")
def review_asset(asset_id: str, request: ReviewRequest, db: Session = Depends(get_db)):
    if request.status not in REVIEW_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid status")

    repo = AssetRepository(db)
    existing_asset = repo.get(asset_id)
    if not existing_asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    if request.status == EXPORTED and existing_asset.status != EXPORTED:
        raise HTTPException(status_code=400, detail="Use the export action after approval to mark an asset exported.")
    if request.status == "approved" and _requires_identity_verification(repo.to_dict(existing_asset)):
        if not request.identity_verified:
            raise HTTPException(
                status_code=400,
                detail="Approval requires confirmation that product identity was checked against the original image.",
            )

    asset = repo.update_review(
        asset_id=asset_id,
        status=request.status,
        reviewer_note=request.reviewer_note,
        review_checklist=request.review_checklist,
        description=request.description,
        caption=request.caption,
        hashtags=request.hashtags,
        channel_outputs=request.channel_outputs,
        best_variant_id=request.best_variant_id,
        selected_variant_id=request.selected_variant_id,
        identity_verified=request.identity_verified,
    )

    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    return repo.to_dict(asset)


def _requires_identity_verification(asset: dict) -> bool:
    report = asset.get("quality_report") or {}
    assurance = report.get("identity_assurance") or {}
    if "requires_identity_review" in assurance:
        return bool(assurance["requires_identity_review"])
    provider = asset.get("visual_provider_used") or ""
    return "source_product_overlay" not in provider and provider != "original_fallback"


def _build_image_evaluation(asset: dict, request: ImageEvaluationRequest) -> dict:
    ratings = {
        field: getattr(request, field)
        for field in IMAGE_EVALUATION_WEIGHTS
    }
    weighted_score = sum(
        ratings[field] / 5 * weight
        for field, weight in IMAGE_EVALUATION_WEIGHTS.items()
    )
    failures = sorted(set(request.failure_modes))
    identity_failures = sorted(set(failures) & IDENTITY_FAILURE_MODES)
    identity_pass = request.product_fidelity >= 4 and not identity_failures
    publishable = (
        identity_pass
        and request.publish_readiness >= 4
        and weighted_score >= 80
        and not failures
    )
    if identity_failures:
        decision = "failed_product_identity"
    elif publishable:
        decision = "publishable_candidate"
    else:
        decision = "needs_revision"

    selected_variant = next(
        (
            variant
            for variant in asset.get("variants", [])
            if variant.get("variant_id") == asset.get("best_variant_id")
        ),
        {},
    )
    return {
        "provider": selected_variant.get("provider") or asset.get("visual_provider_used") or "unknown",
        "variant_id": asset.get("best_variant_id"),
        "ratings": ratings,
        "weighted_score": round(weighted_score, 1),
        "failure_modes": failures,
        "identity_pass": identity_pass,
        "publishable": publishable,
        "decision": decision,
        "compared_with_original": request.compared_with_original,
        "reviewer_comment": request.reviewer_comment,
    }


@app.get("/files")
def get_file(path: str):
    file_path = _resolve_storage_path(path)
    if not file_path.exists():
        if file_path.suffix.lower() in ALLOWED_IMAGE_EXTENSIONS:
            return _missing_file_placeholder(file_path)
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(str(file_path))


@app.get("/assets/{asset_id}/export")
def export_asset(asset_id: str, db: Session = Depends(get_db)):
    repo = AssetRepository(db)
    existing_asset = repo.get(asset_id)
    if not existing_asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    if not _can_export_asset(repo.to_dict(existing_asset)):
        raise HTTPException(status_code=400, detail="Asset must be approved before export.")

    asset = repo.mark_exported(asset_id)

    asset_dict = repo.to_dict(asset)
    zip_path = ExportService().export_asset(asset_dict)
    return FileResponse(zip_path, filename=Path(zip_path).name)


def _can_export_asset(asset: dict) -> bool:
    return asset.get("status") in {APPROVED, EXPORTED}


def _save_upload(upload: UploadFile, folder_name: str) -> Path:
    suffix = Path(upload.filename or "").suffix.lower()
    if suffix not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only jpg, jpeg, png, and webp images are allowed")

    content_type = (upload.content_type or "").lower()
    if content_type and not content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image")

    storage_dir = Path(settings.STORAGE_DIR) / "input" / folder_name
    storage_dir.mkdir(parents=True, exist_ok=True)

    stem = Path(upload.filename or folder_name).stem
    safe_stem = re.sub(r"[^a-zA-Z0-9_-]+", "_", stem).strip("_")[:60] or folder_name
    output_path = storage_dir / f"{uuid4().hex}_{safe_stem}{suffix}"

    max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
    bytes_written = 0
    with open(output_path, "wb") as file:
        while chunk := upload.file.read(1024 * 1024):
            bytes_written += len(chunk)
            if bytes_written > max_bytes:
                output_path.unlink(missing_ok=True)
                raise HTTPException(status_code=413, detail="Uploaded image is too large")
            file.write(chunk)

    upload.file.seek(0)
    return output_path


def _resolve_storage_path(path: str) -> Path:
    storage_root = Path(settings.STORAGE_DIR).resolve()
    requested_path = Path(path)
    if not requested_path.is_absolute():
        requested_path = Path.cwd() / requested_path
    resolved_path = requested_path.resolve()

    if not resolved_path.is_relative_to(storage_root):
        raise HTTPException(status_code=403, detail="File access outside storage is not allowed")

    return resolved_path


def _missing_file_placeholder(file_path: Path) -> StreamingResponse:
    canvas = Image.new("RGB", (1024, 1024), (245, 242, 236))
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle([72, 72, 952, 952], radius=36, outline=(178, 168, 152), width=6)
    draw.text((120, 160), "Image unavailable", fill=(54, 49, 44))
    draw.text((120, 240), file_path.name, fill=(104, 96, 87))
    draw.text(
        (120, 340),
        "The asset file was pruned or never persisted.\nRegenerate the asset to restore the original image.",
        fill=(92, 84, 76),
    )

    buffer = BytesIO()
    canvas.save(buffer, format="PNG")
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="image/png")


def _configuration_warnings() -> list[str]:
    warnings = []
    visual_chain = settings.VISUAL_PROVIDER_CHAIN.lower()
    replicate_token = (settings.REPLICATE_API_TOKEN or "").strip()
    imagen_models = {
        "imagen-4.0-generate-001",
        "imagen-4.0-fast-generate-001",
        "imagen-4.0-ultra-generate-001",
    }

    has_cloudflare_provider = (
        "cloudflare_flux" in visual_chain or "cloudflare_inpaint" in visual_chain
    )
    if has_cloudflare_provider:
        if not settings.CLOUDFLARE_ACCOUNT_ID:
            warnings.append("A Cloudflare image provider is enabled but CLOUDFLARE_ACCOUNT_ID is empty.")
        if not settings.CLOUDFLARE_API_TOKEN:
            warnings.append("A Cloudflare image provider is enabled but CLOUDFLARE_API_TOKEN is empty.")
        if "original" not in visual_chain and "mock" not in visual_chain:
            warnings.append("Add original as a final identity-safe fallback if Cloudflare generation fails.")

    if "cloudflare_flux" in visual_chain:
        if settings.CLOUDFLARE_IMAGE_MODEL != "@cf/black-forest-labs/flux-2-klein-4b":
            warnings.append(
                "CLOUDFLARE_IMAGE_MODEL is not the tested demo editor; "
                "use @cf/black-forest-labs/flux-2-klein-4b for this workflow."
            )

    if "cloudflare_inpaint" in visual_chain:
        if settings.CLOUDFLARE_INPAINT_MODEL != "@cf/runwayml/stable-diffusion-v1-5-inpainting":
            warnings.append(
                "CLOUDFLARE_INPAINT_MODEL is not the tested masked-background fallback; "
                "use @cf/runwayml/stable-diffusion-v1-5-inpainting for this workflow."
            )

    if "google_imagen" in visual_chain or "imagen" in visual_chain:
        if not settings.GEMINI_API_KEY:
            warnings.append("google_imagen is enabled but GEMINI_API_KEY is empty.")
        if settings.GOOGLE_IMAGEN_MODEL not in imagen_models:
            warnings.append(
                "GOOGLE_IMAGEN_MODEL does not look like a current Gemini API Imagen model. "
                "Use imagen-4.0-generate-001, imagen-4.0-fast-generate-001, or imagen-4.0-ultra-generate-001."
            )
        warnings.append(
            "google_imagen is an input-aware text-to-image fallback: it summarizes uploaded images first, "
            "but it is not pixel-level product editing."
        )
        warnings.append(
            "Do not place google_imagen before direct image editors when exact product identity is required."
        )

    if "replicate_flux" in visual_chain:
        if not replicate_token:
            warnings.append("replicate_flux is enabled but REPLICATE_API_TOKEN is empty.")
        elif replicate_token.startswith("bfl_"):
            warnings.append(
                "REPLICATE_API_TOKEN looks like a Black Forest Labs key, but replicate_flux requires a Replicate API token."
            )
        if "original" not in visual_chain and "mock" not in visual_chain:
            warnings.append("Add original as a final identity-safe fallback if all paid image editors fail.")

    return warnings
