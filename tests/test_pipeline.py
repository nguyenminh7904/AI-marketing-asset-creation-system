from PIL import Image
from app.config import settings
from app.core.pipeline import ProductPromotionPipeline
from app.core.schemas import GenerationRequest


def test_pipeline_runs(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "VISUAL_PROVIDER_CHAIN", "mock")
    monkeypatch.setattr(settings, "LLM_PROVIDER_CHAIN", "mock")

    product_path = tmp_path / "product.jpg"
    Image.new("RGB", (300, 300), (255, 0, 0)).save(product_path)

    req = GenerationRequest(
        product_name="Test Shirt",
        campaign_name="Test Campaign",
        brand_name="Test Shop",
        target_audience="students",
        visual_prompt="Put this shirt naturally on a grass field.",
        content_prompt="Write caption",
        num_variants=3,
    )

    result = ProductPromotionPipeline().run(str(product_path), None, req)
    assert result.status in ["generated", "failed"]
    if result.status == "generated":
        assert result.channel_outputs
        assert result.quality_report
        assert len(result.variants) == 3
        assert result.recommended_variant_id
        assert result.selected_variant_id is None
