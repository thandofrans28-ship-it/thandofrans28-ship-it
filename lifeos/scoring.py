"""University admission arithmetic.

Two scores decide the 2027 Electrical Engineering places. Both are reproduced
here exactly, and both are pinned in ``tests/`` against hand-computed totals
so a refactor cannot quietly change a university decision.

UCT — BSc(Eng) Electrical & Computer Engineering
    FPS = English + Mathematics + Physical Sciences + the three next-best
    subjects, Life Orientation excluded. Out of 600.
    Band A guarantee: FPS >= 500 with Mathematics >= 80 and PhysSci >= 75.

Stellenbosch — BEng Electrical & Electronic
    Selection Score = Mathematics + Physical Sciences + 6 x (best-six average),
    Life Orientation excluded. Out of 800. 2027 provisional threshold 620.

    6 x mean(best six) equals sum(best six) only when exactly six subjects are
    available. A partial marks dict — which `life sync` explicitly allows — has
    fewer, and summing there understates the score badly. The mean is computed.
"""

from __future__ import annotations

from dataclasses import dataclass, field

LO = "Life Orientation"

UCT_FPS_TARGET = 500
UCT_MATHS_MIN = 80
UCT_PHYSSCI_MIN = 75
SU_TARGET = 620


@dataclass
class Score:
    total: int
    target: int
    counting: dict[str, int] = field(default_factory=dict)
    gates: dict[str, bool] = field(default_factory=dict)
    partial: bool = False
    """True when fewer subjects were supplied than the formula expects, so the
    total is an estimate from an incomplete transcript rather than a result."""

    @property
    def failed_gates(self) -> list[str]:
        return [name for name, ok in self.gates.items() if not ok]

    @property
    def gap(self) -> int:
        """Points still needed. Zero once the target is met."""
        return max(0, self.target - self.total)

    @property
    def meets_target(self) -> bool:
        return self.total >= self.target

    @property
    def clear(self) -> bool:
        """Target met *and* every subject minimum satisfied."""
        return self.meets_target and all(self.gates.values())


def _without_lo(marks: dict[str, int]) -> dict[str, int]:
    return {k: v for k, v in marks.items() if k != LO}


def uct_fps(marks: dict[str, int]) -> Score:
    """UCT Faculty Points Score.

    ``marks`` maps subject name to percentage and must contain English,
    Mathematics and Physical Sciences.
    """
    required = ("English", "Mathematics", "Physical Sciences")
    missing = [s for s in required if s not in marks]
    if missing:
        raise ValueError(f"UCT FPS needs {', '.join(missing)}")

    pool = _without_lo(marks)
    counting = {s: pool[s] for s in required}
    others = sorted(
        ((s, v) for s, v in pool.items() if s not in required),
        key=lambda kv: (-kv[1], kv[0]),
    )[:3]
    counting.update(dict(others))

    return Score(
        total=sum(counting.values()),
        target=UCT_FPS_TARGET,
        counting=counting,
        partial=len(counting) < 6,
        gates={
            f"Mathematics >= {UCT_MATHS_MIN}": marks.get("Mathematics", 0) >= UCT_MATHS_MIN,
            f"Physical Sciences >= {UCT_PHYSSCI_MIN}": marks.get("Physical Sciences", 0) >= UCT_PHYSSCI_MIN,
        },
    )


def su_selection(marks: dict[str, int]) -> Score:
    """Stellenbosch BEng Electrical & Electronic selection score."""
    required = ("Mathematics", "Physical Sciences")
    missing = [s for s in required if s not in marks]
    if missing:
        raise ValueError(f"SU selection score needs {', '.join(missing)}")

    pool = _without_lo(marks)
    best_six = sorted(pool.items(), key=lambda kv: (-kv[1], kv[0]))[:6]
    if not best_six:
        raise ValueError("SU selection score needs at least one non-LO subject")

    average = sum(v for _, v in best_six) / len(best_six)
    total = round(marks["Mathematics"] + marks["Physical Sciences"] + 6 * average)

    return Score(
        total=total,
        target=SU_TARGET,
        counting=dict(best_six),
        gates={},
        partial=len(best_six) < 6,
    )


def improvement_plan(marks: dict[str, int], targets: dict[str, int]) -> list[dict]:
    """What each planned mark improvement is worth, ranked by FPS gain.

    A mark that is not in the six counting subjects buys nothing at UCT even
    when it rises — this is what makes the ranking worth computing rather
    than guessing.
    """
    base_fps = uct_fps(marks).total
    base_su = su_selection(marks).total

    rows = []
    for subject, goal in targets.items():
        current = marks.get(subject)
        if current is None or goal <= current:
            continue
        lifted = dict(marks, **{subject: goal})
        rows.append(
            {
                "subject": subject,
                "from": current,
                "to": goal,
                "marks_needed": goal - current,
                "fps_gain": uct_fps(lifted).total - base_fps,
                "su_gain": su_selection(lifted).total - base_su,
            }
        )
    rows.sort(key=lambda r: (-r["fps_gain"], -r["su_gain"], r["marks_needed"]))
    return rows
