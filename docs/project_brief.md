# Project Brief

## Project Title

AI Marketing Asset Creation System for Product Promotion

## Background

Small and medium online sellers, luxury resale sellers, social-commerce sellers, and product marketing teams often need attractive campaign visuals and persuasive copy, but they do not always have access to dedicated designers, copywriters, or a structured production workflow. As a result, product promotion is often inconsistent, time-consuming, and difficult to scale.

This project turns a single product image and a campaign brief into a campaign-ready marketing workspace. It helps business users create visual assets and marketing copy while keeping product identity, condition, and claim safety under human review.

## Problem Statement

Existing AI image tools are usually optimized for one-off generation, not for business workflow. They often lack:

- Clear campaign planning inputs
- Product identity preservation controls
- Structured copy generation for different channels
- Quality scoring and review checkpoints
- Exportable campaign packages
- Campaign history and evaluation views

The result is a gap between AI-generated content and a production-ready marketing process.

## Target Users

- Small and medium online sellers
- Luxury resale sellers
- Social-commerce operators
- Product marketing teams
- Student teams preparing graduation demo projects in marketing technology

## User Personas

### 1. Online Seller

Needs to turn product photos into attractive listings quickly without hiring a designer.

### 2. Luxury Resale Seller

Needs high-quality visuals, but must avoid changing labels, wear, or authenticity cues.

### 3. Social-Commerce Marketer

Needs campaign assets for Instagram, TikTok, Facebook, and marketplace channels.

### 4. Reviewer / Team Lead

Needs to inspect the generated image, approve or reject the output, and ensure claim safety.

## Business Value

- Reduces the time needed to create campaign-ready assets
- Improves consistency of product presentation across channels
- Helps sellers communicate more professionally
- Supports safer marketing by keeping unsupported claims under review
- Provides a clear graduation-demo narrative for AI-assisted marketing production

## Core Workflow

1. Upload product image
2. Define campaign brief
3. Select scene template and prompt controls
4. Generate visual and copy assets
5. Review original and generated output side by side
6. Approve, request revision, or reject
7. Save to campaign library
8. Export a campaign package
9. Review evaluation results in the dashboard

## Optional Reference Photo Guidance

The system supports an optional reference photo alongside the required product photo.

- The product photo is the source of truth for product identity, label, color, material, and condition.
- The reference photo is only visual guidance for scene, lighting, pose, layout, background mood, and display style.
- This helps non-technical users get stronger creative direction without writing detailed prompts.
- The prompt builder keeps product-identity protection locked above reference guidance.
- When a provider does not support multi-image conditioning, the reference photo is still saved and used as prompt guidance.

## Multiple Variant Generation

The system can generate several creative options from the same campaign brief so the user can compare alternatives before review.

- The default flow generates 3 variants, with 1 to 4 variants supported to keep the demo fast and manageable.
- Each variant keeps the same product-identity lock but varies composition, lighting, mood, and scene styling.
- The UI marks the highest-scoring option as recommended, but the user still manually selects the final variant.
- Only the selected variant moves into Review, which preserves the human-in-the-loop workflow.
- This helps the system feel like a real marketing production workspace rather than a one-shot image generator.

## AI Role

The AI system is responsible for:

- Generating campaign visuals from the uploaded product image
- Producing marketing copy for the selected platform and funnel stage
- Summarizing visible product details for copy generation
- Scoring output quality with technical signals
- Assisting with claim-safety analysis

## Human-in-the-Loop Role

Human review remains mandatory for:

- Product shape, label, logo, and material verification
- Visible condition checks
- Approval of marketing claims
- Final publishability decisions
- Variant choice before review and export

The system is designed for assisted marketing asset production, not fully autonomous publishing.

## Expected Demo Outcome

The demo should show a user uploading a product image, defining a campaign brief, generating a styled campaign asset, reviewing the output, approving or revising it, and exporting a ready-to-share campaign package.

## Graduation Project Positioning

This project is positioned as a graduation-level AI product design and implementation effort that combines:

- Product thinking
- Human-in-the-loop AI workflow
- Marketing content generation
- Visual generation and scoring
- Persistence and export design
- Evaluation and review UX

It demonstrates practical AI-assisted business automation rather than fully autonomous content publishing.
