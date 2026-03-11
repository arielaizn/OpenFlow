#!/usr/bin/env python3
import argparse
import json
import os
import urllib.request
from pathlib import Path

BASE_URL = "https://api.elevenlabs.io/v1"


def load_api_key() -> str:
    env_key = os.getenv("ELEVENLABS_API_KEY") or os.getenv("XI_API_KEY")
    if env_key:
        return env_key
    cred_file = Path('/root/.openclaw/credentials/elevenlabs.env')
    if cred_file.exists():
        for line in cred_file.read_text().splitlines():
            if line.startswith('ELEVENLABS_API_KEY='):
                return line.split('=', 1)[1].strip()
    raise SystemExit('Missing ELEVENLABS_API_KEY')


def main() -> int:
    p = argparse.ArgumentParser(description='Generate speech with ElevenLabs')
    p.add_argument('text')
    p.add_argument('--out', required=True)
    p.add_argument('--voice-id', default='aUd0VJr5SoAciiJHvyvD')
    p.add_argument('--model-id', default='eleven_v3')
    args = p.parse_args()

    api_key = load_api_key()
    payload = {
        'text': args.text,
        'model_id': args.model_id,
    }
    req = urllib.request.Request(
        f"{BASE_URL}/text-to-speech/{args.voice_id}",
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'xi-api-key': api_key,
            'accept': 'audio/mpeg',
            'content-type': 'application/json',
        },
        method='POST',
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        Path(args.out).write_bytes(resp.read())
    print(args.out)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
