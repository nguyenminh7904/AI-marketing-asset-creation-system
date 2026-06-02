from __future__ import annotations

import json
from datetime import datetime
from uuid import uuid4
from sqlalchemy.orm import Session
from app.repositories.models import Asset, AssetEvent
from app.core.status import EXPORTED


class AssetRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict) -> Asset:
        allowed_fields = set(Asset.__table__.columns.keys())
        asset_data = {key: value for key, value in data.items() if key in allowed_fields}
        asset = Asset(**asset_data)
        self.db.add(asset)
        self.db.commit()
        self.db.refresh(asset)
        self.add_event(
            asset_id=asset.id,
            event_type="asset_created",
            status=asset.status,
            payload={"product_name": asset.product_name, "campaign_name": asset.campaign_name},
        )
        return asset

    def list(self, status: str | None = None) -> list[Asset]:
        query = self.db.query(Asset).order_by(Asset.created_at.desc())
        if status:
            query = query.filter(Asset.status == status)
        return query.all()

    def get(self, asset_id: str) -> Asset | None:
        return self.db.query(Asset).filter(Asset.id == asset_id).first()

    def update_review(
        self,
        asset_id: str,
        status: str,
        reviewer_note: str | None,
        review_checklist: dict | None = None,
        description: str | None = None,
        caption: str | None = None,
        hashtags: list[str] | None = None,
        channel_outputs: dict | None = None,
        best_variant_id: str | None = None,
        selected_variant_id: str | None = None,
        identity_verified: bool = False,
    ):
        asset = self.get(asset_id)
        if not asset:
            return None

        asset.status = status
        asset.reviewer_note = reviewer_note

        if description is not None:
            asset.description = description
        if caption is not None:
            asset.caption = caption
        if hashtags is not None:
            asset.hashtags = json.dumps(hashtags, ensure_ascii=False)
        if channel_outputs is not None:
            asset.channel_outputs_json = json.dumps(channel_outputs, ensure_ascii=False)
        if best_variant_id:
            self._apply_best_variant(asset, best_variant_id)
        if selected_variant_id:
            asset.selected_variant_id = selected_variant_id
        elif best_variant_id and not asset.selected_variant_id:
            asset.selected_variant_id = best_variant_id
        if review_checklist is not None:
            asset.review_checklist_json = json.dumps(review_checklist, ensure_ascii=False)

        asset.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(asset)
        self.add_event(
            asset_id=asset.id,
            event_type="review_updated",
            status=asset.status,
            note=reviewer_note,
            payload={
                "best_variant_id": asset.best_variant_id,
                "edited_content": any(
                    value is not None
                    for value in [description, caption, hashtags, channel_outputs]
                ),
                "identity_verified": identity_verified,
                "review_checklist": review_checklist or {},
            },
        )
        return asset

    def mark_exported(self, asset_id: str):
        asset = self.get(asset_id)
        if not asset:
            return None

        asset.status = EXPORTED
        asset.exported_at = datetime.utcnow()
        asset.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(asset)
        self.add_event(asset.id, "asset_exported", status=asset.status)
        return asset

    def add_event(
        self,
        asset_id: str,
        event_type: str,
        status: str | None = None,
        note: str | None = None,
        payload: dict | None = None,
    ) -> AssetEvent:
        event = AssetEvent(
            id=str(uuid4()),
            asset_id=asset_id,
            event_type=event_type,
            status=status,
            note=note,
            payload_json=json.dumps(payload or {}, ensure_ascii=False),
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def list_events(self, asset_id: str) -> list[AssetEvent]:
        return (
            self.db.query(AssetEvent)
            .filter(AssetEvent.asset_id == asset_id)
            .order_by(AssetEvent.created_at.asc())
            .all()
        )

    def list_events_by_type(self, event_type: str) -> list[AssetEvent]:
        return (
            self.db.query(AssetEvent)
            .filter(AssetEvent.event_type == event_type)
            .order_by(AssetEvent.created_at.asc())
            .all()
        )

    def _apply_best_variant(self, asset: Asset, best_variant_id: str):
        selected = self._find_variant(asset, best_variant_id)
        if not selected:
            return

        asset.best_variant_id = best_variant_id
        asset.best_image_path = selected.get("image_path")
        asset.best_score = selected.get("scores", {}).get("final_score")

    def _find_variant(self, asset: Asset, variant_id: str) -> dict | None:
        variants = json.loads(asset.variants_json or "[]")
        return next((variant for variant in variants if variant.get("variant_id") == variant_id), None)

    def _variant_snapshot(self, asset: Asset, variant_id: str | None) -> dict:
        if not variant_id:
            return {}
        variant = self._find_variant(asset, variant_id)
        if not variant:
            return {}
        scores = variant.get("scores") or {}
        return {
            "variant_id": variant.get("variant_id"),
            "image_path": variant.get("image_path"),
            "provider": variant.get("provider"),
            "score": scores.get("final_score"),
            "display_score": variant.get("display_score"),
            "quality_status": variant.get("quality_status"),
            "notes": variant.get("notes") or [],
            "variant_direction": variant.get("variant_direction"),
        }

    @staticmethod
    def to_dict(asset: Asset) -> dict:
        campaign_brief = json.loads(asset.campaign_brief_json or "{}")
        prompt_controls = json.loads(asset.prompt_controls_json or "{}")
        variants = json.loads(asset.variants_json or "[]")
        recommended_variant_id = asset.best_variant_id
        selected_variant_id = asset.selected_variant_id or recommended_variant_id
        recommended_variant = next(
            (variant for variant in variants if variant.get("variant_id") == recommended_variant_id),
            None,
        ) or {}
        selected_variant = next(
            (variant for variant in variants if variant.get("variant_id") == selected_variant_id),
            None,
        ) or recommended_variant

        selected_scores = selected_variant.get("scores") or {}
        recommended_scores = recommended_variant.get("scores") or {}
        return {
            "id": asset.id,
            "product_name": asset.product_name,
            "campaign_name": asset.campaign_name,
            "campaign_preset": campaign_brief.get("campaign_preset"),
            "brand_name": asset.brand_name,
            "product_condition": asset.product_condition,
            "key_product_facts": asset.key_product_facts,
            "target_audience": asset.target_audience,
            "customer_persona": asset.customer_persona,
            "platform": asset.platform,
            "marketing_objective": asset.marketing_objective,
            "funnel_stage": asset.funnel_stage,
            "copy_framework": asset.copy_framework,
            "selling_points": asset.selling_points,
            "price": asset.price,
            "offer": asset.offer,
            "language": asset.language,
            "compliance_notes": asset.compliance_notes,
            "scene_direction": asset.scene_direction,
            "identity_preservation": asset.identity_preservation,
            "claim_safety": asset.claim_safety,
            "campaign_brief": campaign_brief,
            "prompt_controls": prompt_controls,
            "custom_scene_prompt": prompt_controls.get("custom_scene_prompt") or campaign_brief.get("custom_scene_prompt"),
            "reference_usage": prompt_controls.get("reference_usage"),
            "use_campaign_preset": prompt_controls.get("use_campaign_preset"),
            "review_checklist": json.loads(asset.review_checklist_json or "{}"),
            "status": asset.status,
            "product_image_path": asset.product_image_path,
            "reference_image_path": asset.reference_image_path,
            "best_image_path": selected_variant.get("image_path") or asset.best_image_path,
            "variants": variants,
            "best_variant_id": recommended_variant_id,
            "recommended_variant_id": recommended_variant_id,
            "selected_variant_id": asset.selected_variant_id,
            "selected_variant_number": next(
                (index + 1 for index, variant in enumerate(variants) if variant.get("variant_id") == selected_variant_id),
                None,
            ),
            "best_score": selected_scores.get("final_score") or asset.best_score,
            "recommended_score": recommended_scores.get("final_score") or asset.best_score,
            "selected_score": selected_scores.get("final_score") or asset.best_score,
            "selected_image_path": selected_variant.get("image_path") or asset.best_image_path,
            "recommended_image_path": recommended_variant.get("image_path") or asset.best_image_path,
            "visual_provider_used": asset.visual_provider_used,
            "llm_provider_used": asset.llm_provider_used,
            "description": asset.description,
            "caption": asset.caption,
            "hashtags": json.loads(asset.hashtags or "[]"),
            "channel_outputs": json.loads(asset.channel_outputs_json or "{}"),
            "quality_report": json.loads(asset.quality_report_json or "{}"),
            "visual_prompt": asset.visual_prompt,
            "content_prompt": asset.content_prompt,
            "tone": asset.tone,
            "reviewer_note": asset.reviewer_note,
            "error_message": asset.error_message,
            "exported_at": asset.exported_at.isoformat() if asset.exported_at else None,
            "created_at": asset.created_at.isoformat() if asset.created_at else None,
            "updated_at": asset.updated_at.isoformat() if asset.updated_at else None,
        }

    @staticmethod
    def event_to_dict(event: AssetEvent) -> dict:
        return {
            "id": event.id,
            "asset_id": event.asset_id,
            "event_type": event.event_type,
            "status": event.status,
            "note": event.note,
            "payload": json.loads(event.payload_json or "{}"),
            "created_at": event.created_at.isoformat() if event.created_at else None,
        }
