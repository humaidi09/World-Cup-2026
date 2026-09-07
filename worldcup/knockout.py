"""The knockout bracket: Round of 32 through the final, plus the third-place
play-off.

The bracket *skeleton* here is the real, published FIFA World Cup 2026 one:

  * the fixed Round of 32 schedule (Matches 73-88) with its winner / runner-up
    slots, and which groups' third-placed teams are eligible for each of the
    eight "winner vs third" slots, and
  * how Round of 16, quarter-final, semi-final, final and third-place matches
    connect.

FIFA also publishes a 495-row table saying exactly which qualifying third-place
team fills each slot for every possible combination of the eight groups whose
third-placed teams advance. That table is impractical to bundle in full, so the
eight thirds are assigned to their slots by a deterministic constraint solver
that honours the real per-slot eligibility. This one step is a documented
modelling simplification, not the official allocation; everything else is the
real bracket. Every result produced here is a PREDICTION, not a real result.

This module is pure: it resolves and plays the bracket from qualifiers, an Elo
lookup and a seeded RNG. All printing lives in the CLI.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .elo import knockout_winner_is_a, simulate_scoreline

# ---- the real Round of 32 schedule (Matches 73-88) ----------------------
# Each side is ("W", group) winner, ("R", group) runner-up, or ("T", slot)
# a third-placed team assigned to that slot. Order is Matches 73..88.
ROUND_OF_32: list[tuple[tuple[str, str], tuple[str, str]]] = [
    (("R", "A"), ("R", "B")),   # 73
    (("W", "E"), ("T", "1E")),  # 74
    (("W", "F"), ("R", "C")),   # 75
    (("W", "C"), ("R", "F")),   # 76
    (("W", "I"), ("T", "1I")),  # 77
    (("R", "E"), ("R", "I")),   # 78
    (("W", "A"), ("T", "1A")),  # 79
    (("W", "L"), ("T", "1L")),  # 80
    (("W", "D"), ("T", "1D")),  # 81
    (("W", "G"), ("T", "1G")),  # 82
    (("R", "K"), ("R", "L")),   # 83
    (("W", "H"), ("R", "J")),   # 84
    (("W", "B"), ("T", "1B")),  # 85
    (("W", "J"), ("R", "H")),   # 86
    (("W", "K"), ("T", "1K")),  # 87
    (("R", "D"), ("R", "G")),   # 88
]

# Real per-slot eligibility: which groups' third-placed teams may fill each of
# the eight "winner vs third" slots.
THIRD_SLOT_ELIGIBILITY: dict[str, frozenset[str]] = {
    "1A": frozenset("CEFHI"),
    "1B": frozenset("EFGIJ"),
    "1D": frozenset("BEFIJ"),
    "1E": frozenset("ABCDF"),
    "1G": frozenset("AEHIJ"),
    "1I": frozenset("CDFGH"),
    "1K": frozenset("DEIJL"),
    "1L": frozenset("EHIJK"),
}
# A fixed slot order makes the constraint solver's output deterministic.
_THIRD_SLOTS = ["1A", "1B", "1D", "1E", "1G", "1I", "1K", "1L"]

# How later rounds pair the winners of earlier matches (indices into the
# previous round's match list, in the real bracket's order).
ROUND_OF_16_PAIRS = [(1, 4), (0, 2), (3, 5), (6, 7), (10, 11), (8, 9), (13, 15), (12, 14)]
QUARTER_FINAL_PAIRS = [(0, 1), (4, 5), (2, 3), (6, 7)]
SEMI_FINAL_PAIRS = [(0, 1), (2, 3)]


@dataclass(frozen=True)
class KnockoutMatch:
    """One played knockout tie. ``decided_on`` is "regulation" or "penalties"."""

    round: str
    a: str
    b: str
    goals_a: int
    goals_b: int
    winner: str
    decided_on: str

    def loser(self) -> str:
        return self.b if self.winner == self.a else self.a

    def to_dict(self) -> dict:
        return {
            "round": self.round,
            "a": self.a,
            "b": self.b,
            "goals_a": self.goals_a,
            "goals_b": self.goals_b,
            "winner": self.winner,
            "decided_on": self.decided_on,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "KnockoutMatch":
        return cls(
            round=data["round"],
            a=data["a"],
            b=data["b"],
            goals_a=int(data["goals_a"]),
            goals_b=int(data["goals_b"]),
            winner=data["winner"],
            decided_on=data["decided_on"],
        )


def allocate_thirds(qualifying_groups: list[str]) -> dict[str, str]:
    """Assign the eight qualifying third-place groups to the eight bracket slots.

    Returns ``{slot: group}``. Honours the real per-slot eligibility; the exact
    choice among valid assignments is a documented modelling simplification
    (see the module docstring), made deterministic by fixed slot/group order.
    """
    if len(qualifying_groups) != len(_THIRD_SLOTS):
        raise ValueError(
            f"expected {len(_THIRD_SLOTS)} qualifying third-place groups, "
            f"got {len(qualifying_groups)}"
        )
    groups = sorted(qualifying_groups)
    assignment: dict[str, str] = {}
    used: set[str] = set()

    def solve(slot_index: int) -> bool:
        if slot_index == len(_THIRD_SLOTS):
            return True
        slot = _THIRD_SLOTS[slot_index]
        for group in groups:
            if group in used or group not in THIRD_SLOT_ELIGIBILITY[slot]:
                continue
            assignment[slot] = group
            used.add(group)
            if solve(slot_index + 1):
                return True
            used.discard(group)
            del assignment[slot]
        return False

    if not solve(0):
        raise ValueError(
            f"no valid third-place allocation for groups {sorted(qualifying_groups)}"
        )
    return assignment


def build_round_of_32(
    winners: dict[str, str],
    runners_up: dict[str, str],
    thirds_by_group: dict[str, str],
) -> list[tuple[str, str]]:
    """Resolve the Round of 32 slot schedule into 16 concrete ``(a, b)`` code pairs.

    ``thirds_by_group`` maps each qualifying group label to its third-placed
    team's code (exactly the eight groups whose thirds advanced).
    """
    slot_to_group = allocate_thirds(list(thirds_by_group))
    slot_to_code = {slot: thirds_by_group[group] for slot, group in slot_to_group.items()}

    def resolve(side: tuple[str, str]) -> str:
        kind, key = side
        if kind == "W":
            return winners[key]
        if kind == "R":
            return runners_up[key]
        return slot_to_code[key]  # "T"

    return [(resolve(a), resolve(b)) for a, b in ROUND_OF_32]


def _play_match(
    a: str, b: str, round_name: str, elo_of: Callable[[str], float], rng
) -> KnockoutMatch:
    """Play one tie: a seeded scoreline, decided on penalties if drawn."""
    goals_a, goals_b = simulate_scoreline(elo_of(a), elo_of(b), rng)
    if goals_a != goals_b:
        winner = a if goals_a > goals_b else b
        decided = "regulation"
    else:
        winner = a if knockout_winner_is_a(elo_of(a), elo_of(b), rng) else b
        decided = "penalties"
    return KnockoutMatch(round_name, a, b, goals_a, goals_b, winner, decided)


def _play_round(
    pairs: list[tuple[str, str]], round_name: str, elo_of: Callable[[str], float], rng
) -> list[KnockoutMatch]:
    return [_play_match(a, b, round_name, elo_of, rng) for a, b in pairs]


@dataclass
class KnockoutResult:
    matches: list[KnockoutMatch]
    champion: str
    runner_up: str
    third: str
    fourth: str


def simulate_knockout(
    round_of_32: list[tuple[str, str]], elo_of: Callable[[str], float], rng
) -> KnockoutResult:
    """Play the whole bracket from the Round of 32 down to the champion."""
    r32 = _play_round(round_of_32, "Round of 32", elo_of, rng)

    r16_pairs = [(r32[i].winner, r32[j].winner) for i, j in ROUND_OF_16_PAIRS]
    r16 = _play_round(r16_pairs, "Round of 16", elo_of, rng)

    qf_pairs = [(r16[i].winner, r16[j].winner) for i, j in QUARTER_FINAL_PAIRS]
    qf = _play_round(qf_pairs, "Quarter-final", elo_of, rng)

    sf_pairs = [(qf[i].winner, qf[j].winner) for i, j in SEMI_FINAL_PAIRS]
    sf = _play_round(sf_pairs, "Semi-final", elo_of, rng)

    third_place = _play_match(sf[0].loser(), sf[1].loser(), "Third-place play-off", elo_of, rng)
    final = _play_match(sf[0].winner, sf[1].winner, "Final", elo_of, rng)

    matches = r32 + r16 + qf + sf + [third_place, final]
    return KnockoutResult(
        matches=matches,
        champion=final.winner,
        runner_up=final.loser(),
        third=third_place.winner,
        fourth=third_place.loser(),
    )
