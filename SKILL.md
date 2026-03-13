---
name: kie-video-studio
description: >-
  Create full short-form videos from scratch using Kie.ai image/video/music models,
  ElevenLabs voice generation, and ffmpeg-based editing/rendering on the server. Use when the
  user asks to create a full video, ad, teaser, reel, explainer, trailer,
  music-backed short, or talking/voice-led visual pipeline from an idea or script.
  Especially use when the workflow should turn a rough concept into a shot list,
  generate polished prompts for nano-banana-2 image creation, batch-generate still variants,
  animate scenes through Grok or Kling via Kie.ai, generate narration and sound with ElevenLabs,
  optionally source or generate music including Suno/Kie when available, and assemble the
  final edit with ffmpeg.
---

# Kie Video Studio

Build complete videos from an idea, not just isolated assets.

## Companion skills

Use these companion skills alongside this one when relevant:
- `video-preproduction` to lock concept, shot count, batching, and checklist structure before expensive generation starts.
- `video-visual-generation` to handle passport/reference images, 4-variant shot generation, critical still review, prompt correction, and single-frame selection before animation.
- `video-shot-critic` when a shot needs harsher comparative review, systematic defect detection, or prompt rewrites before anything gets animated.
- `video-animation-stage` to animate approved stills into raw clips.
- `video-voice-music-stage` to add Voice Design, narration, and approved music after visuals are mostly locked.
- `video-ffmpeg-finisher` to assemble, preflight, audit, and render the final cut with ffmpeg.
- `openflow-requirements-guard` at job start when the user gives mandatory steps or quality bars.
- `video-editing-director` before timeline assembly so the edit has intentional cuts and pacing.
- `remotion-preflight-review` immediately before final render if a Remotion project is intentionally used; otherwise run the local ffmpeg preflight script before render.
- `video-delivery-auditor` immediately before claiming the video is done.

For hard-gated jobs, require these artifacts before delivery:
- `delivery-checklist.md`
- `edit-plan.md`
- `preflight-report.md`
- `delivery-audit.md`

## Core workflow

1. Decide the output format first.
   - Goal: ad, reel, teaser, explainer, cinematic short, promo, testimonial-style edit
   - Duration target: usually 10–60 seconds unless the user says otherwise
   - Aspect ratio: 9:16 for vertical, 16:9 for landscape, 1:1 for square
2. Break the idea into scenes.
   - 3–8 scenes for simpler short videos; use many more shots/segments when the goal is a denser, more kinetic cut
   - Do not calculate shot count by simply dividing runtime by raw 5-second clip length
   - Separate raw generated shot duration from final used timeline duration
   - For energetic ads and promos, prefer generating more raw shots than the final runtime would suggest, then trimming each raw shot down to its strongest ~3 seconds in the final cut
   - Each scene needs: purpose, visual subject, camera style, motion, duration, voice line, sound intent
3. Generate strong scene prompts.
   - Before ideation-heavy creative work, pull 3 random seeds from the local `creative-seeds` skill and let them shift your thinking internally
   - Use the nano-banana prompt polishing mindset before generating any image
   - Keep visual continuity across scenes: same subject, wardrobe, colors, environment, lighting language
4. Generate stills with nano-banana-2.
   - For each planned shot, generate at least 4 variants before choosing anything
   - Prefer submitting the 4-variant set as one batch/run rather than serial one-by-one generation
   - Compare the batch and select exactly 1 winning still per shot
   - If the whole batch repeats the same distortion or weak composition, rewrite the prompt and regenerate instead of settling
   - Create one approved source image per scene/shot for animation unless the scene truly needs multiple setup options
5. Animate stills through Kie.ai, using Grok first and Kling as fallback.
   - Default first pass: `grok-imagine/image-to-video`
   - Upload each approved scene still to a temporary public URL first, then use that image URL as the reference input
   - Default Grok settings unless the brief says otherwise: `mode: normal`, `duration: "6"`, `resolution: "720p"`
   - Review the Grok result before accepting it
   - If Grok passes, upscale it through `grok-imagine/upscale` using the Grok task id and keep the upscaled result
   - If Grok shows face/body distortion, broken or jittery motion, melted details, identity loss, or looks too visibly AI-generated for ad use, reject it and retry the same approved still in Kling
   - Kling fallback model id: `kling-3.0/video`
   - For Kling fallback, treat the intended workflow as image-to-video
   - Default each animated raw shot to about 5-6 seconds unless the user asks otherwise
   - Do not assume the full generated clip should stay in the final cut; for energetic edits, prefer trimming each shot down to about 3 strong seconds on the timeline unless a hero moment deserves longer
   - Use 9:16 or 16:9, not square, for video outputs
   - Put camera movement, motion feel, pacing, and animation intent directly into the animation prompt
   - Use Kling `mode: std` for tests and `mode: pro` for fallback final output when appropriate
   - Enable multishot only when it clearly improves the scene instead of adding randomness
   - Prefer one clear motion idea per shot
6. Design voices and generate narration with ElevenLabs.
   - Prefer ElevenLabs Voice Design first when the story benefits from a custom voice cast or a specific narrator vibe
   - Choose the best-fitting generated voice(s) for the story, then render the final narration
   - Use the preferred voice from TOOLS.md when a custom voice is not required or when the user explicitly wants it
   - Write final narration with tone/performance cues in square brackets before each line or segment, for example `[softly]`, `[warm]`, `[dramatic]`
   - Keep narration aligned to scene timing
   - Keep narration aligned to what is visually on screen while that line is being spoken; if a line mentions a concrete thing/event, the concurrent shot should show that thing, its consequence, or an obvious supporting visual
7. Add music automatically when the video benefits from it, unless the user explicitly says not to.
   - Do not search the web for music by default.
   - Generate music through the configured Kie/Suno path by default.
   - In this environment, prefer Kie music generation with model `V5`, `customMode: true`, and `instrumental: true` unless vocals were explicitly requested
   - Treat music as incomplete until it is actually wired into the edit/timeline, not just saved as a file
   - Re-check narration timing after music is chosen; if the ending feels under-voiced, shorten the cut or redistribute/add narration instead of leaving dead air by accident
8. Assemble everything with ffmpeg by default.
   - Build a timeline config with clips, trims, voice, music, timing, simple transitions, and `target_resolution`
   - Use `scripts/ffmpeg_preflight.py <project-dir>` before final render
   - Use `scripts/ffmpeg_assemble.py <project-dir>` to render the final MP4 and any requested subtitle burn-in variant
   - Default `target_resolution` to `1080p`
   - Allow `1440p` and `4k` / `2160p` only when the source quality genuinely supports that upscale target
   - Run a real preflight review before final render; do not skip from "assets exist" to delivery
   - For strict workflows, do not render until `delivery-checklist.md`, `edit-plan.md`, `preflight-report.md`, and `logs/animation-selection.md` (when animation applies) exist and the preflight checks pass
   - Final delivery target is 1080p minimum; if the pipeline cannot honestly meet that bar, block delivery instead of bluffing
   - If the user explicitly asked for real animation, do not treat a still-motion / Ken Burns style fallback as equivalent completion; only count the animation requirement as satisfied when actual animated clips were produced by Kling or another real animation stage

## Creative operating rules

- Before brainstorming story beats, scene ideas, visual motifs, or stylistic twists, use `creative-seeds` internally to break stale pattern-thinking.
- Be highly creative in ideation, but highly disciplined in continuity.
- Be honest about what was actually done; if Voice Design or music-in-edit were requested, verify them before claiming success.
- When the user asks for true animation, be explicit with yourself about the difference between animated clips and still-image motion effects; do not blur that distinction in status updates or final delivery language.
- Keep one visual language across the whole video.
- Prefer clear, cinematic shots over noisy prompt soup.
- Treat repeated defects across a shot batch as a prompt/design failure to fix, not as acceptable model weirdness.
- Do not move to animation until each shot has one clearly chosen winner.
- When the user gives a loose concept, invent the shot design yourself.
- When the user gives tight constraints, follow them exactly.
- Default to production-ready outputs, not concept-art chaos.

## Shot design rules

For each scene, decide:
- subject
- action
- environment
- framing
- motion
- lighting
- style
- transition in/out
- narration line
- audio mood
- why the chosen shot visually matches the narration line (if any)
- what 4-image variant batch will best test the shot before selection
- what failure patterns would force a prompt rewrite instead of a blind reroll

Good scene prompt shape:
- subject + action + environment + framing + lighting + style + continuity anchors

Good Kling motion prompt shape:
- camera move + subject motion + environment motion + pacing

## Consistency rules

If a character/product/place recurs across scenes:
- first create a clean white-background "passport" reference image for that recurring character before generating story scenes
- use that passport image as the anchor reference for later image generation
- repeat defining traits in every prompt
- repeat wardrobe/material/color anchors
- repeat camera/lens language when needed
- avoid introducing new props unless the story requires them

## ffmpeg assembly rules

Use ffmpeg for assembly by default, not for inventing the story.

The assembly stage should:
- place clips on a timeline via config/segment metadata
- add voiceover
- add music bed
- control cuts and simple transitions
- optionally burn captions/subtitles
- render the final deliverable

Keep edits clean and fast:
- hard cuts first
- gentle fades only when they add value
- do not overuse flashy transitions
- decide trims and cut points intentionally; do not just drop full clips into the timeline unchanged
- for energetic short-form work, assume the best 3 seconds of a generated 5-second shot are usually stronger than the whole raw clip
- if narration is active, verify the concurrent shot semantically matches the line being spoken

## Music rules

If the video would benefit from music, add it proactively unless the user says not to.
- infer genre from the video goal
- do not search external sites for music by default
- generate a custom instrumental track via Kie/Suno using `V5` by default
- keep music supportive, not dominant over narration
- if using generated music, request instrumental unless vocals are explicitly wanted
- match BPM/energy to the pacing of the scenes
- after adding music, verify it is present in the final timeline/render config before delivery
- after music is in the edit, check the last 10-15 seconds for narration drop-off; shorten or rewrite the ending structure if the close feels empty

## Deliverables

Default deliverables:
- final video file
- scene plan / shot list
- final narration text
- asset manifest (images, clips, audio)
- `delivery-checklist.md`
- `edit-plan.md`
- `preflight-report.md`
- `delivery-audit.md`
- `logs/animation-selection.md` when animation is part of the workflow

Optional deliverables:
- captions/subtitles
- alternate aspect ratio renders
- thumbnail image
- clean project folder for later edits

## Local resources

Use these bundled resources when doing the work:
- `scripts/kie_job_client.py` — generic Kie.ai create/poll helper for any model
- `scripts/elevenlabs_tts.py` — ElevenLabs speech generator
- `scripts/ffmpeg_preflight.py` — validate timeline segments, trims, and required audio inputs before render
- `scripts/ffmpeg_assemble.py` — build trimmed segment files, stitch them, mix narration/music, burn subtitles when requested, and render final MP4
- `references/workflow.md` — detailed decision flow for full video creation
- `references/prompt-patterns.md` — prompt patterns for scene, motion, narration, and music intent
- `references/grok-kie.md` — Grok image-to-video first-pass defaults, upscale flow, and quality-fail triggers for Kling fallback
- `references/kling-kie.md` — confirmed Kie.ai Kling model name, create/poll flow, and currently known payload limits
- `references/music-generation.md` — Kie V5 music generation defaults, sourcing fallback rules, and ending/narration integration checks
- `references/narration-visual-alignment.md` — rules for making the on-screen shot match the narration line while it is spoken
- `references/shot-length-and-trimming.md` — default policy for generating longer raw shots but using tighter ~3 second selections in the final edit
- `../video-voice-music-stage/references/voice-direction-format.md` — required square-bracket format for narration tone cues before ElevenLabs generation

## Practical defaults

Unless the user specifies otherwise:
- short promo / reel duration: 20–35 seconds
- scene count: 4–6
- narration: concise, punchy, spoken naturally
- music: modern instrumental matching the tone
- edit style: clean, premium, high-clarity

## When API details are unclear

Kie.ai model-specific payloads can vary by model/version.
- Reuse the generic job client for create + poll
- Confirm the exact model name and input fields before shipping a production automation if they were not provided in the request or references
- When Grok docs are available and confirmed, prefer Grok as the default first-pass animation path and reserve Kling for fallback quality recovery
- Keep model-specific options in project config files rather than hardcoding assumptions deep in the flow
