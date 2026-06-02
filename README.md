# AI Marketing Asset Creation System

AI Marketing Asset Creation System turns a raw product photo into a reviewable marketing package: edited product visuals, platform-specific copy, quality scoring, human review, and exportable campaign assets.

The project is designed as a graduation-level marketing technology product, not only an API demo.

## Product Workflow

```text
Data: product image + ready-made scene template + optional reference
Processing: secure upload, prompt controls, and provider routing
Retrieval: uploaded reference/image asset retrieval and saved campaign history
LLM / GenAI: Cloudflare image editing and Gemini marketing copy generation
Validation: technical screening, saved image-model benchmark, identity approval gate, and fallback handling
User: one-click Studio plus human review and editing
Monitoring: health diagnostics, provider logs, audit events, and approved export
```

`Retrieval` here means retrieving uploaded visual references and stored campaign assets. The demo does not currently implement document RAG or a vector database.

## Workflow Coverage

| Stage | Implemented Behavior | Evidence / Boundary |
| --- | --- | --- |
| Data | Accepts a product image, selected scene template, and optional reference image or seller details. | Uploads are validated for image type and size before being stored. |
| Processing | Builds controlled scene prompts, prepares provider-specific image input, routes providers, and retains an original fallback. | Product-preservation instructions prohibit new cracks, wear, label changes, or surface damage. |
| Retrieval | Loads uploaded visual references and saved asset/history records for generation, review, evaluation, and export. | This is application asset retrieval, not semantic RAG or vector retrieval. |
| LLM / GenAI | Uses Cloudflare Workers AI FLUX.2 Klein 4B for image editing and Gemini text generation for marketing copy. | Provider gateways expose configured fallback chains. |
| Validation | Computes technical screen indicators, records image-model evaluations and identity assurance, requires reviewer verification for unverified AI edits, and blocks export until approval. | Technical signals are not proof that an opaque product image is unchanged. |
| User | Provides a preset-driven Studio, optional advanced controls, Review, Library, and Evaluation workspaces. | A reviewer must compare the product before approving ordinary AI-edited outputs. |
| Monitoring | Records application/provider logs, configuration warnings, asset status, audit events, and export history. | Suitable for demo operation; no external observability dashboard is included. |

## Demonstrated Strengths

- The primary demo provider is working in live runs: Cloudflare FLUX.2 Klein successfully produced images on **May 25, 2026 at 12:20:35 PM**, **12:35:21 PM**, and **12:35:53 PM**.
- The LLM gateway is working in the same live runs: Gemini `gemini-2.5-flash-lite` generated marketing content while Cloudflare generated the image.
- Provider failure does not silently break the workflow: when image providers were unavailable, the system returned `original_fallback` and continued with copy generation.
- Product-fidelity controls are explicit: ordinary AI edits require identity review, while transparent PNG uploads can use `source_product_overlay` to retain the source product layer in the composed result.
- Human approval is a real gate: an unverified AI-edited output cannot be approved without identity confirmation, and an asset cannot be exported before approval.
- The workflow is auditable: generated assets, selected variants, quality reports, provider identifiers, review actions, and export events are persisted.

## Observed Failures And Limitations

The following behaviors were observed in local application logs during integration testing. Times are recorded in the local log timezone (`+07:00`).

| Date / Time | Component | Observed Failure | System Response | Current Mitigation |
| --- | --- | --- | --- | --- |
| May 25, 2026, 11:51:08 AM | Replicate FLUX Kontext Max | HTTP `402` insufficient credit. | Tried the next configured Replicate model. | Cloudflare is the current free-tier demo editor; Replicate remains optional for paid fallback use. |
| May 25, 2026, 11:51:09 AM | Replicate FLUX Kontext Pro | HTTP `429` throttle while the account had reduced unpaid rate limits. | Proceeded to the next provider. | Replicate remains configured as an optional fallback and will work when credits are available. |
| May 25, 2026, 11:51:11 AM | Former Gemini Image models | HTTP `429 RESOURCE_EXHAUSTED` for both configured image models. | Returned the original product image through `original_fallback`. | `gemini_image` has been removed from the current visual pipeline because it is not part of the free demo strategy. |
| May 25, 2026, 11:51:16 AM | Visual generation run | All configured generative image editors in that run failed. | Completed successfully with `visual_provider=original_fallback` and Gemini text copy. | The identity-safe original fallback remains configured last in the chain. |
| May 25, 2026, after Cloudflare live generation | Opaque JPG AI editing | Fine product surface detail could be reinterpreted, including an observed cracked appearance. | Generation technically succeeded, but product fidelity required review. | Prompts were tightened, ordinary AI edits are marked unverified, approval/export are gated, and transparent PNG overlay is recommended for exact surfaces. |

Earlier experimental logs also show Google Imagen rejecting generation on an unpaid plan and a temporary malformed Gemini copy response before structured-output handling was added. Those providers are not the primary demo image path.

## Core Features

- Guided Studio workflow: choose a campaign preset, upload one product image, and click `Generate Marketing Asset`.
 - Six campaign presets including Luxury Instagram, Clean E-commerce, Premium Facebook, Minimal Studio, Seasonal Campaign, and Product Launch.
- Product-identity lock prompts direct image-editing providers to preserve visible design, color, logo/label, text, texture, hardware, pattern, packaging, and condition while changing only the scene and lighting.
- Automatic source-product overlay for transparent-background PNG uploads, retaining the uploaded product layer over the generated scene instead of accepting regenerated product pixels.
- Optional controls for a style reference, seller details, language, custom direction, and additional variations are kept out of the primary flow.
- Reference-based visual generation through a provider chain:
  - Cloudflare Workers AI FLUX.2 Klein 4B for a fast demo-friendly direct product editor
  - Cloudflare Stable Diffusion Inpainting as a masked background-only fallback for transparent PNG product cutouts
  - Replicate FLUX Kontext Max then Pro as an installed optional fallback when Replicate credits are available
  - Replicate FLUX Multi-Image Kontext Max then Pro as the optional fallback when a style reference is uploaded
  - Original-image fallback that preserves the submitted image if every editor fails
  - Google Imagen available for concept generation only, not the fidelity-critical default path
- LLM gateway for marketing copy:
  - Gemini text model chain reads the original product photo and returns structured, evidence-grounded product analysis plus marketing copy
  - Deterministic local copy fallback for quota or provider outages
- Channel outputs:
  - SEO title
  - Product description
  - Instagram caption
  - Facebook ad
  - TikTok script
  - Shopee description
  - Email subject
  - CTA suggestions
  - Hashtags
- Human review workflow:
  - generated
  - pending_review
  - needs_revision
  - revised
  - approved
  - rejected
  - exported
  - failed
- Editable review fields:
  - Caption
  - Description
  - Hashtags
  - Channel copy
  - Reviewer notes
  - Selected best variant
- Automated technical screen with measurable image signals:
  - Contrast readability
  - Exposure balance and clipped-pixel rate
  - Detail signal and output resolution
  - Reference palette similarity when a scene reference is supplied
  - Source-to-output scene-change signal, explicitly not an identity test
- Saved image-model benchmark in Evaluation:
  - Side-by-side original and generated image comparison
  - Product fidelity weighted at 40% of the model score
  - Failure tags for introduced damage, changed logos/text, changed material/color, geometry problems, obstruction, unrealistic scenes, and scene mismatch
  - Per-provider identity pass rate, publishable rate, average fidelity, and most common failures
- Identity approval gate: ordinary AI-edited products cannot be approved until a reviewer confirms comparison with the original; only source-layer overlay results can claim the uploaded product layer was retained automatically.
- Export package containing images, campaign brief, channel copy, quality report, metadata, and reviewer notes.
- Built-in evaluation rubric for thesis/product assessment.

## Optional Reference Photo Guidance

The Studio supports an optional reference photo in addition to the required product photo.

- The product photo is the identity source for the item being sold.
- The reference photo is only used for scene, lighting, layout, pose, background mood, or display style.
- The default workflow still works with just a product photo, product name, and campaign preset.
- The prompt builder keeps product identity protection locked above reference guidance.
- Providers that support multiple image inputs can use the reference photo directly; otherwise it remains prompt guidance and stored metadata.

## Multiple Variant Generation

The Studio can generate multiple visual options from the same campaign brief so the user can compare and choose the strongest marketing asset.

- The default is 3 variants, with 1 to 4 variants supported.
- All variants keep the same product identity lock and campaign brief.
- Each variant only changes composition, lighting, mood, and scene styling.
- The UI marks the highest-scoring option as recommended, but the user still manually selects the final variant.
- Only the selected variant goes to Review and Export.

## Architecture

```text
ui/streamlit_app.py
  Minimal scene-first Streamlit studio with optional copy controls, review, library management, and a separate evaluation workspace.

app/main.py
  FastAPI routes for generation, asset listing, review updates, file access, event history, and export.

app/core/pipeline.py
  Orchestrates image generation, scoring, marketing copy, and final result assembly.

app/services/
  Visual providers, the LLM gateway and providers, scoring, and export services.

app/repositories/
  SQLAlchemy models and asset repository with audit events.

storage/
  Uploaded images, generated outputs, and exported ZIP files.

docs/evaluation_framework.md
  Academic evaluation framework for luxury-item campaign testing.
```

## Setup

```bash
cd GenAI_for_marketing_business
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python scripts_init_db.py
```

## Run Backend

```bash
uvicorn app.main:app --reload
```

## Run UI

```bash
python -m streamlit run ui/streamlit_app.py
```

Open:

```text
http://localhost:8501
```

## Environment

See [.env.example](.env.example) for the current placeholder set. The UI now loads `.env` automatically, so the same file can be used for backend and Streamlit runs.

For offline or classroom demos, use:

```env
VISUAL_PROVIDER_CHAIN=mock
LLM_PROVIDER_CHAIN=mock
```

## Input Image Requirements

The quality of the source image matters more than adding prompt detail. Upload a clean product image that exposes the real surface, logo or label, hardware, stitching, and visible condition so both the model and reviewer have a trustworthy source of truth.

| Input | Recommended Format | Recommended Resolution | Composition Requirements | Why It Matters |
| --- | --- | --- | --- | --- |
| Product image, highest-fidelity path | Transparent-background `PNG` | At least `1200 x 1200 px`; ideally `1600-2400 px` on the longest edge | One complete product, clean cutout, no clipped edges, even lighting, natural color, visible labels and condition | Enables `source_product_overlay`, retaining the uploaded product layer over the generated scene. |
| Product image, ordinary photo path | High-quality `JPG`, opaque `PNG`, or `WEBP` | At least `1024 x 1024 px`; ideally `1600 px` or more on the longest edge | One product centered clearly, minimal existing background clutter, no heavy filters, blur, glare, hands, or text overlays | Gives the model and reviewer clearer details, but the AI editor can still reinterpret product pixels. |
| Optional scene reference image | `JPG`, `PNG`, or `WEBP` | `1024 x 1024 px` or larger; square images are preferred for the default `1024 x 1024` output | Show background, surface, lighting, camera mood, and composition only; avoid a competing branded product or visible text | Guides atmosphere and layout without becoming a false product source. |

Upload constraints enforced by the application:

- Supported files: `.jpg`, `.jpeg`, `.png`, and `.webp`.
- Maximum size per uploaded image: `12 MB` by default through `MAX_UPLOAD_MB`.
- Default generated canvas: `1024 x 1024 px` through `CLOUDFLARE_IMAGE_WIDTH` and `CLOUDFLARE_IMAGE_HEIGHT`.

Practical guidance:

1. Use a transparent-background PNG whenever product condition, printed text, leather grain, stitching, or small hardware must remain exact.
2. Photograph or cut out the entire product with margin around every edge. Do not crop handles, straps, packaging corners, or shadows needed to understand the shape.
3. Use neutral, soft, even lighting and avoid reflections that hide labels or surface condition.
4. Do not use a lifestyle/reference image as the product image. The product upload is the only source of product identity.
5. Keep the reference image simple: it should communicate scene style, not introduce another item for the model to imitate.

Cloudflare-specific note: the app stores the original uploaded file for review and overlay, but prepares compact inference copies below `512 x 512 px` for Workers AI input. Therefore, a higher-resolution upload is especially valuable for clean transparent cutouts and human verification; it does not by itself guarantee that an opaque AI-edited product will remain unchanged.

## Generation Strategy

For the configured demo path, use Cloudflare Workers AI FLUX.2 Klein 4B as the primary editor, masked Stable Diffusion Inpainting as a conservative background fallback, and leave Replicate installed as a later fallback for when credits become available:

```env
VISUAL_PROVIDER_CHAIN=cloudflare_flux,cloudflare_inpaint,replicate_flux,original
CLOUDFLARE_ACCOUNT_ID=your_account_id
CLOUDFLARE_API_TOKEN=your_workers_ai_token
CLOUDFLARE_IMAGE_MODEL=@cf/black-forest-labs/flux-2-klein-4b
CLOUDFLARE_INPAINT_MODEL=@cf/runwayml/stable-diffusion-v1-5-inpainting
REPLICATE_API_TOKEN=your_replicate_token
REPLICATE_FLUX_MODEL_CHAIN=black-forest-labs/flux-kontext-max,black-forest-labs/flux-kontext-pro
```

Create a Cloudflare API token with Workers AI permission. The provider sends the product photo as `input_image_0` and, when supplied, the scene reference as `input_image_1`. Workers AI requires these input images below `512x512`, so the integration prepares compact PNG input copies for inference while retaining the original upload.

Image editing models can still reinterpret fine material detail on ordinary JPG, WEBP, or opaque PNG inputs. For products where surface condition, stitching, labels, or cracks must be exact, upload a high-resolution transparent-background PNG cutout. The Cloudflare path then fits and overlays that source product layer over the generated scene and reports `source_product_overlay` in the provider result.

Fallback behavior:

- With a transparent-background PNG, if FLUX fails, `cloudflare_inpaint` builds a mask from the transparent background, generates only the surrounding scene, and composites the uploaded product layer back over the result.
- With JPG, WEBP, or opaque PNG input, `cloudflare_inpaint` deliberately does not run because there is no reliable product mask; the chain can try `replicate_flux`.
- `replicate_flux` remains installed as an optional fallback. While the account has no credit, it can fail with HTTP `402` and the chain proceeds safely to `original_fallback`.
- This fallback handles provider failure. Poor but technically successful FLUX outputs must still be rejected through Evaluation/Review or regenerated.

The default configured chain is also ready for paid Replicate use when its credit is restored:

```env
VISUAL_PROVIDER_CHAIN=cloudflare_flux,cloudflare_inpaint,replicate_flux,original
REPLICATE_FLUX_MODEL_CHAIN=black-forest-labs/flux-kontext-max,black-forest-labs/flux-kontext-pro
```

- Cloudflare FLUX.2 Klein edits the supplied product into the selected scene and is the simplest demo path.
- Cloudflare Inpainting replaces background-only regions from a transparent PNG mask and restores the source product layer.
- With only a product photo, the gateway tries FLUX Kontext Max for quality, then Kontext Pro.
- With a product photo and a style reference, it tries FLUX Multi-Image Kontext Max, then Pro, so the product remains image 1 and the reference is used for scene direction.
- If Replicate is unavailable or out of credit, `original` returns the original uploaded image for safe review instead of inventing a replacement product.

Google Imagen can still be tried for visual concept exploration:

```env
VISUAL_PROVIDER_CHAIN=google_imagen,mock
LLM_PROVIDER_CHAIN=gemini_text,mock
```

In this app, `google_imagen` first summarizes uploaded images, then creates an image from text. It can create useful campaign concepts, but should not be used as the primary path when logos, labels, condition, or exact product identity must remain accurate.

The copy workflow uses `app/services/llm_gateway.py`. `gemini_text` tries the configured Gemini text model chain with structured JSON output; `mock` provides deterministic copy when Gemini is unavailable, so image generation is not lost because caption generation failed.

### Grounded Product Description

When `gemini_text` is available, the pipeline sends the **original uploaded product image** to Gemini together with the campaign request. It does not use the generated lifestyle scene as evidence for product attributes. Gemini returns a structured `product_analysis` object containing:

- Detected product type and a careful visible description.
- Visible design details, label/text placement, hardware, color, finish, and condition observations when discernible.
- Buyer-appeal points derived from visible details and seller-provided facts.
- Unknown or unverified details that must not be claimed in public copy.

The generated product description, marketplace copy, caption, and CTA are then written from this grounded observation. The UI displays the product observation above listing copy, and approved export packages include `content/product_analysis.json`. This makes the text attractive for buyers while keeping factual review possible before publication. If Gemini is unavailable and the local `mock` fallback is used, the UI explicitly indicates that image-based product observation was not performed.

## Validation And Approval

The automated evaluation is intentionally limited to technical image screening: contrast readability, exposure balance, clipping, detail signal, output resolution, and optional reference-palette similarity. It does not certify scene realism, prompt adherence, or that an AI-edited JPG or opaque PNG preserves every product detail.

The Evaluation workspace provides the deeper image-generation assessment. It saves side-by-side human comparisons by model/provider, gives product fidelity 40% of the score, records concrete failure modes such as introduced cracks, and reports identity pass and publishable rates. This creates direct evidence for whether a low-cost model such as Cloudflare FLUX.2 Klein is acceptable for the product category.

Approval policy:

1. `cloudflare_flux` or `replicate_flux` outputs without `source_product_overlay` are recorded as unverified AI edits.
2. A reviewer must compare product shape, logo or label, color, material surface, and visible condition with the original before approval.
3. Any changed surface detail, such as introduced cracks, fails product identity validation regardless of visual score.
4. Export is available only after approval.

For the highest-fidelity demo path, provide a high-resolution transparent-background PNG product cutout so Cloudflare generation can return a result marked `source_product_overlay`.

## Monitoring And Audit

- `/health` reports provider chains, credential presence, selected model configuration, upload limits, and actionable configuration warnings.
- `logs/app.log` records pipeline starts/completions, provider attempts, quota or billing failures, and fallback behavior.
- `/assets/{asset_id}/events` exposes stored audit events for creation, review updates, identity-confirmation payloads, and export activity.
- `/assets/{asset_id}/evaluation` stores a structured image-model assessment after original/output comparison.
- `/evaluation/image-models` aggregates saved assessments into provider-level fidelity and publishability results.
- SQLite persists generated variants, provider identifiers, scores, quality reports, selected image, review state, and export state.

## Database Notes

The app uses SQLite for local development. Startup calls `init_db()` and applies lightweight SQLite-safe migrations for new asset columns. The current schema tracks campaign brief data, generated assets, quality reports, editable channel outputs, review status, export status, and audit events.

For a larger production deployment, replace this with Alembic migrations and a managed database such as PostgreSQL.

## Thesis Framing

Recommended positioning:

> AI Product Studio supports small fashion sellers by transforming raw product photos into campaign-ready marketing assets through AI-assisted image generation, marketing copy generation, technical screening, fidelity-focused model evaluation, and human-in-the-loop approval.

Use the automated score as a technical screen, not proof of product accuracy. Use saved image-model evaluations to compare providers, and require human product comparison unless the output reports `source_product_overlay`.
