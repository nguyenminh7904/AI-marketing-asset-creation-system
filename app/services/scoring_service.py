from PIL import Image, ImageStat
import numpy as np
from loguru import logger


class ScoringService:
    def score_variants(self, variants: list[dict], visual_prompt: str, reference_image_path: str | None) -> list[dict]:
        logger.info("Scoring variants")
        scored = []

        for idx, variant in enumerate(variants):
            scores = self._score_one(
                image_path=variant["image_path"],
                visual_prompt=visual_prompt,
                reference_image_path=reference_image_path,
                idx=idx,
                provider=variant.get("provider"),
            )
            scored.append({**variant, "scores": scores})

        return scored

    def pick_best(self, scored_variants: list[dict]) -> dict:
        return max(scored_variants, key=lambda x: x["scores"]["final_score"])

    def build_quality_report(self, scored_variants: list[dict], best_variant_id: str, campaign_context: dict) -> dict:
        if not scored_variants:
            return {
                "summary": "No variants were available for quality evaluation.",
                "scorecard": {},
                "recommendations": ["Regenerate with at least one visual provider available."],
            }

        best = next(
            (variant for variant in scored_variants if variant["variant_id"] == best_variant_id),
            scored_variants[0],
        )
        best_scores = best.get("scores", {})
        average_score = sum(
            variant.get("scores", {}).get("final_score", 0.0)
            for variant in scored_variants
        ) / len(scored_variants)

        recommendations = []
        if best_scores.get("product_visibility_proxy", 0) < 0.82:
            recommendations.append("Use a tighter product crop or clearer product placement.")
        if best_scores.get("reference_format_similarity_proxy", 0) < 0.78:
            recommendations.append("Choose a reference image closer to the required camera angle and layout.")
        if best_scores.get("commercial_readiness_proxy", 0) < 0.8:
            recommendations.append("Strengthen the offer, CTA, and selling points before publishing.")
        if not recommendations:
            recommendations.append("Ready for human review. Validate brand identity and product details before export.")

        return {
            "summary": (
                f"Best variant {best_variant_id} scored {best_scores.get('final_score', 0):.4f} "
                f"with an average variant score of {average_score:.4f}."
            ),
            "best_variant_id": best_variant_id,
            "best_provider": best.get("provider"),
            "scorecard": best_scores,
            "average_final_score": round(average_score, 4),
            "evaluation_dimensions": [
                "aesthetic_score",
                "prompt_alignment_proxy",
                "product_visibility_proxy",
                "reference_format_similarity_proxy",
                "brand_consistency_proxy",
                "commercial_readiness_proxy",
            ],
            "campaign_fit": {
                "platform": campaign_context.get("platform"),
                "objective": campaign_context.get("marketing_objective"),
                "funnel_stage": campaign_context.get("funnel_stage"),
                "copy_framework": campaign_context.get("copy_framework"),
            },
            "recommendations": recommendations,
            "disclaimer": "Scores are heuristic product-readiness indicators, not lab-grade FID, LPIPS, or CLIP metrics.",
        }

    def _score_one(self, image_path: str, visual_prompt: str, reference_image_path: str | None, idx: int, provider: str | None) -> dict:
        img = Image.open(image_path).convert("RGB")
        stat = ImageStat.Stat(img)

        brightness = sum(stat.mean) / 3
        contrast = sum(stat.stddev) / 3

        aesthetic_score = min(1.0, max(0.0, (contrast / 90) * 0.55 + (brightness / 255) * 0.45))
        prompt_alignment_proxy = 0.72 + min(0.2, len(visual_prompt) / 500)
        product_visibility_proxy = 0.78 + (idx % 3) * 0.025
        provider_bonus = 0.08 if provider in ["gemini_image", "replicate_flux"] else 0.0
        reference_format_similarity_proxy = self._reference_similarity(img, reference_image_path)
        brand_consistency_proxy = min(1.0, 0.74 + min(0.16, len(visual_prompt) / 700))
        commercial_readiness_proxy = min(
            1.0,
            aesthetic_score * 0.45 + product_visibility_proxy * 0.35 + reference_format_similarity_proxy * 0.20,
        )

        final_score = (
            aesthetic_score * 0.20
            + prompt_alignment_proxy * 0.18
            + product_visibility_proxy * 0.18
            + reference_format_similarity_proxy * 0.16
            + brand_consistency_proxy * 0.12
            + commercial_readiness_proxy * 0.08
            + provider_bonus
        )

        return {
            "aesthetic_score": round(min(aesthetic_score, 1.0), 4),
            "prompt_alignment_proxy": round(min(prompt_alignment_proxy, 1.0), 4),
            "product_visibility_proxy": round(min(product_visibility_proxy, 1.0), 4),
            "reference_format_similarity_proxy": round(min(reference_format_similarity_proxy, 1.0), 4),
            "brand_consistency_proxy": round(min(brand_consistency_proxy, 1.0), 4),
            "commercial_readiness_proxy": round(min(commercial_readiness_proxy, 1.0), 4),
            "provider_bonus": round(provider_bonus, 4),
            "final_score": round(min(final_score, 1.0), 4),
        }

    def _reference_similarity(self, img: Image.Image, reference_image_path: str | None) -> float:
        if not reference_image_path:
            return 0.75

        try:
            ref = Image.open(reference_image_path).convert("RGB").resize((128, 128))
            out = img.convert("RGB").resize((128, 128))

            ref_arr = np.asarray(ref).astype("float32") / 255.0
            out_arr = np.asarray(out).astype("float32") / 255.0

            ref_mean = ref_arr.mean(axis=(0, 1))
            out_mean = out_arr.mean(axis=(0, 1))

            distance = float(np.linalg.norm(ref_mean - out_mean))
            return max(0.0, 1.0 - distance)
        except Exception:
            return 0.75
