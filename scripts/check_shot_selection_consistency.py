#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

SHOT_HEADER_RE = re.compile(r'^##\s+(.*)$')
BULLET_RE = re.compile(r'^-\s+([^:]+):\s*(.*)$')
INLINE_CODE_RE = re.compile(r'`([^`]+)`')
NA_VALUES = {'', 'n/a', 'na', 'none', 'no'}


def norm_path(value: str) -> str:
    value = value.strip().strip('`').strip()
    value = value.replace('\\', '/')
    while value.startswith('./'):
        value = value[2:]
    return value


def basename(value: str) -> str:
    return Path(norm_path(value)).name


def parse_args(argv: List[str]) -> Tuple[Path, bool]:
    fix = False
    args = []
    for arg in argv[1:]:
        if arg == '--fix':
            fix = True
        else:
            args.append(arg)
    if len(args) != 1:
        print('Usage: check_shot_selection_consistency.py [--fix] <project-dir>', file=sys.stderr)
        raise SystemExit(2)
    return Path(args[0]).resolve(), fix


def parse_log(path: Path) -> List[Dict[str, object]]:
    entries: List[Dict[str, object]] = []
    current = None
    in_variants = False
    for raw_line in path.read_text().splitlines():
        line = raw_line.rstrip()
        header = SHOT_HEADER_RE.match(line)
        if header:
            if current:
                entries.append(current)
            current = {
                'shot': header.group(1).strip(),
                'variants': [],
                'selected_winner': '',
                'why_it_won': '',
                'repeated_defect_detected': '',
                'defect_note': '',
                'prompt_rewrite_note': '',
            }
            in_variants = False
            continue
        if current is None:
            continue
        bullet = BULLET_RE.match(line)
        if bullet:
            key = bullet.group(1).strip().lower().replace(' ', '_')
            value = bullet.group(2).strip()
            if key == 'variants':
                in_variants = True
            elif key in current:
                current[key] = value
                in_variants = False
            else:
                in_variants = False
            continue
        stripped = line.strip()
        if in_variants and stripped.startswith('-'):
            codes = INLINE_CODE_RE.findall(stripped)
            if codes:
                current['variants'].extend(codes)
            else:
                current['variants'].append(stripped[1:].strip())
    if current:
        entries.append(current)
    return entries


def autofix_entries(entries: List[Dict[str, object]]) -> List[str]:
    fixes = []
    for entry in entries:
        shot = str(entry.get('shot') or 'unknown shot')
        repeated = str(entry.get('repeated_defect_detected', '')).strip().lower()
        defect_note = str(entry.get('defect_note', '')).strip()
        rewrite_note = str(entry.get('prompt_rewrite_note', '')).strip()

        if defect_note.lower() in NA_VALUES:
            entry['defect_note'] = 'n/a'
        if rewrite_note.lower() in NA_VALUES:
            entry['prompt_rewrite_note'] = 'n/a'

        rewrite_note = str(entry.get('prompt_rewrite_note', '')).strip()
        defect_note = str(entry.get('defect_note', '')).strip()

        if rewrite_note and rewrite_note.lower() not in NA_VALUES and repeated not in {'yes', 'true'}:
            entry['repeated_defect_detected'] = 'yes'
            fixes.append(f'{shot}: set repeated defect detected to yes because prompt rewrite note exists')
            repeated = 'yes'

        if repeated in {'yes', 'true'} and not defect_note:
            entry['defect_note'] = 'auto-filled: repeated defect was indicated; add exact defect description manually if needed'
            fixes.append(f'{shot}: auto-filled missing defect note')

        if repeated not in {'yes', 'true'}:
            if not str(entry.get('defect_note', '')).strip():
                entry['defect_note'] = 'n/a'
            if not str(entry.get('prompt_rewrite_note', '')).strip():
                entry['prompt_rewrite_note'] = 'n/a'
    return fixes


def validate_entries(entries: List[Dict[str, object]]) -> List[str]:
    problems = []
    for idx, entry in enumerate(entries, start=1):
        shot = entry['shot'] or f'entry {idx}'
        variants = [norm_path(v) for v in entry['variants'] if str(v).strip()]
        winner = norm_path(str(entry['selected_winner']))
        why = str(entry['why_it_won']).strip()
        repeated = str(entry['repeated_defect_detected']).strip().lower()
        defect_note = str(entry['defect_note']).strip()
        rewrite_note = str(entry['prompt_rewrite_note']).strip()
        if len(variants) < 4:
            problems.append(f'{shot}: fewer than 4 variants listed')
        if not winner:
            problems.append(f'{shot}: missing selected winner')
        if winner and winner not in variants and basename(winner) not in {basename(v) for v in variants}:
            problems.append(f'{shot}: selected winner not present in variants list')
        if not why:
            problems.append(f'{shot}: missing reason the winner was chosen')
        if repeated in {'yes', 'true'} and not defect_note:
            problems.append(f'{shot}: repeated defect marked yes but defect note is missing')
        normalized_rewrite = rewrite_note.lower()
        if normalized_rewrite and normalized_rewrite not in NA_VALUES and repeated not in {'yes', 'true'}:
            problems.append(f'{shot}: prompt rewrite note present but repeated defect is not marked yes')
    return problems


def timeline_sources(cfg: dict) -> List[str]:
    sources = []
    for seg in cfg.get('timeline_segments') or []:
        src = seg.get('source')
        if src:
            sources.append(norm_path(src))
    return sources


def shot_key_from_path(value: str) -> str:
    stem = Path(norm_path(value)).stem.lower()
    match = re.match(r'(.+?)(?:[_-]v\d+|[_-]final|[_-]selected)?$', stem)
    return match.group(1) if match else stem


def winner_lookup(entries: List[Dict[str, object]]) -> Dict[str, str]:
    lookup = {}
    for entry in entries:
        winner = norm_path(str(entry.get('selected_winner', '')))
        if not winner:
            continue
        lookup[winner] = winner
        lookup[basename(winner)] = winner
        lookup[shot_key_from_path(winner)] = winner
        for variant in entry.get('variants', []):
            variant_norm = norm_path(str(variant))
            if variant_norm:
                lookup[variant_norm] = winner
                lookup[basename(variant_norm)] = winner
                lookup[shot_key_from_path(variant_norm)] = winner
    return lookup


def autofix_timeline(cfg: dict, entries: List[Dict[str, object]]) -> List[str]:
    fixes = []
    lookup = winner_lookup(entries)
    for seg in cfg.get('timeline_segments') or []:
        src = norm_path(str(seg.get('source', '')))
        if not src:
            continue
        winner = lookup.get(src) or lookup.get(basename(src)) or lookup.get(shot_key_from_path(src))
        if winner and src != winner:
            seg['source'] = winner
            fixes.append(f'Updated timeline source {src} -> {winner}')
    return fixes


def match_winners_to_timeline(entries: List[Dict[str, object]], sources: List[str]) -> List[str]:
    problems = []
    winners = {norm_path(str(e['selected_winner'])) for e in entries if str(e['selected_winner']).strip()}
    winner_basenames = {basename(w) for w in winners}
    for src in sources:
        if src in winners or basename(src) in winner_basenames:
            continue
        problems.append(f'Timeline source not found among logged selected winners: {src}')
    return problems


def render_log(entries: List[Dict[str, object]]) -> str:
    lines = ['# Shot Selection Log', '']
    for entry in entries:
        lines.append(f"## {entry['shot']}")
        lines.append(f"- Selected winner: `{norm_path(str(entry['selected_winner']))}`" if str(entry['selected_winner']).strip() else '- Selected winner:')
        lines.append(f"- Why it won: {str(entry['why_it_won']).strip()}")
        lines.append('- Variants:')
        for variant in entry['variants']:
            lines.append(f"  - `{norm_path(str(variant))}`")
        lines.append(f"- Repeated defect detected: {str(entry['repeated_defect_detected']).strip()}")
        lines.append(f"- Defect note: {str(entry['defect_note']).strip()}")
        lines.append(f"- Prompt rewrite note: {str(entry['prompt_rewrite_note']).strip()}")
        lines.append('')
    return '\n'.join(lines).rstrip() + '\n'


def main() -> int:
    project, fix = parse_args(sys.argv)
    project_json = project / 'project.json'
    log_path = project / 'logs' / 'shot-selection.md'
    problems: List[str] = []
    fixes_applied: List[str] = []

    if not project_json.exists():
        problems.append('Missing project.json')
        cfg = {}
    else:
        cfg = json.loads(project_json.read_text())

    if not log_path.exists():
        problems.append('Missing logs/shot-selection.md')
        entries = []
    else:
        entries = parse_log(log_path)
        if not entries:
            problems.append('No shot entries found in logs/shot-selection.md')

    if fix and entries:
        fixes_applied.extend(autofix_entries(entries))
        if cfg:
            fixes_applied.extend(autofix_timeline(cfg, entries))
        log_path.write_text(render_log(entries))
        project_json.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + '\n')

    if entries:
        problems.extend(validate_entries(entries))
    sources = timeline_sources(cfg) if cfg else []
    if not sources:
        problems.append('No timeline_segments sources found in project.json')
    elif entries:
        problems.extend(match_winners_to_timeline(entries, sources))

    report = {
        'pass': not problems,
        'fix_mode': fix,
        'project_dir': str(project),
        'shot_log_path': str(log_path),
        'logged_shot_count': len(entries),
        'timeline_source_count': len(sources),
        'fixes_applied': fixes_applied,
        'problems': problems,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not problems else 1


if __name__ == '__main__':
    raise SystemExit(main())
