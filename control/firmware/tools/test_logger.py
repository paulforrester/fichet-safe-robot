"""Tests for logger.py (run: python3 -m pytest control/firmware/tools)."""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
import logger  # noqa: E402


def test_parse_att_line_from_firmware():
    # Format written by core::Robot::logAttempt (robot.h header comment).
    row = logger.parse_att("ATT,13434,57,1,3,18,958,107.7,1,90,CLEAN,107.6")
    assert row["index"] == 57 and (row["a"], row["b"], row["c"]) == (1, 3, 18)
    assert row["key_steps"] == 958 and row["key_deg"] == 107.7 and row["stalled"] == 1
    assert row["cls"] == "CLEAN" and row["delta_deg"] == 0.1
    assert logger.parse_att("ATT,1,2,3") is None
    assert logger.parse_att("EV,0,BOOT,0") is None
    assert logger.parse_att("ATT,x,57,1,3,18,958,107.7,1,90,CLEAN,107.6") is None


def make_rows(n=500, seed=1):
    rnd = random.Random(seed)
    rows = []
    for i in range(n):
        delta = rnd.gauss(0.0, 0.5)
        cls = "CLEAN"
        if i in (100, 333):
            delta, cls = 6.0, "FALSESET"
        if i == 450:
            delta, cls = 15.0, "SUCCESS"
        rows.append({"index": i, "a": 1, "b": 1, "c": 1, "delta_deg": round(delta, 1),
                     "key_deg": 100 + delta, "stalled": 1, "cls": cls})
    return rows


def test_analyse_finds_false_sets_and_success():
    summary, rows = logger.analyse(make_rows())
    assert summary["SUCCESS"] == 1
    assert summary["FALSESET"] == 2
    assert summary["firmware_disagrees"] == 0
    flagged = sorted(r["index"] for r in rows if r["offline_cls"] == "FALSESET")
    assert flagged == [100, 333]


def test_replay_roundtrip(tmp_path):
    raw = tmp_path / "x_raw.log"
    raw.write_text(
        "2026-10-06T10:00:00.000\tEV,0,BOOT,0\n"
        "2026-10-06T10:00:01.000\tATT,13434,0,1,1,1,958,107.7,1,90,CLEAN,107.6\n"
        "2026-10-06T10:00:02.000\tATT,14148,1,1,1,2,1010,113.6,1,90,FALSESET,107.6\n"
        "garbage line\n")
    out = tmp_path / "x_attempts.csv"
    assert logger.replay(str(raw), str(out)) == 2
    rows = logger.load_attempts(str(out))
    assert [r["index"] for r in rows] == [0, 1]
    assert rows[1]["delta_deg"] == 6.0
    assert rows[0]["host_time"] == "2026-10-06T10:00:01.000"
