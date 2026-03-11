# OpenFlow

OpenFlow is an OpenClaw skill for building short-form videos from an idea using a multi-stage pipeline:

- scene planning
- polished image prompting
- image generation via Kie.ai
- scene animation via Kling on Kie.ai
- voice generation via ElevenLabs
- timeline assembly and render via Remotion

## What it includes

- `SKILL.md` — the operating instructions for the skill
- `references/` — workflow and prompt references
- `scripts/kie_job_client.py` — generic Kie.ai create / poll helper
- `scripts/elevenlabs_tts.py` — ElevenLabs text-to-speech helper
- `scripts/remotion_bootstrap.sh` — bootstraps a minimal Remotion project

## Notes

- No API keys are included in this repository.
- Credentials are loaded from environment variables or local credential files outside the repo.
- Kling/Kie payload support in this repo reflects the behavior discovered during real testing and may need updates if the provider changes their API.

## Expected environment

- Python 3
- Node.js + npm
- OpenClaw workspace
- Access to Kie.ai and ElevenLabs credentials outside version control

## Example capabilities

- create a recurring character passport image first
- generate consistent scene stills
- animate scenes with Kling as 5-second image-to-video shots
- design a voice and render Hebrew narration
- assemble and export a final vertical video in Remotion
