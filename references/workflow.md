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
- default to about a 5-second raw clip
- use 9:16 or 16:9 aspect ratio
- enable multishot only when it clearly improves the scene
- plan to keep only the strongest ~3 seconds on the final timeline for energetic edits unless a shot deserves a longer hold

Track returned task IDs and clip URLs.

## 5. Voice

Generate narration scene-by-scene or as one continuous voice file.
Prefer one clean full narration file when timing is stable; prefer per-scene files when timing is still moving.

## 6. Music

Do not wait for a follow-up prompt when the video clearly needs music.

Preferred order:
- if external sourcing is allowed, search for a strong candidate track on the web first
- if sourcing fails, is blocked, or sounds weaker than needed, generate a custom instrumental track via Kie music
- in this setup, prefer Kie music model `V5` with `customMode: true` and `instrumental: true`

After choosing the music:
- wire it into the edit immediately
- retime key cuts to major beats where useful
- re-check narration coverage so the ending does not feel empty or under-voiced

## 7. ffmpeg assembly

Create a project folder per video job.
Suggested structure:
- `project.json`
- `assets/images/`
- `assets/video/`
- `assets/audio/`
- `assets/music/`
- `subtitles.srt` (optional)
- `ffmpeg-build/` (generated)

Populate `project.json` with timeline segment metadata including:
- `source`
- `start_sec`
- `duration_sec`
- optional emphasis flags like `zoom_in`
- `narration_file`
- `music_file`
- optional `subtitle_srt`
- `final_output`

Run `scripts/ffmpeg_preflight.py <project-dir>` before render.
Run `scripts/ffmpeg_assemble.py <project-dir>` for final render.

## 8. Render

Export final MP4 with ffmpeg.
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
