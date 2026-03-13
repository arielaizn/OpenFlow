# Grok Image-to-Video via Kie.ai

## Confirmed API flow

Grok image-to-video uses the same two-step Kie.ai pattern:
1. `POST https://api.kie.ai/api/v1/jobs/createTask`
2. `GET https://api.kie.ai/api/v1/jobs/recordInfo?taskId=...`

Authentication:
- `Authorization: Bearer <KIE_AI_API_KEY>`

## Confirmed model names

Use these exact model identifiers:
- `grok-imagine/image-to-video`
- `grok-imagine/upscale`

## Image-to-video request shape

```json
{
  "model": "grok-imagine/image-to-video",
  "input": {
    "image_urls": ["https://public.example/shot01.png"],
    "prompt": "camera pushes in slowly as fabric moves naturally in the wind",
    "mode": "normal",
    "duration": "6",
    "resolution": "480p"
  }
}
```

## Image-to-video notes

- External-image flow supports one reference image URL.
- Do not send `image_urls` and `task_id` together.
- `mode` options: `fun`, `normal`, `spicy`
- When using external image URLs, `spicy` is not supported and falls back to `normal`.
- `duration` options: `6`, `10`, `15`
- `resolution` options: `480p`, `720p`

## Upscale request shape

```json
{
  "model": "grok-imagine/upscale",
  "input": {
    "task_id": "<grok-task-id>"
  }
}
```

## Practical workflow

1. Animate the approved still with `grok-imagine/image-to-video` first.
2. Review the result for commercial usability.
3. If the Grok result is good enough, run `grok-imagine/upscale` on the Grok task id.
4. If the Grok result is not good enough, switch to Kling for the retry.

## Quality-fail triggers for Grok fallback

Treat the Grok animation as not good enough when one or more of these are clearly present:
- face or body distortion
- broken or jittery motion
- melted details or unstable edges
- main subject loses shape or identity
- the shot looks too visibly AI-generated for ad use

When this happens:
1. log the failure briefly
2. keep the same approved still
3. retry animation in Kling instead of forcing Grok through

## Resolution truthfulness

The provided docs confirm Grok image-to-video input options of `480p` and `720p`, but they do **not** state an exact numeric maximum output resolution for `grok-imagine/upscale`.

So do not claim a confirmed Grok-upscale ceiling that the docs do not provide.
Use this honest policy instead:
- treat `720p` as the highest documented Grok generation input resolution
- run `grok-imagine/upscale` on successful Grok outputs
- require the **final delivered render** to be at least `1080p`
- if the workflow cannot produce a believable 1080p final deliverable, block delivery instead of pretending the source upscale guarantees it

## Default operating preference

Unless the brief says otherwise:
- try Grok first for cost efficiency
- use `duration: "6"`
- use `resolution: "720p"` for the first Grok pass by default
- upscale successful Grok outputs to the maximum available documented path through `grok-imagine/upscale`
- require final delivery at `1080p` or better
- use Kling as fallback when Grok quality is not good enough
