#!/usr/bin/env python3
import json, subprocess, sys, shlex
from pathlib import Path


DEFAULT_FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
TARGET_SCALES = {
    '720p': (1280, 720),
    '1080p': (1920, 1080),
    '1440p': (2560, 1440),
    '4k': (3840, 2160),
    '2160p': (3840, 2160),
}


def run(cmd):
    subprocess.run(cmd, check=True)


def esc(text):
    return str(text).replace('\\', r'\\').replace(':', r'\:').replace("'", r"\'").replace(',', r'\,')


def overlay_filter(seg, cfg):
    overlays = seg.get('text_overlays') or seg.get('overlays') or []
    if not overlays:
        return None

    defaults = cfg.get('overlay_defaults', {})
    parts = []
    for ov in overlays:
        text = ov.get('text')
        if not text:
            continue
        fontfile = ov.get('fontfile') or defaults.get('fontfile') or DEFAULT_FONT
        fontsize = ov.get('fontsize', defaults.get('fontsize', 64))
        fontcolor = ov.get('fontcolor', defaults.get('fontcolor', 'white'))
        x = ov.get('x', defaults.get('x', '(w-text_w)/2'))
        y = ov.get('y', defaults.get('y', 'h*0.82'))
        alpha = ov.get('alpha', defaults.get('alpha', 1.0))
        start = float(ov.get('start_sec', 0.0))
        end = float(ov.get('end_sec', seg.get('duration_sec', 0)))
        box = 1 if ov.get('box', defaults.get('box', False)) else 0
        boxcolor = ov.get('boxcolor', defaults.get('boxcolor', 'black@0.28'))
        boxborderw = ov.get('boxborderw', defaults.get('boxborderw', 24))
        line_spacing = ov.get('line_spacing', defaults.get('line_spacing', 8))
        shadowcolor = ov.get('shadowcolor', defaults.get('shadowcolor', 'black@0.45'))
        shadowx = ov.get('shadowx', defaults.get('shadowx', 0))
        shadowy = ov.get('shadowy', defaults.get('shadowy', 3))
        borderw = ov.get('borderw', defaults.get('borderw', 0))
        bordercolor = ov.get('bordercolor', defaults.get('bordercolor', 'white@0.0'))
        enable = ov.get('enable') or f'between(t,{start},{end})'
        draw = (
            f"drawtext=fontfile='{esc(fontfile)}':"
            f"text='{esc(text)}':"
            f"fontsize={fontsize}:fontcolor={fontcolor}:"
            f"x={x}:y={y}:alpha={alpha}:"
            f"line_spacing={line_spacing}:"
            f"shadowcolor={shadowcolor}:shadowx={shadowx}:shadowy={shadowy}:"
            f"borderw={borderw}:bordercolor={bordercolor}:"
            f"box={box}:boxcolor={boxcolor}:boxborderw={boxborderw}:"
            f"enable='{enable}'"
        )
        parts.append(draw)
    return ','.join(parts) if parts else None


def target_scale_filter(cfg):
    target = str(cfg.get('target_resolution', '1080p')).lower()
    dims = TARGET_SCALES.get(target)
    if not dims:
        return None
    w, h = dims
    return f'scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:black'


def main():
    if len(sys.argv) != 2:
        print('Usage: ffmpeg_assemble.py <project-dir>', file=sys.stderr)
        return 2
    project = Path(sys.argv[1]).resolve()
    cfg = json.loads((project / 'project.json').read_text())
    assets = project / 'assets'
    out = project / cfg.get('final_output', 'final.mp4')
    out.parent.mkdir(parents=True, exist_ok=True)
    work = project / 'ffmpeg-build'
    work.mkdir(exist_ok=True)

    shots = cfg.get('timeline_segments') or []
    if not shots:
        raise SystemExit('project.json missing timeline_segments')

    concat = work / 'concat.txt'
    lines = []
    for i, seg in enumerate(shots, start=1):
        src = project / seg['source']
        trim = work / f'seg-{i:03d}.mp4'
        ss = str(seg.get('start_sec', 0))
        dur = str(seg.get('duration_sec', 3))
        vf = []
        if seg.get('zoom_in'):
            vf.append('scale=iw*1.06:ih*1.06,crop=iw/1.06:ih/1.06')
        seg_overlay = overlay_filter(seg, cfg)
        if seg_overlay:
            vf.append(seg_overlay)
        cmd = ['ffmpeg', '-y', '-ss', ss, '-i', str(src), '-t', dur]
        if vf:
            cmd += ['-vf', ','.join(vf)]
        cmd += ['-an', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', str(trim)]
        run(cmd)
        lines.append(f"file '{trim}'\n")
    concat.write_text(''.join(lines))

    stitched = work / 'stitched.mp4'
    run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', str(concat), '-c', 'copy', str(stitched)])

    audio_inputs = []
    filters = []
    idx = 1
    narration = assets / 'audio' / cfg.get('narration_file', '') if cfg.get('narration_file') else None
    music = assets / 'music' / cfg.get('music_file', '') if cfg.get('music_file') else None
    cmd = ['ffmpeg', '-y', '-i', str(stitched)]
    if narration and narration.exists():
        cmd += ['-i', str(narration)]
        audio_inputs.append(('narration', idx))
        idx += 1
    if music and music.exists():
        cmd += ['-i', str(music)]
        audio_inputs.append(('music', idx))
        idx += 1

    if len(audio_inputs) == 2:
        n_idx = audio_inputs[0][1]
        m_idx = audio_inputs[1][1]
        filters.append(f'[{m_idx}:a]volume={cfg.get("music_volume", 0.18)}[musiclow]')
        filters.append(f'[musiclow][{n_idx}:a]amix=inputs=2:duration=first:normalize=0[aout]')
        cmd += ['-filter_complex', ';'.join(filters), '-map', '0:v:0', '-map', '[aout]']
    elif len(audio_inputs) == 1:
        cmd += ['-map', '0:v:0', '-map', f'{audio_inputs[0][1]}:a:0']
    else:
        cmd += ['-map', '0:v:0']

    final_vf = []
    scale_filter = target_scale_filter(cfg)
    if scale_filter:
        final_vf.append(scale_filter)

    subtitles = cfg.get('subtitle_srt')
    if subtitles and (project / subtitles).exists():
        final_vf.append(f"subtitles={shlex.quote(str(project / subtitles))}")

    if final_vf:
        cmd += ['-vf', ','.join(final_vf)]

    cmd += ['-c:v', 'libx264', '-c:a', 'aac', '-shortest', str(out)]
    run(cmd)
    print(out)


if __name__ == '__main__':
    raise SystemExit(main())
