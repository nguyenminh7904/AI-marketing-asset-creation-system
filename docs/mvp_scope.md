# MVP Scope

## Must-Have Features

- Product image upload
- Campaign brief form
- Scene template selection
- Flexible prompt controls for background, lighting, angle, props, palette, and mood
- Optional reference photo upload for visual direction
- Optional advanced custom scene prompt
- Multiple visual variants per campaign, with manual selection before review
- AI visual generation
- Marketing copy generation
- 0-100 quality score display
- Review tab with side-by-side comparison
- Approve / request revision / reject actions
- Campaign library
- Exportable campaign package
- Evaluation dashboard
- Demo mode fallback

## Should-Have Features

- Claim-safety notes in copy output
- Reviewer notes persistence
- Raw data expander for debugging or admin inspection
- Status labels such as ready for review, usable with inspection, and needs regeneration
- Charts in the evaluation dashboard
- API health or configuration visibility

## Could-Have Features

- Prebuilt sample campaign briefs
- More scene templates and seasonal presets
- Additional platform-specific copy variants
- Simple compare view for multiple generations
- Campaign duplication or reuse

## Out-of-Scope Features

- Automatic publishing to social or marketplace platforms
- Team accounts and permissions
- Payment processing
- Training a custom image model
- Real-time collaboration
- Large-scale analytics warehouse integration

## Demo Success Criteria

- The application opens without errors.
- The user can complete the full campaign workflow.
- The output feels like a real marketing workspace rather than a raw image generator.
- The review flow clearly shows human oversight.
- The evaluation page communicates that the system is assisted, not autonomous.

## Multiple Variant Generation

- Default to 3 variants per campaign.
- Allow 1, 2, 3, or 4 variants from the Studio.
- Show the generated variants in a simple comparison grid.
- Mark the highest-scoring variant as recommended, but require the user to choose the final asset manually.
- Send only the selected variant to Review and Export.

## Optional Reference Photo Guidance

The reference photo is an optional creative aid, not the product identity source.

- Product photo controls item identity and must always remain the source of truth.
- Reference photo controls scene inspiration such as layout, lighting, background mood, pose, and composition.
- The feature is hidden behind the advanced workflow so the default path stays simple.
- If a provider cannot condition on multiple images, the reference photo is still saved and used as prompt guidance.

## MVP User Journey

1. Open Studio.
2. Upload a product image.
3. Fill in campaign brief details.
4. Choose a scene template and professional prompt controls.
5. Generate multiple campaign variants.
6. Compare the variants and choose the best one.
7. Send the selected variant to Review.
8. Approve, revise, or reject the asset.
9. Find the asset in the Library.
10. Export the campaign package.
11. Inspect evaluation metrics and quality summary.
