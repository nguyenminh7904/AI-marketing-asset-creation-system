# AI Product Studio Update Summary

This document summarizes the main product, backend, database, UI, provider, and evaluation updates made to AI Product Studio.

## 1. Product Direction

The system was upgraded from a simple API demo into a more complete AI marketing asset workspace.

Current positioning:

```text
AI Product Studio helps small fashion and luxury resale sellers transform raw product photos into campaign-ready marketing assets through AI image generation, marketing copy generation, quality scoring, and human-in-the-loop review.
```

The product now focuses on campaign creation, luxury resale templates, review workflows, channel-specific marketing outputs, and exportable campaign packages.

## 2. UI Updates

Updated file:

```text
ui/streamlit_app.py
```

Major UI changes:

- Added a workspace-style Streamlit interface.
- Added tabs for:
  - Create Campaign
  - Review Board
  - Asset Library
  - Evaluation
- Replaced the football jersey default campaign with luxury product templates.
- Added editable campaign brief fields.
- Added variant comparison.
- Added editable review fields for caption, description, hashtags, channel copy, and reviewer notes.
- Added best-variant selection.
- Added audit trail toggle.
- Added campaign ZIP export button.
- Fixed Streamlit nested-expander error by replacing the audit-trail expander with a toggle.

## 3. Luxury Campaign Templates

Added four reusable luxury-item campaign templates:

| Template | Product Type | Main Platform | Main Goal |
| --- | --- | --- | --- |
| Luxury Handbag Resale | Pre-owned leather handbag | Instagram | Conversion |
| Luxury Watch Collector Drop | Pre-owned luxury watch | Facebook | Conversion |
| Silk Scarf Editorial | Vintage silk scarf | TikTok | Engagement |
| Premium Leather Loafers | Pre-owned leather loafers | Shopee | Conversion |

Each template includes:

- Campaign name
- Product name
- Brand/shop name
- Target audience
- Customer persona
- Selling points
- Offer
- Price
- Platform
- Funnel stage
- Copywriting framework
- Compliance notes
- Visual prompt
- Content prompt

## 4. Backend/API Updates

Updated file:

```text
app/main.py
```

Major backend changes:

- Expanded `/generate` input fields for campaign-grade briefs.
- Added safer upload handling.
- Added file extension and content-type validation.
- Added upload size limit through `MAX_UPLOAD_MB`.
- Added safer `/files` route so only files inside `storage/` can be served.
- Added `/assets/{asset_id}/events` endpoint for audit history.
- Added review update support for editable marketing content.
- Added export status tracking.
- Added `/health` configuration warnings.

## 5. Database Updates

Updated files:

```text
app/repositories/models.py
app/repositories/asset_repository.py
app/database.py
```

Database improvements:

- Added campaign fields to assets:
  - campaign name
  - brand name
  - target audience
  - customer persona
  - platform
  - marketing objective
  - funnel stage
  - copy framework
  - selling points
  - price
  - offer
  - language
  - compliance notes
- Added channel outputs JSON.
- Added quality report JSON.
- Added export timestamp.
- Added `asset_events` table for audit history.
- Added lightweight SQLite-safe migrations so existing local `app.db` can be upgraded without being deleted.

## 6. AI Pipeline Updates

Updated files:

```text
app/core/pipeline.py
app/core/schemas.py
app/services/scoring_service.py
app/services/llm_service.py
app/services/llm_providers/gemini_text_provider.py
app/services/llm_providers/mock_provider.py
```

Pipeline improvements:

- Added campaign context to image prompts.
- Added campaign context to LLM copy generation.
- Connected the original product image to Gemini text generation for grounded product recognition and detailed sales copy.
- Added structured `product_analysis` output: detected product type, observed description, visible details, condition observations, buyer-appeal points, and unknown/unverified details.
- Displayed product analysis in the UI and included it in export packages as `content/product_analysis.json`.
- Added channel-specific marketing outputs:
  - SEO title
  - Product description
  - Instagram caption
  - Facebook ad
  - TikTok script
  - Shopee description
  - Email subject
  - CTA suggestions
  - Hashtags
- Added quality report generation.
- Replaced weak prompt-length and variant-index scoring proxies with technical image screening:
  - contrast readability
  - exposure balance
  - clipped-pixel quality
  - detail signal
  - resolution sufficiency
  - optional reference-palette similarity
- Added saved image-model evaluations with a 40% product-fidelity weight and hard failure tags for altered product condition or identity.

## 7. Review Workflow Updates

Updated workflow statuses:

```text
generated
pending_review
needs_revision
revised
approved
rejected
exported
failed
```

Human-in-the-loop review now supports:

- Editing generated content.
- Selecting the best visual variant manually.
- Saving reviewer notes.
- Marking assets as needing revision.
- Approving assets.
- Exporting final campaign packages.
- Tracking events in an audit trail.

## 8. Export Updates

Updated file:

```text
app/services/export_service.py
```

Export ZIP now includes:

- Best image.
- All variants.
- Original product image.
- Reference image when provided.
- Campaign brief JSON.
- Asset metadata JSON.
- Quality report JSON.
- Caption text.
- Channel-specific content files.
- Reviewer note when available.

## 9. Provider Handling Updates

Updated files:

```text
app/services/visual_service.py
app/config.py
.env.example
README.md
```

Provider improvements:

- Added `cloudflare_inpaint` using `@cf/runwayml/stable-diffusion-v1-5-inpainting` as a background-only fallback for transparent PNG product cutouts.
- Updated the configured chain to `cloudflare_flux,cloudflare_inpaint,replicate_flux,original`; Replicate remains installed as an optional fallback for when credits are available.
- Added provider circuit breaker for the current generation run.
- If a provider fails with quota, billing, authentication, or rate-limit errors, the app skips that provider for the remaining variants in the same run.
- Added safer provider error logging.
- Added configuration warnings for likely wrong provider setup.
- Removed `gemini_image` from the active provider registry and configuration because it is not part of the free image-generation strategy.
- Added `google_imagen` visual provider through the Gemini API Imagen endpoint.

Current configured visual provider chain:

```env
VISUAL_PROVIDER_CHAIN=cloudflare_flux,cloudflare_inpaint,replicate_flux,original
```

Optional Replicate fallback settings:

```env
REPLICATE_FLUX_MODEL_CHAIN=black-forest-labs/flux-kontext-max,black-forest-labs/flux-kontext-pro
REPLICATE_FLUX_REFERENCE_MODEL_CHAIN=flux-kontext-apps/multi-image-kontext-max,flux-kontext-apps/multi-image-kontext-pro
```

When Replicate credit is exhausted, its existing `402`/rate-limit handling allows the chain to proceed to `original` without removing the provider implementation.

Google Imagen settings:

```env
VISUAL_PROVIDER_CHAIN=google_imagen,mock
GOOGLE_IMAGEN_MODEL=imagen-4.0-generate-001
GOOGLE_IMAGEN_ASPECT_RATIO=1:1
```

Important limitation: `google_imagen` is an optional input-aware text-to-image concept generator in this app. It uses Gemini Text/Vision to summarize uploaded product/reference images, then sends those summaries into Imagen. It is not in the default provider chain and is not intended for exact product editing.

## 10. Evaluation Framework

Added file:

```text
docs/evaluation_framework.md
```

Added an academic/product evaluation framework for luxury resale campaigns.

Evaluation criteria:

| Criterion | Weight |
| --- | ---: |
| Product identity preservation | 20% |
| Luxury visual quality | 20% |
| Marketing message fit | 15% |
| Commercial readiness | 15% |
| Human review usefulness | 10% |
| Trust and compliance | 10% |
| System reliability | 10% |

The Streamlit app now includes an image-model benchmark in Evaluation with side-by-side original/output review, structured failure modes, persisted assessments, and per-provider identity-pass and publishable rates.

## 11. Environment Guidance

For the configured Cloudflare path with Replicate retained as an optional fallback:

```env
VISUAL_PROVIDER_CHAIN=cloudflare_flux,cloudflare_inpaint,replicate_flux,original
LLM_PROVIDER_CHAIN=gemini_text,mock
```

For Replicate FLUX only:

```env
VISUAL_PROVIDER_CHAIN=replicate_flux,mock
LLM_PROVIDER_CHAIN=gemini_text,mock
```

For clean local/classroom testing without paid image calls:

```env
VISUAL_PROVIDER_CHAIN=mock
LLM_PROVIDER_CHAIN=gemini_text,mock
```

## 12. Retired Gemini Image Provider Logs

Earlier local logs confirmed that the former `gemini_image` provider returned:

```text
provider=gemini_image
ClientError: 429 RESOURCE_EXHAUSTED
```

This appeared in multiple runs, including:

| Time | Asset ID | Result |
| --- | --- | --- |
| 2026-05-15 19:26:58 | `38bcd812-e389-4293-a203-edb85e85a4b1` | `gemini_image` failed with `429 RESOURCE_EXHAUSTED`; app fell back to mock image generation |
| 2026-05-15 19:36:54 | `ee322f0b-11da-4c66-bd4d-f8fcdb9eee4f` | `gemini_image` failed with `429 RESOURCE_EXHAUSTED`; app fell back to mock image generation |

Interpretation:

- The request reached the Gemini API.
- Gemini rejected the image-generation request with HTTP `429`.
- `RESOURCE_EXHAUSTED` means the configured Google project/key has exhausted quota, rate limit, or billing allowance for that model.
- This is not the same as a frontend bug.
- This is not the same as Replicate failing.
- The `gemini_image` visual provider has now been removed from the configured/registered image-generation path; Gemini text analysis remains supported separately.

In that earlier logged run:

```text
gemini_image -> 429 RESOURCE_EXHAUSTED
replicate_flux -> 402 Insufficient credit
mock -> success
gemini_text -> success
```

That earlier app run completed with a mock visual fallback and Gemini Text copy. The current image chain now uses Cloudflare providers, optional Replicate fallback, then the original image fallback.

## 13. Remaining Production Gaps

The app is much stronger than a demo now, but these are still recommended before real production deployment:

- Add user authentication.
- Add Alembic migrations instead of lightweight SQLite migration helpers.
- Move from SQLite to PostgreSQL for multi-user use.
- Add background job queue for long image generation calls.
- Add real object storage such as S3 or Cloud Storage.
- Add automated provider health checks.
- Add formal CLIP/FID/LPIPS or human-evaluation experiments if needed for a stronger academic thesis.
- Add billing/cost tracking per generation.
- Add publishing integrations such as Shopify, Instagram, or CMS export.
