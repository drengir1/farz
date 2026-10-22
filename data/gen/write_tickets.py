"""Turn scenario skeletons into customer ticket text with GPT-6 Astra, then check every ticket.

The writer sees the situation, language, style and the exact strings it must include. It never
sees the category or priority names, so it cannot leak a label word into the text.

  python data/gen/write_tickets.py brief astra 26     # writes batch input files for the Astra writer
  python data/gen/write_tickets.py run   astra-03     # runs one Astra batch (needs the Codex CLI)
  python data/gen/write_tickets.py brief claude 24    # batch files for the Claude writer (run by hand)
  python data/gen/write_tickets.py check              # merges results, checks strings and words, writes tickets
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GEN = ROOT / "data" / "gen"
BATCHES = GEN / "batches"
CODEX = Path(os.environ.get("CODEX_EXE", "C:/Users/huawei/.codex/plugins/.plugin-appserver/codex.exe"))

LANG_NOTE = {
    "dialect": "Iraqi Arabic dialect (Baghdadi), Arabic script, the way people really type on WhatsApp.",
    "english": "English, as typed by an Iraqi customer. Simple English, maybe a small mistake.",
    "arabizi": "Iraqi Arabic dialect written in Latin letters and numbers (3 = ع, 7 = ح, 6 = ط, 9 = ص, ch = چ, g = گ).",
    "mixed": "Iraqi Arabic dialect in Arabic script, with some English words mixed in (app, transfer, balance, OTP, card).",
}

# Shakir's word list for any Iraqi Arabic we produce (server: _resources/copy/iraqi-words.tsv).
WORD_FIXES = {"مسدود": "معزل", "مسدودين": "معزلين", "فاتحين": "مفتحين", "ورينا": "شوفنا", "ورّينا": "شوفنا",
              "نوريك": "نشوفك", "نورّيك": "نشوفك", "زباين": "زبائن", "ينبلغ": "يتبلغ"}
BANNED = ["حچاك", "حجاك"]

BRIEF = """You write realistic customer support tickets for testing a support system at an Iraqi mobile wallet company (a ZainCash-like wallet). Everything is invented: no real people.

For each item below, write ONE ticket as the customer would type it into the app's support chat. Follow its situation, language and style.

Rules:
- Each ticket must contain every string in must_include exactly as given, character for character (same digits, same spacing, same letters). Do not reformat them. Do not add any other amounts, phone numbers or reference numbers.
- Never use support-team words like category, priority, urgent, high priority, ticket type, fraud team, escalate. Customers describe what happened, they do not label it.
- Do not open with "Dear ZainCash" every time. Vary openings; many real messages have no greeting at all.
- Length: mostly 1 to 4 sentences. "very short" means under ten words plus the required strings.
- If an item has an "injection" note, include that line naturally in the customer's message as described.
- Iraqi Arabic word rules (these are corrections from a native speaker, follow them):
  write معزل not مسدود, معزلين not مسدودين, مفتحين not فاتحين, شوفنا not ورينا, نشوفك not نوريك, زبائن not زباين, يتبلغ not ينبلغ.
  never write حچاك or حجاك. If you write شكد, it must be followed by سعر (شكد سعرها); for amounts use شگد/كم with the noun instead.
  keep the spellings گاعد and چان.
- Use natural Iraqi words: هواية، شلون، شنو، ليش، اكو، ماكو، هسه، باچر، دزيت، حولت، رصيد، وكيل، المحفظة، الكود، مو، چا.

Return JSON: {"tickets": [{"id": "...", "text": "..."}]} with one entry per item, same ids, same order.

Items:
"""

SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["tickets"],
    "properties": {"tickets": {"type": "array", "items": {
        "type": "object", "additionalProperties": False, "required": ["id", "text"],
        "properties": {"id": {"type": "string"}, "text": {"type": "string"}}}}},
}


def writer_item(sc: dict) -> dict:
    item = {"id": sc["id"], "situation": sc["situation"], "language": LANG_NOTE[sc["language"]],
            "style": sc["style"], "must_include": sc["must_include"]}
    if sc["injection"]:
        item["injection"] = sc["injection"]
    return item


def brief(writer: str, size: int):
    scenarios = json.loads((GEN / "scenarios.json").read_text(encoding="utf-8"))
    mine = [sc for sc in scenarios if sc["writer"] == writer]
    BATCHES.mkdir(exist_ok=True)
    for i in range(0, len(mine), size):
        name = f"{writer}-{i // size + 1:02d}"
        items = [writer_item(sc) for sc in mine[i:i + size]]
        (BATCHES / f"{name}.prompt.md").write_text(BRIEF + json.dumps(items, ensure_ascii=False, indent=1) + "\n",
                                                   encoding="utf-8")
        print(name, len(items))


def run(name: str):
    prompt = (BATCHES / f"{name}.prompt.md").read_text(encoding="utf-8")
    out = BATCHES / f"{name}.out.json"
    with tempfile.TemporaryDirectory() as box:
        schema = Path(box) / "schema.json"
        schema.write_text(json.dumps(SCHEMA), encoding="utf-8")
        work = Path(box) / "work"
        work.mkdir()
        env = {k: v for k, v in os.environ.items() if not k.startswith("OPENAI_")}
        cmd = [str(CODEX), "exec", "--ephemeral", "--ignore-user-config", "--ignore-rules", "--skip-git-repo-check",
               "--sandbox", "read-only", "--color", "never", "-m", "gpt-6-astra",
               "-c", "model_reasoning_effort=high", "-c", 'web_search="disabled"', "-c", "agents.enabled=false",
               "--disable", "shell_tool", "--disable", "browser_use", "--disable", "browser_use_external",
               "--disable", "computer_use", "--disable", "apps", "--disable", "hooks", "--disable", "in_app_browser",
               "--disable", "image_generation", "--disable", "code_mode_host", "--disable", "unified_exec",
               "-C", str(work), "--output-schema", str(schema), "-o", str(out), "-"]
        r = subprocess.run(cmd, input=prompt.encode("utf-8"), capture_output=True, env=env, timeout=900)
        if r.returncode != 0 or not out.exists():
            sys.stderr.write(r.stderr.decode("utf-8", "replace")[-2000:])
            raise SystemExit(f"{name}: codex exit {r.returncode}")
    data = json.loads(out.read_text(encoding="utf-8"))
    print(name, "tickets", len(data["tickets"]))


def check():
    scenarios = {sc["id"]: sc for sc in json.loads((GEN / "scenarios.json").read_text(encoding="utf-8"))}
    texts = {}
    for f in sorted(BATCHES.glob("*.out.json")):
        for t in json.loads(f.read_text(encoding="utf-8"))["tickets"]:
            if t["id"] in scenarios:
                texts[t["id"]] = t["text"].strip()
    problems = []
    for tid, sc in scenarios.items():
        text = texts.get(tid)
        if not text:
            problems.append((tid, "missing"))
            continue
        for s in sc["must_include"]:
            if s not in text:
                problems.append((tid, f"lacks {s!r}"))
        for wrong in list(WORD_FIXES) + BANNED:
            if re.search(rf"(?<![\u0600-\u06FF]){wrong}(?![\u0600-\u06FF])", text):
                problems.append((tid, f"word {wrong}"))
        if re.search(r"شكد(?!\s*سعر)", text):
            problems.append((tid, "شكد without سعر"))
        for leak in ("priority", "category", "urgent", "escalat", "fraud team", "أولوية", "تصنيف"):
            if leak in text.lower():
                problems.append((tid, f"label word {leak}"))
    for p in problems:
        print(*p)
    print(f"{len(texts)} written, {len(problems)} problems")
    if problems:
        raise SystemExit(1)
    # One file per split, so the held-out set can be kept apart from everything we tune on.
    for split in ("dev", "heldout"):
        rows = []
        for tid, sc in scenarios.items():
            if sc["split"] != split:
                continue
            rows.append({"id": tid, "text": texts[tid], "wallet_phone": sc["wallet_phone"], "language": sc["language"],
                         "writer": sc["writer"],
                         "gold": {"category": sc["category"], "priority": sc["priority"], "amount": sc["gold_amount"],
                                  "phone": sc["gold_phone"], "reference": sc["gold_reference"],
                                  "txn_refs": sc["gold_txn_refs"], "ledger_case": sc["ledger_case"],
                                  "must_person": sc["must_person"], "injection": bool(sc["injection"])}})
        path = ROOT / "data" / f"{split}.jsonl"
        path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8",
                        newline="\n")
        print(path.name, len(rows))


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    cmd = sys.argv[1]
    if cmd == "brief":
        brief(sys.argv[2], int(sys.argv[3]))
    elif cmd == "run":
        run(sys.argv[2])
    elif cmd == "check":
        check()
