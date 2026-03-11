# Kling via Kie.ai

## Confirmed API flow

Kling jobs use the same two-step Kie.ai pattern as other models:
1. `POST https://api.kie.ai/api/v1/jobs/createTask`
2. `GET https://api.kie.ai/api/v1/jobs/recordInfo?taskId=...`

Authentication:
- `Authorization: Bearer <KIE_AI_API_KEY>`

## Confirmed model name

Use this exact model identifier:
- `kling-3.0/video`

## Confirmed documented input

Minimal documented request shape:

```json
{
  "model": "kling-3.0/video",
  "input": {
    "mode": "std"
  }
}
```

### input.mode
- `std` = standard resolution
- `pro` = higher resolution

## Response shape

Create task returns:
- `data.taskId`

Query task returns:
- `data.state` -> `waiting | success | fail`
- `data.resultJson` -> JSON string containing `resultUrls`

Example success result payload:

```json
{
  "resultUrls": [
    "https://.../video.mp4"
  ]
}
```

## Important current limitation

The provided documentation confirms:
- exact model name
- task creation endpoint
- task polling endpoint
- `mode` values

But it does **not yet document** the fields required for:
- image-to-video input
- text-to-video prompt fields
- duration / aspect ratio / camera controls
- start/end frame references
- motion strength or other animation controls

So for now, this skill can safely treat Kling integration as:
- **confirmed generic job transport exists**
- **confirmed model id exists**
- **confirmed mode field exists**
- **full production payload for animating scene stills still needs more model-specific docs**

## Practical guidance

When using Kling through this skill:
- Treat the intended path as image-to-video
- Use a temporary public image URL as the reference input
- Put motion, camera movement, and pacing instructions into the prompt itself
- Default each generated scene clip to 5 seconds
- Prefer 9:16 or 16:9 outputs, not square
- Prefer `mode: pro` for final-quality output when speed/cost allow
- Prefer `mode: std` for tests and rapid iteration
- Enable multishot only when it clearly improves the result
- Use `scripts/kie_job_client.py` for create/wait calls
- Do not hardcode guessed Kling payload fields as if they are confirmed API behavior unless verified in real tests
- If the user supplies more Kling docs later, extend the pipeline from this reference file rather than scattering assumptions through SKILL.md
