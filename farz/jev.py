"""Jev client over one kept-open HTTPS connection.

Measured 22 Sep 2026 from Baghdad: a fresh connection costs about 826 ms, a reused one about
320 ms. So the connection is opened once, reused, and reopened once on any failure.
The key comes from TYPESAFE_API_KEY or a .env file and is never printed or logged.
"""

from __future__ import annotations

import http.client
import json
import os
import threading
import time

HOST = "api.typesafe.ai"
PATH = "/v1/systemone"
MODEL = os.environ.get("TYPESAFE_DEFAULT_MODEL", "jev-latest")
KEY_NAME = "TYPESAFE_API_KEY"
USD_PER_INPUT_TOKEN = 42 / 1_000_000_000

_PING = {"alive": {"type": "noul", "instructions": "Is this a keep-alive ping?"}}


def load_key() -> str:
    key = os.environ.get(KEY_NAME, "").strip()
    if key:
        return key
    for path in (os.environ.get("JEV_ENV_FILE"), ".env"):
        if not path or not os.path.exists(path):
            continue
        with open(path, encoding="utf-8", errors="replace") as handle:
            for line in handle:
                name, sep, value = line.strip().partition("=")
                if sep and name.strip() == KEY_NAME and value.strip():
                    return value.strip().strip('"').strip("'")
    raise SystemExit(f"Set {KEY_NAME}, or point JEV_ENV_FILE at a .env file that has it.")


class Jev:
    def __init__(self, key: str | None = None):
        self._key = key or load_key()
        self._lock = threading.Lock()
        self._conn = None

    def _post(self, body: bytes) -> dict:
        if self._conn is None:
            self._conn = http.client.HTTPSConnection(HOST, timeout=20)
        headers = {"Authorization": f"Bearer {self._key}", "Content-Type": "application/json",
                   "Connection": "keep-alive"}
        self._conn.request("POST", PATH, body=body, headers=headers)
        response = self._conn.getresponse()
        payload = response.read()
        if response.status != 200:
            raise RuntimeError(f"Jev HTTP {response.status}: {payload[:200]!r}")
        return json.loads(payload.decode("utf-8"))

    def ask(self, state: str, questions: dict) -> tuple[dict, float]:
        """Returns (response, elapsed_ms)."""
        body = json.dumps({"state": state, "model": MODEL, "questions": questions},
                          ensure_ascii=False).encode("utf-8")
        with self._lock:
            started = time.perf_counter()
            try:
                result = self._post(body)
            except (OSError, http.client.HTTPException, RuntimeError):
                self._close()
                started = time.perf_counter()
                result = self._post(body)
            return result, (time.perf_counter() - started) * 1000.0

    def warm(self) -> float:
        """Open the connection now so the first real ticket is not the slow one."""
        return self.ask("keep-alive", _PING)[1]

    def _close(self):
        if self._conn is not None:
            try:
                self._conn.close()
            finally:
                self._conn = None

    def stop(self):
        with self._lock:
            self._close()


def cost(response: dict) -> tuple[int, float]:
    tokens = int((response.get("usage") or {}).get("input_tokens") or 0)
    return tokens, tokens * USD_PER_INPUT_TOKEN
