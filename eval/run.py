"""Score a decider on one ticket set, through the whole pipeline.

    python eval/run.py --decider local --set dev        # local is scored out-of-fold on dev
    python eval/run.py --decider jev   --set probe      # needs TYPESAFE_API_KEY or JEV_ENV_FILE
    python eval/run.py --decider jev   --set heldout    # once per decider, see below
    python eval/run.py --decider local --set dev --calibrated   # with the confidence correction

Sets:
  dev      175 tickets. Jev sees them cold. Our model is scored with 5-fold cross-validation,
           so every ticket is judged by a model that was not trained on it.
  probe    63 tickets written by a person on 23 Sep. Category and priority only, no ledger.
  heldout  75 tickets kept apart. The file's hash is checked first, and each decider is scored
           on it once: a second run is refused unless --again is given, and that is reported.

Writes eval/results/<set>-<decider>.json with the numbers and every routed ticket.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from farz.deciders import LocalDecider, decision, fit_temperature, sharpen  # noqa: E402
from farz.gate import THRESHOLD  # noqa: E402
from farz.ledger import Ledger  # noqa: E402
from farz.pipeline import LEDGER, LOCAL_MODEL, make_decider, route  # noqa: E402

HELDOUT_SHA256 = "39de061d3e0be132730027fa5be38c79be07a6781a62305c767321d397ca9b38"
RESULTS = ROOT / "eval" / "results"
CURVE = (0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99)
PICK_GRID = [round(0.30 + 0.05 * i, 2) for i in range(14)] + [0.99]
PICK_TARGET, PICK_MIN = 0.95, 10


def load_set(name: str) -> list[dict]:
    if name == "probe":
        rows = json.loads((ROOT / "probe" / "tickets.json").read_text(encoding="utf-8"))
        return [{"id": r["id"], "text": r["text"], "wallet_phone": "",
                 "gold": {"category": r["category"], "priority": r["priority"]}} for r in rows]
    path = ROOT / "data" / f"{name}.jsonl"
    raw = path.read_bytes()
    if name == "heldout" and hashlib.sha256(raw).hexdigest() != HELDOUT_SHA256:
        raise SystemExit("heldout.jsonl does not match its recorded hash; the held-out score would be void")
    return [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]


class Fixed:
    """Hands the pipeline decisions that were made beforehand (the out-of-fold ones)."""

    def __init__(self, decisions):
        self.decisions = decisions

    def decide(self, texts):
        return self.decisions


def _as_decision(row: dict) -> dict:
    """Rebuild a decider's answer from a routed row, so dev can be re-routed without asking Jev again."""
    return {q: {"choice": row[q], "confidence": row[f"{q}_confidence"], "probabilities": row["probabilities"][q]}
            for q in ("category", "priority")}


def out_of_fold(tickets: list[dict], calibrated: bool = False, folds: int = 5, seed: int = 20261023) -> list[dict]:
    from sklearn.model_selection import StratifiedKFold
    texts = [t["text"] for t in tickets]
    y = {q: [t["gold"][q] for t in tickets] for q in ("category", "priority")}
    decisions, fold_of = [None] * len(tickets), [0] * len(tickets)
    splits = list(StratifiedKFold(folds, shuffle=True, random_state=seed).split(texts, y["category"]))
    for k, (train, test) in enumerate(splits):
        model = LocalDecider().fit([texts[i] for i in train], {q: [v[i] for i in train] for q, v in y.items()})
        for i, d in zip(test, model.decide([texts[i] for i in test])):
            decisions[i], fold_of[i] = d, k
    if not calibrated:
        return decisions
    # The saved model's temperature is fitted on all of these predictions. To score it fairly, each
    # fold's tickets are corrected with a temperature fitted on the other four folds only.
    raw = {q: [d[q]["probabilities"] for d in decisions] for q in y}
    for k in range(folds):
        others = [i for i in range(len(tickets)) if fold_of[i] != k]
        for q in y:
            t = fit_temperature([raw[q][i] for i in others], [y[q][i] for i in others])
            for i in range(len(tickets)):
                if fold_of[i] == k:
                    decisions[i] = {**decisions[i], q: decision(sharpen(raw[q][i], t))}
    return decisions


def share(hits: int, total: int):
    return None if total == 0 else round(hits / total, 4)


def pick_threshold(tickets: list[dict], routed: list[dict]) -> float | None:
    """Lowest confidence at which at least 95% of the tickets the decider is sure of are right.

    Only ever run on dev. Probe and held-out runs reuse the value, they never choose it.
    """
    for t in PICK_GRID:
        sure = [r["category"] == k["gold"]["category"] and r["priority"] == k["gold"]["priority"]
                for r, k in zip(routed, tickets)
                if r["category_confidence"] >= t and r["priority_confidence"] >= t]
        if len(sure) >= PICK_MIN and sum(sure) / len(sure) >= PICK_TARGET:
            return t
    return None


def dev_threshold(decider: str) -> float:
    path = RESULTS / f"dev-{decider}.json"
    if path.exists():
        picked = json.loads(path.read_text(encoding="utf-8")).get("picked_threshold")
        if picked is not None:
            return picked
    return THRESHOLD


BINS = (0.0, 0.5, 0.7, 0.8, 0.9, 1.01)


def calibration(routed: list[dict], gold: list[dict], question: str) -> dict:
    """Does a stated confidence of 0.9 mean right nine times in ten?

    The gate trusts these numbers, so a decider that says 0.95 and is right 70% of the time is
    dangerous even with good accuracy. Gap is the ticket-weighted distance between confidence and
    accuracy across the bins (lower is better); Brier is the squared error of all the probabilities.
    """
    rows = [(r[f"{question}_confidence"], r[question] == g[question], r["probabilities"][question], g[question])
            for r, g in zip(routed, gold)]
    bins, gap = [], 0.0
    for lo, hi in zip(BINS, BINS[1:]):
        inside = [(c, ok) for c, ok, _, _ in rows if lo <= c < hi]
        if not inside:
            continue
        conf = statistics.mean(c for c, _ in inside)
        acc = sum(ok for _, ok in inside) / len(inside)
        gap += len(inside) / len(rows) * abs(acc - conf)
        bins.append({"from": lo, "to": min(hi, 1.0), "tickets": len(inside),
                     "said": round(conf, 3), "right": round(acc, 3)})
    brier = statistics.mean(sum((p.get(k, 0.0) - (k == want)) ** 2 for k in set(p) | {want})
                            for _, _, p, want in rows)
    return {"gap": round(gap, 4), "brier": round(brier, 4), "bins": bins}


def fraud_scores(routed: list[dict], gold: list[dict]) -> dict:
    """Scam tickets on their own: a missed scam costs far more than a wrong team."""
    said = [r["category"] == "fraud_scam" for r in routed]
    real = [g["category"] == "fraud_scam" for g in gold]
    caught = sum(s and f for s, f in zip(said, real))
    return {"fraud_tickets": sum(real),
            "fraud_named_as_fraud": share(caught, sum(real)),
            "fraud_label_right_when_given": share(caught, sum(said)),
            "fraud_missed_ids": [r["id"] for r, s, f in zip(routed, said, real) if f and not s],
            "fraud_missed_and_auto_routed_ids": [r["id"] for r, s, f in zip(routed, said, real)
                                                 if f and not s and r["route"] == "team_queue"]}


def score(tickets: list[dict], routed: list[dict], per_ticket_ms: list[float], usd: float) -> dict:
    gold = [t["gold"] for t in tickets]
    n = len(tickets)
    cat_ok = [r["category"] == g["category"] for r, g in zip(routed, gold)]
    pri_ok = [r["priority"] == g["priority"] for r, g in zip(routed, gold)]
    auto = [r["route"] == "team_queue" for r in routed]
    m = {
        "tickets": n,
        "category_accuracy": share(sum(cat_ok), n),
        "priority_accuracy": share(sum(pri_ok), n),
        "both_right": share(sum(a and b for a, b in zip(cat_ok, pri_ok)), n),
        "sent_to_team_queue": share(sum(auto), n),
        "team_queue_both_right": share(sum(a and c and p for a, c, p in zip(auto, cat_ok, pri_ok)), sum(auto)),
        "team_queue_wrong_ids": [r["id"] for r, a, c, p in zip(routed, auto, cat_ok, pri_ok) if a and not (c and p)],
    }
    fraud = [r for r, g in zip(routed, gold) if g["category"] == "fraud_scam"]
    m["fraud_to_person"] = share(sum(r["route"] == "person" for r in fraud), len(fraud))
    m.update(fraud_scores(routed, gold))
    m["calibration"] = {q: calibration(routed, gold, q) for q in ("category", "priority")}
    if "must_person" in gold[0]:
        must = [(r, g) for r, g in zip(routed, gold) if g["must_person"]]
        m["must_person_tickets"] = len(must)
        m["must_person_to_person"] = share(sum(r["route"] == "person" for r, _ in must), len(must))
        m["must_person_missed_ids"] = [r["id"] for r, _ in must if r["route"] != "person"]
        inj = [r for r, g in zip(routed, gold) if g["injection"]]
        m["injection_to_person"] = share(sum(r["route"] == "person" for r in inj), len(inj))
        rest = [r for r, g in zip(routed, gold) if not g["must_person"]]
        m["others_sent_to_person"] = share(sum(r["route"] == "person" for r in rest), len(rest))
        for field in ("amount", "phone", "reference"):
            m[f"{field}_exact"] = share(sum(r["entities"][field] == g[field] for r, g in zip(routed, gold)), n)
        # "Not about a transaction" and "no details given" both mean there is nothing to check.
        # "mismatch" and "not_found" both mean the ledger disagrees and a person must look.
        bucket = {"not_applicable": "nothing", "no_details": "nothing", "match": "match",
                  "mismatch": "problem", "not_found": "problem"}
        outcome = [bucket[(r["ledger"] or {}).get("outcome", "not_applicable")] for r in routed]
        m["ledger_outcome_right"] = share(sum(o == bucket[g["ledger_case"]] for o, g in zip(outcome, gold)), n)
        bad = [o for o, g in zip(outcome, gold) if bucket[g["ledger_case"]] == "problem"]
        m["ledger_problems_flagged"] = share(bad.count("problem"), len(bad))
        m["ledger_false_alarms"] = sum(o == "problem" and bucket[g["ledger_case"]] != "problem"
                                       for o, g in zip(outcome, gold))
        found = [(r, g) for r, g in zip(routed, gold) if g["ledger_case"] == "match"]
        m["ledger_rows_exact"] = share(sum(set((r["ledger"] or {}).get("txns", [])) == set(g["txn_refs"])
                                           for r, g in found), len(found))
    curve = []
    for t in CURVE:
        sure = [c and p for c, p, r in zip(cat_ok, pri_ok, routed)
                if r["category_confidence"] >= t and r["priority_confidence"] >= t]
        curve.append({"threshold": t, "coverage": share(len(sure), n), "both_right": share(sum(sure), len(sure))})
    m["confidence_curve"] = curve
    m["ms_per_ticket_median"] = round(statistics.median(per_ticket_ms), 1)
    m["ms_per_ticket_p95"] = round(sorted(per_ticket_ms)[int(0.95 * (len(per_ticket_ms) - 1))], 1)
    m["usd_total"] = round(usd, 6)
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--decider", required=True, choices=["local", "jev"])
    ap.add_argument("--set", required=True, choices=["dev", "probe", "heldout"])
    ap.add_argument("--threshold", type=float,
                    help="default: the value picked on dev for this decider, else the gate's 0.90")
    ap.add_argument("--calibrated", action="store_true", help="local only: apply the confidence correction")
    ap.add_argument("--again", action="store_true", help="allow a second held-out run (it is recorded)")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    if args.calibrated and args.decider != "local":
        raise SystemExit("--calibrated is for the local decider")
    name = "local-calibrated" if args.calibrated else args.decider

    out = RESULTS / f"{args.set}-{name}.json"
    runs = 1
    if args.set == "heldout" and out.exists():
        if not args.again:
            raise SystemExit(f"{out.name} exists: the held-out set was already scored for {args.decider}")
        runs = json.loads(out.read_text(encoding="utf-8"))["heldout_runs"] + 1

    tickets = load_set(args.set)
    if args.threshold is None:
        args.threshold = THRESHOLD if args.set == "dev" else dev_threshold(name)
    if args.decider == "local" and args.set == "dev":
        decider = Fixed(out_of_fold(tickets, args.calibrated))
        note = "5-fold out-of-fold on dev (timing excludes the model, see probe for that)"
    elif args.decider == "local":
        decider = LocalDecider.load(LOCAL_MODEL)
        decider.calibrated = args.calibrated
        note = "trained on all 175 dev tickets"
    else:
        decider = make_decider("jev")
        note = "zero-shot"

    started = time.perf_counter()
    routed = route(tickets, decider, Ledger.load(LEDGER), args.threshold)
    elapsed = (time.perf_counter() - started) * 1000.0
    picked = None
    if args.set == "dev":
        # Choose the threshold on dev, then route dev again with it so its numbers match later runs.
        picked = pick_threshold(tickets, routed)
        if picked is not None and picked != args.threshold:
            args.threshold = picked
            routed = route(tickets, Fixed(decider.decisions if isinstance(decider, Fixed) else
                                          [_as_decision(r) for r in routed]), Ledger.load(LEDGER), picked)
    if args.decider == "jev":
        per_ticket = [m["ms"] for m in decider.last_meta]
        usd = sum(m["usd"] or 0 for m in decider.last_meta)
    else:
        per_ticket = [elapsed / len(tickets)] * len(tickets)
        usd = 0.0

    metrics = score(tickets, routed, per_ticket, usd)
    record = {"set": args.set, "decider": name, "how": note, "threshold": args.threshold,
              "date": time.strftime("%Y-%m-%d %H:%M"), "metrics": metrics, "routed": routed}
    if args.set == "dev":
        record["picked_threshold"] = picked
    if args.set == "heldout":
        record["heldout_runs"] = runs
        record["heldout_sha256"] = HELDOUT_SHA256
    RESULTS.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(record, ensure_ascii=False, indent=1), encoding="utf-8")
    shown = {k: v for k, v in metrics.items() if k not in ("confidence_curve", "calibration") and not k.endswith("_ids")}
    print(json.dumps({"set": args.set, "decider": name, "how": note, **shown}, indent=1))
    print("confidence curve:", " ".join(f"{c['threshold']}: {c['coverage']} at {c['both_right']}"
                                        for c in metrics["confidence_curve"]))


if __name__ == "__main__":
    main()
