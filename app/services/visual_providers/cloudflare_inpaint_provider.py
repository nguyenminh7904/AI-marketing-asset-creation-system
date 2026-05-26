import base64
import binascii
from io import BytesIO

import requests
from PIL import Image

from app.config import settings
from app.services.visual_providers.cloudflare_flux_provider import CloudflareFluxProvider


class CloudflareInpaintProvider(CloudflareFluxProvider):
    """Background-only fallback for transparent product cutouts."""

    name = "cloudflare_inpaint"

    def generate_variant(
        self,
        asset_id: str,
        variant_index: int,
        product_image_path: str,
        reference_image_path: str | None,
        visual_prompt: str,
        output_path: str,
    ) -> dict:
        if not settings.CLOUDFLARE_ACCOUNT_ID or not settings.CLOUDFLARE_API_TOKEN:
            raise RuntimeError("Missing CLOUDFLARE_ACCOUNT_ID or CLOUDFLARE_API_TOKEN")
        if not self._has_transparent_foreground(product_image_path):
            raise RuntimeError(
                "cloudflare_inpaint requires a transparent-background PNG product cutout for a safe mask"
            )

        source_product_overlay = self._build_source_product_overlay(product_image_path)
        starter_bytes, mask_bytes = self._build_inpaint_inputs(source_product_overlay)
        response = requests.post(
            self._endpoint(),
            headers={"Authorization": f"Bearer {settings.CLOUDFLARE_API_TOKEN}"},
            json={
                "prompt": self._build_inpaint_prompt(visual_prompt, variant_index),
                "negative_prompt": (
                    "text, watermark, logo added to background, hands, people, competing product, "
                    "props covering the product silhouette, unrealistic shadow"
                ),
                "image_b64": base64.b64encode(starter_bytes).decode("ascii"),
                "mask": list(mask_bytes),
                "width": settings.CLOUDFLARE_IMAGE_WIDTH,
                "height": settings.CLOUDFLARE_IMAGE_HEIGHT,
                "num_steps": 20,
                "strength": 1,
                "guidance": 7.5,
            },
            timeout=settings.REQUEST_TIMEOUT_SECONDS,
        )
        if response.status_code >= 400:
            raise RuntimeError(
                f"Cloudflare Workers AI inpainting failed: {response.status_code} {response.text[:300]}"
            )

        self._write_output_image(
            self._decode_output_image(response),
            output_path,
            source_product_overlay,
        )
        return {
            "variant_id": f"v{variant_index + 1}",
            "image_path": output_path,
            "provider": (
                f"{self.name}:{settings.CLOUDFLARE_INPAINT_MODEL}:source_product_overlay"
            ),
        }

    def _endpoint(self) -> str:
        return (
            "https://api.cloudflare.com/client/v4/accounts/"
            f"{settings.CLOUDFLARE_ACCOUNT_ID}/ai/run/{settings.CLOUDFLARE_INPAINT_MODEL}"
        )

    def _build_inpaint_prompt(self, visual_prompt: str, variant_index: int) -> str:
        return f"""
Create only the professional product-photography environment outside the protected product mask.
The product will be composited back from its original transparent source layer, so keep the central
product area clear and produce a believable external grounding shadow without adding any object over it.

Scene direction:
{visual_prompt}

Create fallback variant {variant_index + 1}. No text, watermark, people, hands, duplicate products,
or decorative props crossing the protected product silhouette.
"""

    def _build_inpaint_inputs(self, source_product_overlay: Image.Image) -> tuple[bytes, bytes]:
        starter = Image.new("RGBA", source_product_overlay.size, (244, 242, 238, 255))
        starter.alpha_composite(source_product_overlay)

        # Inpaint the transparent background area and protect the source product silhouette.
        alpha = source_product_overlay.getchannel("A")
        mask = Image.eval(alpha, lambda value: 255 - value)

        starter_buffer = BytesIO()
        starter.convert("RGB").save(starter_buffer, format="PNG", optimize=True)
        mask_buffer = BytesIO()
        mask.save(mask_buffer, format="PNG", optimize=True)
        return starter_buffer.getvalue(), mask_buffer.getvalue()

    def _decode_output_image(self, response) -> bytes:
        content_type = (response.headers.get("content-type", "") if response.headers else "").lower()
        if "image/" in content_type or response.content.startswith((b"\x89PNG", b"\xff\xd8\xff")):
            return response.content

        try:
            payload = response.json()
            result = payload.get("result", payload)
            encoded_image = result.get("image") if isinstance(result, dict) else None
            if not encoded_image:
                raise ValueError("response has no output image")
            return base64.b64decode(encoded_image.split(",", 1)[-1], validate=True)
        except (ValueError, KeyError, TypeError, binascii.Error) as exc:
            raise RuntimeError(f"Cloudflare inpainting returned no decodable image: {exc}") from exc
