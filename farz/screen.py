"""The agent screen: a local web page in Iraqi Arabic where a support agent works the queue.

For every ticket the agent sees the customer's message, what Farz found (category, priority,
team, the amount, phone and reference, the ledger check, why it reached a person) and the
drafted reply. They approve the draft, edit it, or take the ticket over and write their own.
Nothing is sent anywhere: each choice is written to runs/actions.jsonl.

  python -m farz.screen                       # demo queue: the dev tickets as Jev routed them
  python -m farz.screen routed.jsonl          # output of python -m farz.pipeline ... --out routed.jsonl
  python -m farz.screen --port 8008
"""

from __future__ import annotations

import argparse
import json
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .ledger import Ledger
from .pipeline import LEDGER, ROOT

PAGE = Path(__file__).with_name("screen.html")
MARK = Path(__file__).with_name("mark.svg")  # the Nurunim mark
ACTIONS = ROOT / "runs" / "actions.jsonl"
CHOICES = {"approve", "edit", "take_over"}


def demo_queue() -> list[dict]:
    """Dev tickets with Jev's saved routes and the best drafts on disk, so the demo needs no network."""
    from .drafts import draft_all
    results = ROOT / "eval" / "results"
    tickets = {t["id"]: t for t in map(json.loads, (ROOT / "data" / "dev.jsonl").read_text(encoding="utf-8").splitlines())}
    routed = json.loads((results / "dev-jev.json").read_text(encoding="utf-8"))["routed"]
    saved = {}
    for name in ("drafts-dev-template.json", "drafts-dev-astra.json"):
        path = results / name
        if path.exists():
            saved.update({d["id"]: d for d in json.loads(path.read_text(encoding="utf-8"))["drafts"]})
    rows = []
    for r in routed:
        t = tickets[r["id"]]
        r = {**r, "text": t["text"], "wallet_phone": t["wallet_phone"]}
        if r["id"] in saved:
            d = saved[r["id"]]
            r.update({k: d.get(k) for k in ("draft", "draft_writer", "draft_problems", "reply_language")})
        rows.append(r)
    missing = [r for r in rows if not r.get("draft")]
    if missing:
        draft_all(missing, missing, Ledger.load(LEDGER))
    return rows


def load_queue(path: str | None) -> list[dict]:
    rows = demo_queue() if path is None else [json.loads(x) for x in Path(path).read_text(encoding="utf-8").splitlines() if x.strip()]
    ledger = Ledger.load(LEDGER)
    for r in rows:
        refs = (r.get("ledger") or {}).get("txns", [])
        r["ledger_rows"] = [t for t in (ledger.txn(r.get("wallet_phone", ""), ref) for ref in refs) if t]
    # People first, then by urgency, the way an agent should work the queue.
    order = {"urgent": 0, "high": 1, "normal": 2, "low": 3}
    rows.sort(key=lambda r: (r["route"] != "person", order.get(r["priority"], 4), r["id"]))
    return rows


class Store:
    def __init__(self, path: Path):
        self.path, self.lock, self.done = path, threading.Lock(), {}
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    a = json.loads(line)
                    self.done[a["id"]] = a

    def add(self, a: dict):
        with self.lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8", newline="\n") as f:
                f.write(json.dumps(a, ensure_ascii=False) + "\n")
            self.done[a["id"]] = a


def make_handler(queue: list[dict], store: Store):
    ids = {r["id"]: r for r in queue}

    class Handler(BaseHTTPRequestHandler):
        def _send(self, code: int, body: bytes, kind: str):
            self.send_response(code)
            self.send_header("Content-Type", kind)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _json(self, code: int, data):
            self._send(code, json.dumps(data, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

        def do_GET(self):
            if self.path in ("/", "/index.html"):
                self._send(200, PAGE.read_bytes(), "text/html; charset=utf-8")
            elif self.path == "/mark.svg":
                self._send(200, MARK.read_bytes(), "image/svg+xml")
            elif self.path == "/api/queue":
                self._json(200, {"tickets": queue, "actions": store.done})
            else:
                self._json(404, {"error": "not found"})

        def do_POST(self):
            if self.path != "/api/action":
                return self._json(404, {"error": "not found"})
            try:
                a = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))).decode("utf-8"))
            except (ValueError, UnicodeDecodeError):
                return self._json(400, {"error": "bad json"})
            if a.get("id") not in ids or a.get("choice") not in CHOICES:
                return self._json(400, {"error": "unknown ticket or choice"})
            r = ids[a["id"]]
            text = str(a.get("text") or "")[:4000]
            record = {"id": r["id"], "choice": a["choice"], "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                      "draft": r.get("draft"), "draft_writer": r.get("draft_writer"),
                      "sent_text": None if a["choice"] == "take_over" else text,
                      "changed": a["choice"] == "edit" and text.strip() != (r.get("draft") or "").strip(),
                      "route": r["route"], "category": r["category"], "priority": r["priority"]}
            store.add(record)
            self._json(200, record)

        def log_message(self, *args):
            pass

    return Handler


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("routed", nargs="?", help="pipeline output (jsonl); default: the demo queue")
    ap.add_argument("--port", type=int, default=8008)
    ap.add_argument("--actions", default=str(ACTIONS))
    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    queue = load_queue(args.routed)
    server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(queue, Store(Path(args.actions))))
    print(f"Farz agent screen: http://localhost:{args.port}  ({len(queue)} tickets)", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
