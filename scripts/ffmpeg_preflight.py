#!/usr/bin/env python3
import json, sys
from pathlib import Path


DEFAULT_FONT = Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
VALID_TARGETS = {'720p', '1080p', '1440p', '4k', '2160p'}


def main():
    if len(sys.argv) != 2:
        print('Usage: ffmpeg_preflight.py <project-dir>', file=sys.stderr)
        return 2
    project = Path(sys.argv[1]).resolve()
    cfg = json.loads((project / 'project.json').read_text())
    problems = []
    overlay_count = 0
    target_resolution = str(cfg.get('target_resolution', '1080p')).lower()
    segments = cfg.get('timeline_segments') or []
    if target_resolution not in VALID_TARGETS:
        problems.append(f'Unsupported target_resolution: {target_resolution}')
    if target_resolution in {'4k', '2160p'} and len(segments) and not cfg.get('allow_4k_upscale'):
        problems.append('4K delivery requested but allow_4k_upscale is not enabled')
    if not segments:
        problems.append('No timeline_segments in project.json')
    for seg in segments:
        src = seg['source']
        p = project / src
        if not p.exists():
            problems.append(f"Missing clip: {src}")
        dur = float(seg.get('duration_sec', 0))
        if dur <= 0 or dur > 5.1:
            problems.append(f"Unexpected segment duration for {src}: {dur}")
        overlays = seg.get('text_overlays') or seg.get('overlays') or []
        overlay_count += len(overlays)
        for ov in overlays:
            if not ov.get('text'):
                problems.append(f"Overlay missing text for {src}")
            start = float(ov.get('start_sec', 0.0))
            end = float(ov.get('end_sec', dur))
            if start < 0 or end <= start or end > dur + 0.01:
                problems.append(f"Overlay timing invalid for {src}: {start}-{end} within {dur}")
            fontfile = Path(ov.get('fontfile', cfg.get('overlay_defaults', {}).get('fontfile', DEFAULT_FONT)))
            if not fontfile.exists():
                problems.append(f"Overlay font missing for {src}: {fontfile}")
    if cfg.get('narration_file') and not (project / 'assets' / 'audio' / cfg['narration_file']).exists():
        problems.append('Narration file missing')
    if cfg.get('music_file') and not (project / 'assets' / 'music' / cfg['music_file']).exists():
        problems.append('Music file missing')
    report = {
        'pass': not problems,
        'problems': problems,
        'segment_count': len(segments),
        'overlay_count': overlay_count,
        'target_resolution': target_resolution,
        'total_timeline_sec': round(sum(float(s.get('duration_sec', 0)) for s in segments), 2)
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not problems else 1


if __name__ == '__main__':
    raise SystemExit(main())
