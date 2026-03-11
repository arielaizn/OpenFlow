#!/usr/bin/env python3
import argparse
import json
import os
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE_URL = "https://api.kie.ai/api/v1"


def load_api_key() -> str:
    env_key = os.getenv("KIE_AI_API_KEY")
    if env_key:
        return env_key
    cred_file = Path("/root/.openclaw/credentials/kie.ai.env")
    if cred_file.exists():
        for line in cred_file.read_text().splitlines():
            if line.startswith("KIE_AI_API_KEY="):
                return line.split("=", 1)[1].strip()
    raise SystemExit("Missing KIE_AI_API_KEY")


def request_json(method: str, url: str, api_key: str, payload: dict | None = None) -> dict:
    headers = {"Accept": "application/json", "Authorization": f"Bearer {api_key}"}
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> int:
    p = argparse.ArgumentParser(description="Generic Kie.ai job client")
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("create")
    c.add_argument("--model", required=True)
    c.add_argument("--input-json", required=True, help="JSON string or @path/to/file.json")

    g = sub.add_parser("get")
    g.add_argument("task_id")

    w = sub.add_parser("wait")
    w.add_argument("task_id")
    w.add_argument("--timeout", type=int, default=300)
    w.add_argument("--poll-interval", type=float, default=5.0)

    args = p.parse_args()
    api_key = load_api_key()

    if args.cmd == "create":
        raw = args.input_json
        if raw.startswith("@"):
            raw = Path(raw[1:]).read_text()
        payload = {"model": args.model, "input": json.loads(raw)}
        print(json.dumps(request_json("POST", f"{BASE_URL}/jobs/createTask", api_key, payload), ensure_ascii=False, indent=2))
        return 0

    if args.cmd == "get":
        q = urllib.parse.urlencode({"taskId": args.task_id})
        print(json.dumps(request_json("GET", f"{BASE_URL}/jobs/recordInfo?{q}", api_key), ensure_ascii=False, indent=2))
        return 0

    deadline = time.time() + args.timeout
    while time.time() < deadline:
        q = urllib.parse.urlencode({"taskId": args.task_id})
        obj = request_json("GET", f"{BASE_URL}/jobs/recordInfo?{q}", api_key)
        state = obj.get("data", {}).get("state")
        if state in {"success", "fail"}:
            print(json.dumps(obj, ensure_ascii=False, indent=2))
            return 0 if state == "success" else 1
        time.sleep(args.poll_interval)
    print(json.dumps({"taskId": args.task_id, "state": "timeout"}, ensure_ascii=False, indent=2))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
