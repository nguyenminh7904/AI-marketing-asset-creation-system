# Product Requirements Document

## Product Vision

Build an AI-assisted marketing workspace that transforms product images and campaign briefs into reviewable, exportable campaign assets for product promotion.

## Objectives

- Allow a business user to define a complete campaign brief
- Generate a professional campaign visual and marketing copy from one product image
- Preserve product identity and condition through prompt constraints and human review
- Support approval, revision, rejection, library browsing, and export
- Present evaluation results clearly for graduation-demo use

## Scope

### In Scope

- Product image upload
- Campaign brief definition
- Scene template selection and prompt control
- Multiple visual variant generation with manual selection
- AI visual generation
- Marketing copy generation
- Optional reference photo upload for visual direction
- Quality scoring
- Human review workflow
- Campaign library
- Exportable marketing package
- Evaluation dashboard
- Demo mode for offline presentation stability

### Out of Scope

- Direct marketplace publishing
- Multi-user permission management
- Real-time collaborative editing
- Advanced asset version control beyond the current review flow
- Training custom image models
- Automated claim verification against external commerce databases

## User Personas

- Seller
- Marketer
- Reviewer
- Demo presenter / student

## User Stories

- As a seller, I want to upload a product image so that I can create a campaign asset from my own product.
- As a marketer, I want to define platform, objective, tone, and funnel stage so that the output fits my campaign.
- As a reviewer, I want to compare the original image with the generated result so that I can catch identity changes.
- As a marketer, I want multiple visual options so that I can choose the strongest campaign asset before review.
- As a reviewer, I want to approve, reject, or request revision so that the workflow has a clear decision gate.
- As a manager, I want a campaign library so that I can review previous assets and reuse approved outputs.
- As a presenter, I want demo mode so that the app still looks complete when external APIs are unavailable.

## Functional Requirements

1. The system must accept a product image upload.
2. The system must allow campaign brief entry for product, brand, platform, objective, funnel stage, audience, tone, and language.
3. The system must expose scene and prompt controls for background, lighting, angle, props, palette, mood, aspect ratio, and identity preservation.
4. The system must generate a visual asset and marketing copy from the brief.
5. The system must support 1 to 4 visual variants per generation request.
6. The system must score each generated variant and display readable 0-100 quality scores.
7. The system must identify a recommended variant but require manual selection before review.
8. The system must show clear review status labels.
9. The system must allow human review actions: approve, request revision, and reject.
10. The system must save campaign records and review decisions when persistence is available.
11. The system must present a campaign library in a business-friendly layout.
12. The system must provide an evaluation view with summary metrics and charts.
13. The system must allow an optional reference photo to guide scene and composition without overriding product identity.

## Non-Functional Requirements

- The app should open successfully on a local machine.
- The UI should be understandable to non-technical business users.
- The workflow should remain stable even if external APIs are unavailable.
- Generated outputs should be stored and retrievable from the backend.
- The app should avoid exposing secrets or hardcoded production API endpoints.
- Existing provider fallback logic should remain intact.

## AI Requirements

- Visual generation must prioritize product identity preservation.
- Copy generation must avoid unsupported claims unless facts are explicitly provided.
- The copy response should include claim-safety guidance.
- The system should retain a demo-safe fallback mode.
- Human review must remain part of the workflow for business use.

## Multiple Variant Generation

The system generates several creative alternatives from the same brief so the user can compare options before review.

- The default request uses 3 variants, with a hard cap of 4 to keep the demo responsive.
- All variants share the same identity lock and campaign brief.
- Each variant changes only composition, lighting, mood, and scene styling.
- The system marks the highest-scoring variant as recommended, but the user still manually selects the final asset.
- Only the selected variant is used for Review and Export.

## Prompt-Control Requirements

The visual prompt must be structured into the following layers:

1. Product identity lock
2. Scene template
3. Campaign context
4. Professional visual direction
5. Negative constraints
6. Optional reference photo guidance when a reference image is uploaded
7. Variant direction for the current option

The copy prompt must include:

- Platform
- Target audience
- Campaign objective
- Funnel stage
- Product facts
- Offer
- Tone of voice
- Copywriting framework
- Language

## Review and Approval Requirements

- The review screen must show the original product photo and the selected generated variant side by side.
- The review checklist must be visible.
- Review actions must include approve, request revision, and reject.
- Reviewer notes must be saved.
- Unsupported claims and condition changes must block easy approval judgment.

## Data Model Overview

Primary records include:

- Asset / campaign metadata
- Product image path
- Reference image path
- Optional reference usage metadata
- Optional custom scene prompt metadata
- Generated image variants
- Selected variant ID
- Selected best variant
- Quality report
- Channel outputs
- Claim-safety data
- Review checklist and reviewer notes
- Export status and timestamps

## Evaluation Metrics

- Total generated variants
- Approved assets
- Rejected assets
- Pending review assets
- Exported packages
- Average quality score
- Publishable rate
- Most common issue

## Acceptance Criteria

- User can upload or select a product image.
- User can define a full campaign brief.
- User can control scene direction professionally.
- User can optionally upload a reference photo and choose what it should guide.
- User can generate visual and copy outputs.
- Output displays a 0-100 score and a readable status label.
- Review tab shows original versus generated image.
- Review checklist is visible.
- Library displays campaign assets in a business-friendly way.
- Evaluation tab explains demo quality clearly.
- Documentation matches the implemented system.

## Risks and Mitigations

### Risk: Product identity drift

Mitigation: identity-preservation prompt rules, review checklist, and human approval gate.

### Risk: Unsupported marketing claims

Mitigation: claim-safety guidance in copy generation and reviewer notes.

### Risk: API outage during demo

Mitigation: demo mode with fallback presentation state and mock providers.

### Risk: Confusing technical UI

Mitigation: business-oriented labels, step-based layout, and campaign workspace framing.
