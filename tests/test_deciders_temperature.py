from farz.deciders import fit_temperature, sharpen


def test_sharpen_keeps_the_choice_and_sums_to_one():
    p = {"a": 0.5, "b": 0.3, "c": 0.2}
    s = sharpen(p, 0.5)
    assert max(s, key=s.get) == "a" and abs(sum(s.values()) - 1) < 1e-9 and s["a"] > 0.5
    assert sharpen(p, 1.0) == p


def test_a_modest_but_always_right_model_gets_sharpened():
    probs = [{"a": 0.4, "b": 0.3, "c": 0.3}] * 20 + [{"a": 0.3, "b": 0.4, "c": 0.3}] * 20
    gold = ["a"] * 20 + ["b"] * 20
    assert fit_temperature(probs, gold) < 0.5
