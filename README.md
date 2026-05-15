# AI Product Studio

AI Product Studio is a campaign workspace for small fashion sellers. It turns a raw product photo and campaign brief into reviewable marketing assets: edited product visuals, platform-specific copy, quality scoring, human review, and exportable campaign packages.

The project is designed as a graduation-level marketing technology product, not only an API demo.

## Product Workflow

```text
Campaign brief
Product image + optional reference image
Visual provider chain
Multi-variant generation
Quality scoring and best-variant selection
Channel-specific marketing copy
Human-in-the-loop review and editing
Audit history
Campaign ZIP export
```

## Core Features

- Campaign brief inputs: brand, audience, persona, platform, objective, funnel stage, offer, price, tone, and compliance notes.
- Luxury campaign templates for handbags, watches, silk scarves, and premium leather shoes.
- Reference-based visual generation through a provider chain:
  - Gemini Image
  - Replicate FLUX Kontext
  - Local mock fallback
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
- Quality report with heuristic scoring dimensions:
  - Aesthetic score
  - Prompt alignment proxy
  - Product visibility proxy
  - Reference similarity proxy
  - Brand consistency proxy
  - Commercial readiness proxy
- Export package containing images, campaign brief, channel copy, quality report, metadata, and reviewer notes.
- Built-in evaluation rubric for thesis/product assessment.

## Architecture

```text
ui/streamlit_app.py
  Streamlit workspace for campaign creation, review, editing, library management, and evaluation.

app/main.py
  FastAPI routes for generation, asset listing, review updates, file access, event history, and export.

app/core/pipeline.py
  Orchestrates image generation, scoring, marketing copy, and final result assembly.

app/services/
  Visual providers, LLM providers, scoring, and export services.

app/repositories/
  SQLAlchemy models and asset repository with audit events.

storage/
  Uploaded images, generated outputs, and exported ZIP files.

docs/evaluation_framework.md
  Academic evaluation framework for luxury-item campaign testing.
```

## Setup

```bash
cd ai-product-studio-reference-editing
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
streamlit run ui/streamlit_app.py
```

Open:

```text
http://localhost:8501
```

## Environment

```env
APP_NAME=AI Product Studio Reference Editing
ENV=dev
DATABASE_URL=sqlite:///./app.db
STORAGE_DIR=storage
LOG_LEVEL=INFO

VISUAL_PROVIDER_CHAIN=gemini_image,replicate_flux,mock
GEMINI_API_KEY=
GEMINI_IMAGE_MODEL=gemini-2.5-flash-image
GEMINI_IMAGE_MODEL_CHAIN=gemini-2.5-flash-image,gemini-3-pro-image-preview

REPLICATE_API_TOKEN=
REPLICATE_FLUX_MODEL=black-forest-labs/flux-kontext-pro

LLM_PROVIDER_CHAIN=gemini_text,mock
GEMINI_TEXT_MODEL=gemini-2.0-flash

DEFAULT_VARIANTS=2
REQUEST_TIMEOUT_SECONDS=120
MAX_UPLOAD_MB=12
```

For offline or classroom demos, use:

```env
VISUAL_PROVIDER_CHAIN=mock
LLM_PROVIDER_CHAIN=mock
```

## Database Notes

The app uses SQLite for local development. Startup calls `init_db()` and applies lightweight SQLite-safe migrations for new asset columns. The current schema tracks campaign brief data, generated assets, quality reports, editable channel outputs, review status, export status, and audit events.

For a larger production deployment, replace this with Alembic migrations and a managed database such as PostgreSQL.

## Thesis Framing

Recommended positioning:

> AI Product Studio supports small fashion sellers by transforming raw product photos into campaign-ready marketing assets through AI-assisted image generation, marketing copy generation, heuristic quality evaluation, and human-in-the-loop approval.

Use the scoring as "heuristic quality evaluation" unless you later add formal CLIP, FID, LPIPS, or human evaluation studies.
