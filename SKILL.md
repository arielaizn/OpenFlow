---
name: kie-video-studio
description: >-
  Create full short-form videos from scratch using Kie.ai image/video/music models,
  ElevenLabs voice generation, and Remotion editing on the server. Use when the
  user asks to create a full video, ad, teaser, reel, explainer, trailer,
  music-backed short, or talking/voice-led visual pipeline from an idea or script.
  Especially use when the workflow should turn a rough concept into a shot list,
  generate polished prompts for nano-banana-2 image creation, animate scenes with
  Kling via Kie.ai, generate narration and sound with ElevenLabs, optionally
  source or generate music including Suno/Kie when available, and assemble the
  final edit with Remotion.
---

# Kie Video Studio

Build complete videos from an idea, not just isolated assets.

## Core workflow

1. Decide the output format first.
   - Goal: ad, reel, teaser, explainer, cinematic short, promo, testimonial-style edit
   - Duration target: usually 10–60 seconds unless the user says otherwise
   - Aspect ratio: 9:16 for vertical, 16:9 for landscape, 1:1 for square
2. Break the idea into scenes.
   - 3–8 scenes for short videos
   - Each scene needs: purpose, visual subject, camera style, motion, duration, voice line, sound intent
3. Generate strong scene prompts.
   - Use the nano-banana prompt polishing mindset before generating any image
   - Keep visual continuity across scenes: same subject, wardrobe, colors, environment, lighting language
4. Generate stills with nano-banana-2.
   - Create one source image per scene unless the scene truly needs multiple setup options
5. Animate stills with Kling via Kie.ai.
   - Use the confirmed model id `kling-3.0/video`
   - Treat the intended workflow as image-to-video
   - Upload each scene still to a temporary public URL first, then use that image URL as the reference input
   - Default each animated shot to 5 seconds unless the user asks otherwise
   - Use 9:16 or 16:9, not square, for video outputs
   - Put camera movement, motion feel, pacing, and animation intent directly into the animation prompt
   - Use `mode: std` for tests and `mode: pro` for final output when appropriate
   - Enable multishot only when it clearly improves the scene instead of adding randomness
   - Prefer one clear motion idea per shot
6. Design voices and generate narration with ElevenLabs.
   - Prefer ElevenLabs Voice Design first when the story benefits from a custom voice cast or a specific narrator vibe
   - Choose the best-fitting generated voice(s) for the story, then render the final narration
   - Use the preferred voice from TOOLS.md when a custom voice is not required or when the user explicitly wants it
   - Keep narration aligned to scene timing
7. Add music only if requested or clearly useful.
   - If the user asks for matching music, either source it or generate it through the configured music path (for example Suno via Kie if available)
8. Assemble everything in Remotion.
   - Build a timeline with clips, voice, music, timing, and simple transitions
   - Export a final MP4 and any requested caption/subtitle variants

## Creative operating rules

- Be highly creative in ideation, but highly disciplined in continuity.
- Keep one visual language across the whole video.
- Prefer clear, cinematic shots over noisy prompt soup.
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

## Remotion rules

Use Remotion for assembly, not for inventing the story.

The Remotion stage should:
- place clips on a timeline
- add voiceover
- add music bed
- control cuts and simple transitions
- optionally burn captions
- render the final deliverable

Keep edits clean and fast:
- hard cuts first
- gentle fades only when they add value
- do not overuse flashy transitions

## Music rules

If the video would benefit from music, add it proactively unless the user says not to.
- infer genre from the video goal
- keep music supportive, not dominant over narration
- if using generated music, request instrumental unless vocals are explicitly wanted
- match BPM/energy to the pacing of the scenes

## Deliverables

Default deliverables:
- final video file
- scene plan / shot list
- final narration text
- asset manifest (images, clips, audio)

Optional deliverables:
- captions/subtitles
- alternate aspect ratio renders
- thumbnail image
- clean project folder for later edits

## Local resources

Use these bundled resources when doing the work:
- `scripts/kie_job_client.py` — generic Kie.ai create/poll helper for any model
- `scripts/elevenlabs_tts.py` — ElevenLabs speech generator
- `scripts/remotion_bootstrap.sh` — scaffold a minimal Remotion project in a target folder
- `references/workflow.md` — detailed decision flow for full video creation
- `references/prompt-patterns.md` — prompt patterns for scene, motion, narration, and music intent
- `references/kling-kie.md` — confirmed Kie.ai Kling model name, create/poll flow, and currently known payload limits

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
- Keep model-specific options in project config files rather than hardcoding assumptions deep in the flow
