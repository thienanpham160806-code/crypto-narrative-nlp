"""Kiểm thử khối từ điển đã port – chạy: pytest -q (không cần mạng)."""
import collections, math, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from features.lexicon.scoring import EnglishScorer, VietScorer, tfidf_scores, indices
from utils.common import K, to_utc


def test_lm_negation_rule():
    sc = EnglishScorer({"positive": {"GOOD"}, "negative": {"LOSS"}})
    _, c, _ = sc.run("This was not a good year. Later results were good. A loss.")
    assert c["positive"] == 1 and c["negative"] == 1


def test_viet_longest_match_and_negation():
    sc = VietScorer({"negative": {"nợ xấu"}, "positive": {"tăng trưởng"}, "uncertainty": set(), "litigious": set()})
    _, c, _ = sc.run("Nợ xấu tăng nhưng doanh thu tăng trưởng; công ty không tăng trưởng mảng khác.")
    assert c["negative"] == 1 and c["positive"] == 1


def test_tfidf_matches_lm_equation():
    docs = [collections.Counter({"LOSS": 2}), collections.Counter({"LOSS": 1, "DECLINE": 1})]
    s = tfidf_scores(docs, [100, 50])
    assert math.isclose(s[0], 0.0) and math.isclose(s[1], 1 / (1 + math.log(50)) * math.log(2))


def test_indices_and_names():
    assert math.isclose(indices("fin", 100, {"positive": 3, "negative": 1})["fin_net"], 0.5)
    assert K("car", -1, 1) == "car_m1_1"


def test_vn_time_to_utc():
    import pandas as pd
    assert str(to_utc(pd.Series(["2026-10-16 08:00"]), "Asia/Ho_Chi_Minh")[0]) == "2026-10-16 01:00:00+00:00"
