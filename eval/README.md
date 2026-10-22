# Scoring

```
python eval/train_local.py                          # 5-fold on dev, then fit on all of dev, save models/local.pkl
python eval/run.py --decider local --set dev        # out-of-fold, picks the gate threshold
python eval/run.py --decider jev   --set dev        # needs TYPESAFE_API_KEY or JEV_ENV_FILE
python eval/run.py --decider local --set probe
python eval/run.py --decider local --set heldout    # once; a second run needs --again and is recorded
```

`models/` is not in git. `train_local.py` rebuilds it in about five minutes on a laptop; the first run downloads the two encoders (about 2 GB).

`results/<set>-<decider>.json` holds the numbers and every routed ticket for each run.

## Picking the threshold

On dev only, the scorer tries confidence thresholds from 0.30 to 0.99 and takes the lowest one at which at least 10 tickets clear it on both questions and at least 95% of those are fully right. Probe and held-out runs reuse that value.

## Local models tried

All on the 175 dev tickets with the same 5 folds (seed 20261023), corrected labels. "Sure at 0.5" is the share of tickets where both confidences are 0.5 or more, and how many of those are fully right.

| Model | Category | Priority | Both | Sure at 0.5 |
| --- | --- | --- | --- | --- |
| Character 2-5 grams, logistic regression (first version) | 66.3% | 74.9% | 55.4% | 11%, all right |
| Character and word grams, calibrated linear SVM | 71.4% | 72.6% | 56.0% | 41% at 79% |
| multilingual-e5-small vectors | 66.3% | 76.6% | 55.4% | 29% at 84% |
| multilingual-e5-base vectors | 69.1% | 83.4% | 62.9% | 32% at 91% |
| multilingual mpnet vectors | 63.4% | 76.0% | 53.7% | 42% at 76% |
| bge-m3 vectors | 75.4% | 80.6% | 62.3% | 42% at 92% |
| bge-m3 averaged with the grams | 77.7% | 78.9% | 65.1% | 39% at 91% |
| **e5-base and mpnet vectors averaged with the grams (chosen)** | **74.9%** | **78.9%** | **63.4%** | **38% at 95%** |

The top three are within three tickets of each other, which is noise at this size. We took the one that leaves the most tickets safely to the team at the 95% bar. bge-m3 is the close runner-up; it is a 2.2 GB model and about three times slower on the laptop.
