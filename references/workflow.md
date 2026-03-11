# Workflow

## 1. Intake

Capture:
- video goal
- target platform
- duration
- aspect ratio
- language
- narration yes/no
- music yes/no
- visual style
- required brand/product/person assets

## 2. Plan

Build a shot list as JSON or bullet list with:
- `scene_number`
- `duration_sec`
- `visual_prompt`
- `motion_prompt`
- `voice_line`
- `music_note`

## 3. Image generation

Generate scene stills with nano-banana-2.
Use one polished prompt per scene.

## 4. Animation

Send stills to Kling through Kie.ai as image-to-video jobs.
For each scene:
- upload the still to a temporary public URL first
- use that URL as the scene reference image
- write a dedicated animation prompt focused on camera movement, motion, and pacing
- default to a 5-second clip
- use 9:16 or 16:9 aspect ratio
- enable multishot only when it clearly improves the scene

Track returned task IDs and clip URLs.

## 5. Voice

Generate narration scene-by-scene or as one continuous voice file.
Prefer one clean full narration file when timing is stable; prefer per-scene files when timing is still moving.

## 6. Music

If requested, either:
- generate music via the configured Kie/music route
- or attach a suitable sourced track if the user supplied one

## 7. Remotion assembly

Create a project folder per video job.
Suggested structure:
- `project.json`
- `assets/images/`
- `assets/video/`
- `assets/audio/`
- `src/Root.tsx`
- `src/Composition.tsx`

## 8. Render

Export final MP4.
Store alongside source assets.

## 9. Review loop

If the user wants revisions, identify whether the problem is:
- concept
- prompt
- identity consistency
- motion
- narration tone
- pacing/edit
- music

Revise the narrowest layer possible.
