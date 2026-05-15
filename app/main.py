import json
import re
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.logging_config import setup_logging
from app.database import get_db, init_db
from app.core.schemas import GenerationRequest, ReviewRequest
from app.core.status import REVIEW_STATUSES
from app.core.pipeline import ProductPromotionPipeline
from app.repositories.asset_repository import AssetRepository
from app.services.export_service import ExportService


logger = setup_logging()
app = FastAPI(title=settings.APP_NAME)

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


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
        "has_gemini_key": bool(settings.GEMINI_API_KEY),
        "has_replicate_key": bool(settings.REPLICATE_API_TOKEN),
        "gemini_image_model": settings.GEMINI_IMAGE_MODEL,
        "gemini_image_model_chain": settings.GEMINI_IMAGE_MODEL_CHAIN,
        "gemini_text_model": settings.GEMINI_TEXT_MODEL,
        "max_upload_mb": settings.MAX_UPLOAD_MB,
        "configuration_warnings": _configuration_warnings(),
    }


@app.post("/generate")
async def generate_asset(
    product_image: UploadFile = File(...),
    reference_image: UploadFile | None = File(None),
    product_name: str | None = Form(None),
    campaign_name: str | None = Form(None),
    brand_name: str | None = Form(None),
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
        brand_name=brand_name,
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
        visual_prompt=visual_prompt,
        content_prompt=content_prompt,
        tone=tone,
        num_variants=num_variants,
    )

    result = ProductPromotionPipeline().run(
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


@app.patch("/assets/{asset_id}/review")
def review_asset(asset_id: str, request: ReviewRequest, db: Session = Depends(get_db)):
    if request.status not in REVIEW_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid status")

    repo = AssetRepository(db)
    asset = repo.update_review(
        asset_id=asset_id,
        status=request.status,
        reviewer_note=request.reviewer_note,
        description=request.description,
        caption=request.caption,
        hashtags=request.hashtags,
        channel_outputs=request.channel_outputs,
        best_variant_id=request.best_variant_id,
    )

    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    return repo.to_dict(asset)


@app.get("/files")
def get_file(path: str):
    file_path = _resolve_storage_path(path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(str(file_path))


@app.get("/assets/{asset_id}/export")
def export_asset(asset_id: str, db: Session = Depends(get_db)):
    repo = AssetRepository(db)
    asset = repo.mark_exported(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    asset_dict = repo.to_dict(asset)
    zip_path = ExportService().export_asset(asset_dict)
    return FileResponse(zip_path, filename=Path(zip_path).name)


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


def _configuration_warnings() -> list[str]:
    warnings = []
    visual_chain = settings.VISUAL_PROVIDER_CHAIN.lower()
    replicate_token = (settings.REPLICATE_API_TOKEN or "").strip()
    gemini_image_models = {"gemini-2.5-flash-image", "gemini-3-pro-image-preview"}

    if "replicate_flux" in visual_chain:
        if not replicate_token:
            warnings.append("replicate_flux is enabled but REPLICATE_API_TOKEN is empty.")
        elif replicate_token.startswith("bfl_"):
            warnings.append(
                "REPLICATE_API_TOKEN looks like a Black Forest Labs key, but replicate_flux requires a Replicate API token."
            )

    if "gemini_image" in visual_chain and not settings.GEMINI_API_KEY:
        warnings.append("gemini_image is enabled but GEMINI_API_KEY is empty.")
    elif "gemini_image" in visual_chain:
        configured_models = [
            model.strip()
            for model in (settings.GEMINI_IMAGE_MODEL_CHAIN or settings.GEMINI_IMAGE_MODEL).split(",")
            if model.strip()
        ]
        unknown_models = [model for model in configured_models if model not in gemini_image_models]
        if unknown_models:
            warnings.append(
                "GEMINI_IMAGE_MODEL_CHAIN contains model(s) that do not look like current Gemini image models: "
                + ", ".join(unknown_models)
            )
        warnings.append(
            "Gemini image 429 errors usually mean project quota, rate limit, or billing allowance is exhausted; "
            "switching Gemini image models may not bypass account-level quota."
        )

    return warnings
