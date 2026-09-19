"""Tests for life.

Marks here are SYNTHETIC. This repo is public, so no real result appears in
it — the fixtures exist to pin the two admission formulas, and hand-computed
expected totals do that just as well as real ones.

  FPS = 70 + 80 + 75 + (85 + 65 + 60)          = 435   [LO 90 excluded]
  SU  = 80 + 75 + (70+80+75+85+65+60)          = 590

If a refactor breaks the arithmetic these fail, rather than silently
mis-advising a university choice.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from lifeos import store  # noqa: E402
from lifeos.cli import days_until, main  # noqa: E402
from lifeos.render import table  # noqa: E402
from lifeos.scoring import improvement_plan, su_selection, uct_fps  # noqa: E402

# Synthetic. Life Orientation is deliberately the highest mark so the
# exclusion rules are exercised, and the two UCT gates sit exactly on their
# boundaries (Maths 80, PhysSci 75).
SAMPLE = {
    "English": 70, "Mathematics": 80, "Physical Sciences": 75,
    "Life Sciences": 85, "Information Technology": 60,
    "Afrikaans FAL": 65, "Life Orientation": 90,
}


# ── scoring ───────────────────────────────────────────────────────────────────

def test_uct_fps_matches_hand_computed_total():
    assert uct_fps(SAMPLE).total == 435


def test_su_selection_matches_hand_computed_total():
    assert su_selection(SAMPLE).total == 590


def test_fps_excludes_life_orientation():
    """LO is the highest mark here, and must still never be counted."""
    assert "Life Orientation" not in uct_fps(SAMPLE).counting


def test_fps_counts_exactly_six_subjects():
    assert len(uct_fps(SAMPLE).counting) == 6


def test_fps_gap_and_gates():
    s = uct_fps(SAMPLE)
    assert s.gap == 65
    assert all(s.gates.values())      # 80 and 75 sit exactly on the minimums
    assert not s.clear                # but the 500 target is not met


def test_band_a_needs_both_target_and_gates():
    """FPS 500 with Maths below 80 is not a Band A guarantee."""
    marks = dict(SAMPLE, Mathematics=79, English=90, **{"Physical Sciences": 90})
    s = uct_fps(marks)
    s.total = 500  # force the target to be met
    assert s.meets_target
    assert not s.gates["Mathematics >= 80"]
    assert not s.clear


def test_su_double_counts_maths_and_physsci():
    """Maths and PhysSci appear in the explicit terms and in the best six."""
    base = su_selection(SAMPLE).total
    lifted = su_selection(dict(SAMPLE, Mathematics=90)).total   # +10 marks
    assert lifted - base == 20


def test_su_single_counts_other_subjects():
    base = su_selection(SAMPLE).total
    lifted = su_selection(dict(SAMPLE, **{"Life Sciences": 95})).total  # +10 marks
    assert lifted - base == 10


def test_strong_distribution_clears_both_thresholds():
    """A Band A distribution must clear UCT 500 and SU 620 together."""
    planned = {
        "Mathematics": 90, "Physical Sciences": 85, "English": 75,
        "Life Sciences": 86, "Information Technology": 82,
        "Further Studies Maths": 82, "Life Orientation": 82,
    }
    assert uct_fps(planned).total >= 500
    assert uct_fps(planned).clear
    assert su_selection(planned).total >= 620


def test_improvement_plan_ranks_by_fps_gain():
    plan = improvement_plan(SAMPLE, {"English": 79, "Afrikaans FAL": 68})
    assert [r["subject"] for r in plan] == ["English", "Afrikaans FAL"]
    assert plan[0]["fps_gain"] == 9


def test_improvement_plan_ignores_downgrades():
    assert improvement_plan(SAMPLE, {"Mathematics": 75}) == []


def test_missing_required_subject_raises():
    with pytest.raises(ValueError, match="English"):
        uct_fps({"Mathematics": 84, "Physical Sciences": 77})


# ── store ─────────────────────────────────────────────────────────────────────

def test_store_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setenv("LIFE_HOME", str(tmp_path))
    data = store.load()
    data["marks"] = SAMPLE
    store.save(data)
    assert store.load()["marks"] == SAMPLE


def test_store_missing_file_returns_skeleton(tmp_path, monkeypatch):
    monkeypatch.setenv("LIFE_HOME", str(tmp_path / "nope"))
    assert store.load()["marks"] == {}


def test_store_fills_keys_added_later(tmp_path, monkeypatch):
    monkeypatch.setenv("LIFE_HOME", str(tmp_path))
    (tmp_path / "store.json").write_text('{"schema": 1, "marks": {}}')
    assert "deadlines" in store.load()


def test_store_is_not_world_readable(tmp_path, monkeypatch):
    monkeypatch.setenv("LIFE_HOME", str(tmp_path))
    store.save(store.load())
    assert store.path().stat().st_mode & 0o077 == 0


# ── dates and rendering ───────────────────────────────────────────────────────

def test_days_until_uses_override(monkeypatch):
    monkeypatch.setenv("LIFE_TODAY", "2026-09-19")
    assert days_until("2026-10-15") == 26
    assert days_until("2026-09-19") == 0
    assert days_until("2026-09-12") == -7


def test_days_until_tolerates_junk():
    assert days_until(None) is None
    assert days_until("not-a-date") is None


def test_table_aligns_around_ansi_codes():
    lines = table([["\033[1mxx\033[0m", "a"], ["y", "b"]]).splitlines()
    # "xx" is 2 visible chars despite the escapes, so both columns line up.
    assert lines[0].index("a") - len("\033[1m\033[0m") == lines[1].index("b")


def test_table_handles_empty():
    assert "nothing" in table([])


# ── CLI ───────────────────────────────────────────────────────────────────────

@pytest.fixture
def seeded(tmp_path, monkeypatch):
    monkeypatch.setenv("LIFE_HOME", str(tmp_path))
    monkeypatch.setenv("LIFE_TODAY", "2026-09-19")
    monkeypatch.setenv("NO_COLOR", "1")
    data = store.load()
    data.update({
        "marks": SAMPLE,
        "synced_at": "2026-09-19",
        "deadlines": [{"due": "2026-09-30", "what": "Example scholarship", "action": "Apply"}],
        "open_loops": [{"what": "Example unanswered reply", "waiting_since": "2026-09-01",
                        "priority": "high", "action": "Answer it"}],
        "documents": [{"name": "Example document", "have": False, "blocking": True}],
        "applications": [{"name": "Example bursary", "stage": "action-needed", "note": "Pending"}],
    })
    store.save(data)
    return tmp_path


def test_brief_shows_next_paper_and_deadline(seeded, capsys):
    assert main(["brief"]) == 0
    out = capsys.readouterr().out
    assert "IT P1" in out and "Example scholarship" in out and "Example unanswered" in out


def test_doctor_fails_on_blocking_document(seeded, capsys):
    assert main(["doctor"]) == 1
    assert "Example document" in capsys.readouterr().out


def test_doctor_passes_when_clean(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("LIFE_HOME", str(tmp_path))
    monkeypatch.setenv("LIFE_TODAY", "2026-09-19")
    data = store.load()
    data["synced_at"] = "2026-09-19"
    store.save(data)
    # Connector warnings are warnings, not failures.
    assert main(["doctor"]) == 0


def test_marks_reports_both_scores(seeded, capsys):
    assert main(["marks"]) == 0
    out = capsys.readouterr().out
    assert "435" in out and "590" in out


def test_empty_store_guides_instead_of_crashing(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("LIFE_HOME", str(tmp_path / "fresh"))
    monkeypatch.setenv("NO_COLOR", "1")
    for cmd in ("brief", "marks", "apps", "deadlines"):
        assert main([cmd]) == 0
    assert "life init" in capsys.readouterr().out


def test_sync_merges_and_stamps(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("LIFE_HOME", str(tmp_path))
    payload = tmp_path / "p.json"
    payload.write_text(json.dumps({"marks": SAMPLE, "bogus_key": 1}))
    assert main(["sync", str(payload)]) == 0
    out = capsys.readouterr().out
    assert "bogus_key" in out          # unknown keys are reported, not silently dropped
    data = store.load()
    assert data["marks"] == SAMPLE
    assert data["synced_at"] is not None
    assert "bogus_key" not in data


def test_sync_rejects_bad_json(tmp_path, monkeypatch):
    monkeypatch.setenv("LIFE_HOME", str(tmp_path))
    bad = tmp_path / "bad.json"
    bad.write_text("{nope")
    assert main(["sync", str(bad)]) == 1


def test_init_refuses_to_clobber(tmp_path, monkeypatch):
    monkeypatch.setenv("LIFE_HOME", str(tmp_path))
    assert main(["init"]) == 0
    assert main(["init"]) == 1
    assert main(["init", "--force"]) == 0


def test_entrypoint_runs_as_script():
    env = {**os.environ, "LIFE_HOME": "/nonexistent-life-home", "NO_COLOR": "1"}
    r = subprocess.run([sys.executable, str(ROOT / "life"), "--version"],
                       capture_output=True, text=True, env=env)
    assert r.returncode == 0 and "life" in r.stdout


def test_repo_contains_no_personal_store():
    """The repo is public. A committed store would leak marks and ID numbers."""
    tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout
    assert "store.json" not in tracked
    assert ".life/" not in tracked


# ── projects ──────────────────────────────────────────────────────────────────

def test_projects_lists_and_orders_by_blocked_first(seeded, capsys):
    data = store.load()
    data["projects"] = [
        {"name": "archived-thing", "status": "archived", "last_push": "2026-01-01"},
        {"name": "blocked-thing", "status": "blocked", "last_push": "2026-09-13",
         "blocker": "account verification failed"},
        {"name": "live-thing", "status": "live", "last_push": "2026-09-13"},
    ]
    store.save(data)
    assert main(["projects"]) == 0
    out = capsys.readouterr().out
    assert out.index("blocked-thing") < out.index("live-thing") < out.index("archived-thing")
    assert "account verification failed" in out


def test_doctor_fails_on_a_blocked_project(seeded, capsys):
    data = store.load()
    data["documents"] = []          # isolate the project as the only hard problem
    data["open_loops"] = []
    data["projects"] = [{"name": "app", "status": "blocked", "blocker": "store review"}]
    store.save(data)
    assert main(["doctor"]) == 1
    assert "store review" in capsys.readouterr().out


def test_projects_without_blocker_is_not_a_doctor_failure(seeded, capsys):
    data = store.load()
    data["documents"] = []
    data["open_loops"] = []
    data["projects"] = [{"name": "app", "status": "live", "last_push": "2026-09-13"}]
    store.save(data)
    assert main(["doctor"]) == 0


def test_projects_empty_store_guides(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("LIFE_HOME", str(tmp_path / "fresh"))
    monkeypatch.setenv("NO_COLOR", "1")
    assert main(["projects"]) == 0
    assert "life init" in capsys.readouterr().out


# ── regressions found in code review of PR #2 ────────────────────────────────

def test_su_uses_the_mean_not_the_sum_when_subjects_are_missing():
    """`life sync` documents partial marks dicts. sum(best) != 6*mean(best)
    below six subjects, and understating the score misreports the verdict."""
    four = {"Mathematics": 90, "Physical Sciences": 85, "English": 75, "Life Sciences": 86}
    expected = round(90 + 85 + 6 * (sum(four.values()) / 4))
    s = su_selection(four)
    assert s.total == expected == 679
    assert s.meets_target          # the summing bug reported 109 points short
    assert s.partial


def test_scores_are_unchanged_for_a_complete_transcript():
    """The mean/sum fix must not move a real six-subject result."""
    assert su_selection(SAMPLE).total == 590
    assert uct_fps(SAMPLE).total == 435
    assert not su_selection(SAMPLE).partial
    assert not uct_fps(SAMPLE).partial


def test_partial_flag_is_set_for_a_short_fps():
    assert uct_fps({"English": 70, "Mathematics": 80, "Physical Sciences": 75}).partial


def test_failed_gates_are_named_when_the_target_is_met():
    # FPS 539 (>= 500) but Mathematics 79 misses the 80 minimum.
    marks = {"English": 95, "Mathematics": 79, "Physical Sciences": 95,
             "Life Sciences": 95, "Information Technology": 90,
             "Afrikaans FAL": 85, "Life Orientation": 99}
    s = uct_fps(marks)
    assert s.total >= 500
    assert s.gap == 0 and not s.clear          # "0 points short" was the old lie
    assert "Mathematics >= 80" in s.failed_gates


def test_marks_reports_the_gate_not_a_zero_gap(seeded, capsys):
    data = store.load()
    data["marks"] = {"English": 95, "Mathematics": 79, "Physical Sciences": 95,
                     "Life Sciences": 95, "Information Technology": 95,
                     "Afrikaans FAL": 95, "Life Orientation": 40}
    store.save(data)
    assert main(["marks"]) == 0
    out = capsys.readouterr().out
    assert "0 points short" not in out
    assert "Mathematics >= 80" in out


def test_explicit_within_14_actually_filters(seeded, capsys):
    """`--within 14` collided with the default sentinel and did nothing."""
    data = store.load()
    data["deadlines"] = [{"due": "2026-12-25", "what": "far away"},
                         {"due": "2026-09-25", "what": "near"}]
    store.save(data)
    assert main(["deadlines", "--within", "14"]) == 0
    out = capsys.readouterr().out
    assert "near" in out and "far away" not in out


def test_deadlines_defaults_to_no_horizon(seeded, capsys):
    data = store.load()
    data["deadlines"] = [{"due": "2026-12-25", "what": "far away"}]
    store.save(data)
    assert main(["deadlines"]) == 0
    assert "far away" in capsys.readouterr().out


def test_undated_deadline_is_shown_not_silently_dropped(seeded, capsys):
    data = store.load()
    data["deadlines"] = [{"what": "no date at all"},
                         {"due": "not-a-date", "what": "bad date"}]
    store.save(data)
    assert main(["deadlines"]) == 0
    out = capsys.readouterr().out
    assert "no date at all" in out and "bad date" in out


def test_free_day_today_is_still_listed(seeded, capsys, monkeypatch):
    """days_until()==0 was folded into the unparsable-date fallback."""
    monkeypatch.setenv("LIFE_TODAY", "2026-11-03")   # a printed free day
    assert main(["exams"]) == 0
    assert "2026-11-03" in capsys.readouterr().out


def test_sync_reports_a_missing_file_instead_of_raising(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("LIFE_HOME", str(tmp_path))
    monkeypatch.setenv("NO_COLOR", "1")
    assert main(["sync", str(tmp_path / "nope.json")]) == 1
    assert "Cannot read" in capsys.readouterr().out
