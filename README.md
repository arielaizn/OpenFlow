# OpenFlow

OpenFlow is an OpenClaw skill for building short-form AI videos from a simple idea.

It is designed for workflows where one agent coordinates the full stack:

- story and scene planning
- prompt polishing
- consistent character setup
- image generation with Kie.ai
- image-to-video animation with Kling via Kie.ai
- voice design and narration with ElevenLabs
- assembly and rendering with Remotion

This repo contains the skill definition plus the helper scripts and reference material needed to run that pipeline in a real OpenClaw workspace.

## What makes it different

OpenFlow is not just a prompt template.
It is a production-oriented workflow for turning a rough creative ask into a structured video pipeline.

It supports ideas like:

- "Create a 30-second vertical promo"
- "Build a short story video with a recurring character"
- "Generate scene stills, animate them, narrate them, and render the final MP4"
- "Keep one character consistent across all shots"

A key design principle in this repo is **continuity first**:
when a recurring character is needed, the workflow creates a clean passport-style reference image first and then reuses it as the identity anchor for later scenes.

## Core pipeline

OpenFlow is built around this sequence:

1. **Spark ideation first**
   - use the `creative-seeds` companion skill internally to break stale pattern-thinking before story and scene design
2. **Plan the video**
   - define goal, duration, aspect ratio, tone, and scene list
2. **Create a recurring character reference if needed**
   - generate a white-background passport-style identity image first
3. **Generate scene stills**
   - create polished prompts and generate scene images with Kie.ai
4. **Animate scenes with Kling**
   - upload scene images to temporary public URLs
   - animate each shot as image-to-video
5. **Create voice**
   - use ElevenLabs Voice Design when a tailored narrator voice helps
   - render narration audio
6. **Add music**
   - generate or attach a music bed when it improves the final result
7. **Assemble in Remotion**
   - place scenes, voice, and music on a clean timeline
8. **Render final video**
   - export a vertical or horizontal MP4

## Screenshots

### Character passport reference

![Yoav passport reference](assets/screenshots/yoav-passport.png)

### Example generated scenes

![Scene 1](assets/screenshots/scene-1.png)
![Scene 3](assets/screenshots/scene-3.png)
![Scene 5](assets/screenshots/scene-5.png)


## Companion skills

This repo now ships with companion quality-control skills that are meant to be used alongside OpenFlow:

- `video-editing-director` — editing judgment for cuts, pacing, trim points, and scene order
- `openflow-requirements-guard` — requirement checklist / gatekeeper for user-mandated workflow steps
- `remotion-preflight-review` — pre-render inspection before final export
- `video-delivery-auditor` — post-render evidence-based QA before claiming completion

Packaged `.skill` files for these companions are included under `dist/`.

The workflow is now hardened with required proof artifacts before render/delivery:
- `delivery-checklist.md`
- `edit-plan.md`
- `preflight-report.md`
- `delivery-audit.md`

## Repository structure

```text
OpenFlow/
├── SKILL.md
├── README.md
├── dist/
│   ├── kie-video-studio.skill
│   ├── video-editing-director.skill
│   ├── video-delivery-auditor.skill
│   ├── remotion-preflight-review.skill
│   └── openflow-requirements-guard.skill
├── assets/
│   └── screenshots/
├── references/
│   ├── kling-kie.md
│   ├── prompt-patterns.md
│   └── workflow.md
└── scripts/
    ├── elevenlabs_tts.py
    ├── kie_job_client.py
    └── remotion_bootstrap.sh
```

## Files

### `SKILL.md`
The main OpenClaw skill definition.
It explains when to use the skill and how the workflow should behave.

### `references/workflow.md`
A higher-level flow for intake, planning, asset creation, animation, voice, music, Remotion assembly, and revision loops.

### `references/prompt-patterns.md`
Prompt patterns for scene stills, Kling motion prompts, narration tone, and music intent.

### `references/kling-kie.md`
Working notes for Kling via Kie.ai, including the model name that worked in practice and the behavior discovered while testing.

### `scripts/kie_job_client.py`
A generic Kie.ai helper for:
- creating jobs
- polling job status
- waiting for completion

### `scripts/elevenlabs_tts.py`
A minimal ElevenLabs speech helper for generating narration audio files.

### `scripts/remotion_bootstrap.sh`
Bootstraps a minimal Remotion project for timeline assembly and local rendering.


### `dist/`
Packaged `.skill` artifacts ready to install or publish:
- the updated `kie-video-studio.skill`
- the companion QA / editing skills bundled with this repo


Additional editorial rule now enforced: narration-to-visual alignment. If the voiceover mentions a concrete thing or event, the concurrent shot should show that thing, its consequence, or an obvious supporting visual.

Additional pacing rule now enforced: generated clips may be around 5 seconds as raw material, but energetic edits should usually keep only the strongest ~3 seconds of each shot unless a hero moment deserves longer.

## Confirmed working pieces

This repo was built from real end-to-end testing in an OpenClaw workspace.
The following pieces were verified in practice:

- Kie.ai image generation workflow
- Kling via Kie.ai using `kling-3.0/video`
- ElevenLabs voice generation
- ElevenLabs Voice Design workflow compatibility
- Remotion project bootstrap and rendering
- final vertical MP4 export from a multi-stage generated workflow

## Kling notes discovered in practice

The most important confirmed behavior so far:

- working model id: `kling-3.0/video`
- `kling-3.0` without `/video` did not work in this environment
- a minimal working payload included:
  - `prompt`
  - `image_urls`
  - `duration: "5"`
  - `aspect_ratio: "9:16"`
  - `mode: "std"`
  - `multi_shots: false`
  - `sound: false`
- omitting `sound` triggered a `422 sound cannot be empty` error in testing
- some Kling jobs returned temporary `500 internal error`, and retries with a fresh URL plus a slightly simpler prompt helped

These findings are documented so future runs do not need to rediscover them from scratch.

## Expected environment

OpenFlow assumes an environment with:

- Python 3
- Node.js and npm
- an OpenClaw workspace
- network access for the required APIs
- credentials available outside version control

Typical external services used by the workflow:

- **Kie.ai** for image generation and Kling animation
- **ElevenLabs** for voice design and narration
- **Remotion** for assembly and render

## Credentials and safety

No API keys are included in this repository.

The helper scripts are written to load credentials from environment variables or local credential files that live **outside** the repo.

This repo is intentionally safe to publish because it does **not** include:

- API keys
- secrets
- credential files
- private user assets
- generated output folders from real jobs

## What this repo is for

This repository is best viewed as:

- a reusable OpenClaw skill
- a reference implementation for AI-assisted video workflows
- a base for building stronger creative automations over time

It is not meant to be a full commercial SaaS or standalone GUI app.
It is the workflow layer that teaches an agent how to orchestrate the moving parts.

OpenFlow now also assumes a creative pre-ideation step powered by the companion `creative-seeds` skill, which helps break repetitive AI pattern-thinking before scene design.

## Recommended next upgrades

Good follow-up improvements for this repo include:

- adding subtitle / caption generation
- adding reusable project templates for different video styles
- improving music generation and mixing
- documenting more exact Kling payload variants as they are discovered
- adding sample project manifests
- adding thumbnail generation as a default side-output

## Summary

OpenFlow turns a vague video request into a structured pipeline:
idea → scenes → images → animation → voice → music → Remotion → final render.

If you are building agent-driven content workflows inside OpenClaw, this repo is a strong starting point.
