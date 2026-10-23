"""Score the saved runs again for confidence and scams, without asking any decider again.

    python eval/calibration.py

Reads every eval/results/<set>-<decider>.json, recomputes the calibration and the scam numbers
from the routed rows already there, adds them to each file's metrics and prints one table.
Nothing is tuned on these numbers: the gate threshold is still picked on dev only.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from eval.run import RESULTS, calibration, fraud_scores, load_set  # noqa: E402


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    print(f"{'run':<24}{'cat gap':>9}{'cat brier':>11}{'pri gap':>9}{'scams':>7}{'named':>8}{'missed':>8}{'auto':>6}")
    for s in ("dev", "probe", "heldout"):
        gold = None
        for decider in ("jev", "local", "local-calibrated"):
            path = RESULTS / f"{s}-{decider}.json"
            if not path.exists():
                continue
            gold = gold or [t["gold"] for t in load_set(s)]
            record = json.loads(path.read_text(encoding="utf-8"))
            routed = record["routed"]
            m = record["metrics"]
            m.update(fraud_scores(routed, gold))
            m["calibration"] = {q: calibration(routed, gold, q) for q in ("category", "priority")}
            path.write_text(json.dumps(record, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
            c = m["calibration"]
            print(f"{s + '-' + decider:<24}{c['category']['gap']:>9}{c['category']['brier']:>11}"
                  f"{c['priority']['gap']:>9}{m['fraud_tickets']:>7}{str(m['fraud_named_as_fraud']):>8}"
                  f"{len(m['fraud_missed_ids']):>8}{len(m['fraud_missed_and_auto_routed_ids']):>6}")
            for q in ("category", "priority"):
                print("   ", q, " ".join(f"[{b['from']}-{b['to']}] n={b['tickets']} said {b['said']} right {b['right']}"
                                         for b in c[q]["bins"]))


if __name__ == "__main__":
    main()
