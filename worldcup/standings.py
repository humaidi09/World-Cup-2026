"""Group standings: build each group's table from its played matches, order it
by the official FIFA tiebreakers, and rank the third-placed teams to find the
eight best that also advance.

Tiebreaker order applied (FIFA World Cup group stage):

  1. points (win 3, draw 1)
  2. goal difference across all group matches
  3. goals for across all group matches
  4. head-to-head among only the teams still level: points, then goal
     difference, then goals for in the matches between just those teams
  5. drawing of lots

FIFA lists a fair-play (disciplinary) criterion between 4 and 5. This engine
does not model bookings, and inventing card counts would break the project's
"real data only" rule, so that one criterion is omitted; the drawing of lots
(a seeded RNG, documented here as a stand-in for the real draw) resolves any
tie that head-to-head cannot. Every standings output is a PREDICTION.

This module is pure: it computes tables and orderings from match results and a
seeded RNG. All printing lives in the CLI.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import groupby

WIN_POINTS = 3
DRAW_POINTS = 1


@dataclass(frozen=True)
class Match:
    """One played match between two teams, ``a`` versus ``b``.

    Group matches are treated as neutral-venue: no home advantage is applied,
    because the engine does not carry real per-match venue assignments and
    inventing them would break the real-data rule. ``group`` is the group label
    for group-stage matches, or ``None`` for knockout matches added later.
    """

    a: str
    b: str
    goals_a: int
    goals_b: int
    group: str | None = None

    def winner(self) -> str | None:
        """Code of the winner, or ``None`` if drawn."""
        if self.goals_a > self.goals_b:
            return self.a
        if self.goals_b > self.goals_a:
            return self.b
        return None

    def to_dict(self) -> dict:
        return {
            "a": self.a,
            "b": self.b,
            "goals_a": self.goals_a,
            "goals_b": self.goals_b,
            "group": self.group,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Match":
        return cls(
            a=data["a"],
            b=data["b"],
            goals_a=int(data["goals_a"]),
            goals_b=int(data["goals_b"]),
            group=data.get("group"),
        )


@dataclass
class TeamRecord:
    """A team's running tally within one table (a group, or a mini head-to-head)."""

    code: str
    played: int = 0
    won: int = 0
    drawn: int = 0
    lost: int = 0
    goals_for: int = 0
    goals_against: int = 0

    @property
    def points(self) -> int:
        return self.won * WIN_POINTS + self.drawn * DRAW_POINTS

    @property
    def goal_difference(self) -> int:
        return self.goals_for - self.goals_against

    def _record(self, scored: int, conceded: int) -> None:
        self.played += 1
        self.goals_for += scored
        self.goals_against += conceded
        if scored > conceded:
            self.won += 1
        elif scored < conceded:
            self.lost += 1
        else:
            self.drawn += 1

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "played": self.played,
            "won": self.won,
            "drawn": self.drawn,
            "lost": self.lost,
            "goals_for": self.goals_for,
            "goals_against": self.goals_against,
            "points": self.points,
            "goal_difference": self.goal_difference,
        }


def _overall_key(rec: TeamRecord) -> tuple[int, int, int]:
    """Points, then goal difference, then goals for — all descending."""
    return (rec.points, rec.goal_difference, rec.goals_for)


def build_table(codes: list[str], matches: list[Match]) -> dict[str, TeamRecord]:
    """Tally ``codes`` over ``matches`` that involve only those codes."""
    table = {code: TeamRecord(code) for code in codes}
    wanted = set(codes)
    for m in matches:
        if m.a in wanted and m.b in wanted:
            table[m.a]._record(m.goals_a, m.goals_b)
            table[m.b]._record(m.goals_b, m.goals_a)
    return table


def _break_tie(block: list[str], matches: list[Match], rng) -> list[str]:
    """Order teams tied on the overall key using head-to-head, then lots."""
    h2h = build_table(block, matches)  # only matches among the tied teams count
    ordered: list[str] = []
    by_h2h = sorted(block, key=lambda c: _overall_key(h2h[c]), reverse=True)
    for _, group_iter in groupby(by_h2h, key=lambda c: _overall_key(h2h[c])):
        still_level = list(group_iter)
        if len(still_level) == 1:
            ordered.append(still_level[0])
        else:
            # Head-to-head could not separate these teams: drawing of lots.
            rng.shuffle(still_level)
            ordered.extend(still_level)
    return ordered


def order_group(codes: list[str], matches: list[Match], rng) -> list[TeamRecord]:
    """Return the group's teams ordered 1st→last by the official tiebreakers."""
    table = build_table(codes, matches)
    by_overall = sorted(codes, key=lambda c: _overall_key(table[c]), reverse=True)
    ordered_codes: list[str] = []
    for _, group_iter in groupby(by_overall, key=lambda c: _overall_key(table[c])):
        block = list(group_iter)
        if len(block) == 1:
            ordered_codes.append(block[0])
        else:
            ordered_codes.extend(_break_tie(block, matches, rng))
    return [table[c] for c in ordered_codes]


def rank_third_placed(
    thirds: list[tuple[str, TeamRecord]], rng
) -> list[tuple[str, TeamRecord]]:
    """Rank the third-placed teams (``(group_label, record)`` pairs) best→worst.

    Third-placed teams never met, so head-to-head does not apply: they are
    ranked on the overall key, and any remaining tie goes to drawing of lots.
    The caller takes the top eight as the best-third qualifiers.
    """
    ordered: list[tuple[str, TeamRecord]] = []
    by_overall = sorted(thirds, key=lambda pair: _overall_key(pair[1]), reverse=True)
    for _, group_iter in groupby(by_overall, key=lambda pair: _overall_key(pair[1])):
        block = list(group_iter)
        if len(block) > 1:
            rng.shuffle(block)
        ordered.extend(block)
    return ordered
