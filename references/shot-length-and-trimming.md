# Shot Length and Trimming Policy

## Core rule

Do not assume the generated shot length should equal the final edit length used on the timeline.

Prefer generating slightly longer raw shots, then using only the strongest part of each shot in the final edit.

## Default policy

Unless the user explicitly asks for longer held shots:
- generate raw animated shots at about 5 seconds each
- use about 3 seconds of each shot in the final edit by default
- trim away weaker startup and settle frames

This is not only for 45-second videos. Treat it as the normal editing bias for high-energy short-form work.

## Why

Generated clips often contain:
- weak startup frames
- repetitive mid-motion
- slow settle frames

Using the whole 5 seconds usually makes the edit feel slower and less intentional than necessary.

## Timeline planning rule

When estimating scene count, separate:
- raw generation duration
- final used timeline duration

Example:
- Want a 45s energetic ad
- Generate around 15 raw shots x 5s
- Use around 15 edited segments x ~3s
- The final cut can still land near 45s while feeling denser because trims, overlaps, repeated inserts, and structure are intentional

## Per-shot edit decision

For every generated shot, decide:
- best in-point
- best out-point
- whether the strongest 3 seconds are enough
- whether the shot deserves longer than 3 seconds because it is a hero moment

## Exceptions

Hold longer only when there is a reason, such as:
- hero product beauty shot
- emotional payoff
- premium slow-breathing moment
- a narration line that needs visual room

## Delivery rule

In `edit-plan.md`, note when the workflow is using:
- raw shot duration
- final used duration

This prevents confusion between "5-second generated clip" and "3-second timeline usage".
