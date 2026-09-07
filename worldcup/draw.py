"""The group draw.

Twelve groups (A-L), one team from each of the four pots per group. The real
FIFA constraint: no group may hold two teams from the same confederation,
**except UEFA** — with 16 UEFA teams across 12 groups, a group may hold up to
two of them (and some must).

We fill pot by pot. Within a pot the teams are shuffled with the injected RNG,
then placed by backtracking: a team goes into a group whose slot for this pot
is free and whose confederation rule still holds, and if a pot cannot be
completed we backtrack and try another arrangement. A bounded number of
reshuffled restarts keeps it fast and, crucially, reproducible under ``--seed``.

With ``real_hosts=True`` the three hosts are pre-placed exactly as the real
draw fixed them — Mexico -> A, Canada -> B, USA -> D — otherwise the draw is
fully random (still rule-valid).
"""

from __future__ import annotations

import random

from .team import Team

GROUP_LABELS = [chr(ord("A") + i) for i in range(12)]  # "A".."L"

# Real host pre-placements (group index): Mexico -> A(0), Canada -> B(1), USA -> D(3).
_HOST_SLOTS = {"MEX": 0, "CAN": 1, "USA": 3}

_MAX_UEFA_PER_GROUP = 2
_MAX_RESTARTS = 20000


def _confederation_ok(group: list[Team], team: Team) -> bool:
    same = [t for t in group if t.confederation == team.confederation]
    if not same:
        return True
    # Only UEFA may double up, and only to two.
    if team.confederation == "UEFA":
        return len(same) < _MAX_UEFA_PER_GROUP
    return False


def _place_pot(
    groups: list[list[Team]],
    pot_teams: list[Team],
    fixed_group_of: dict[str, int],
) -> bool:
    """Backtracking placement of one pot's teams into the 12 groups.

    Each group receives exactly one team from this pot. Pre-placed (host) teams
    take their fixed group; the rest are assigned to the remaining open groups.
    """
    used_groups: set[int] = set()
    remaining: list[Team] = []
    for team in pot_teams:
        if team.code in fixed_group_of:
            gi = fixed_group_of[team.code]
            groups[gi].append(team)
            used_groups.add(gi)
        else:
            remaining.append(team)

    open_groups = [i for i in range(12) if i not in used_groups]
    filled: set[int] = set()

    def backtrack(idx: int) -> bool:
        if idx == len(remaining):
            return True
        team = remaining[idx]
        for gi in open_groups:
            if gi in filled:
                continue
            if _confederation_ok(groups[gi], team):
                groups[gi].append(team)
                filled.add(gi)
                if backtrack(idx + 1):
                    return True
                filled.discard(gi)
                groups[gi].pop()
        return False

    if backtrack(0):
        return True

    # Failed: undo this pot's pre-placed teams so the caller can restart clean.
    for gi in used_groups:
        groups[gi].pop()
    return False


def draw_groups(
    teams: list[Team],
    rng: random.Random,
    real_hosts: bool = False,
) -> dict[str, list[Team]]:
    """Return an ordered mapping ``{"A": [pot1, pot2, pot3, pot4], ...}``."""
    by_pot: dict[int, list[Team]] = {1: [], 2: [], 3: [], 4: []}
    for team in teams:
        by_pot[team.pot].append(team)

    fixed_group_of: dict[str, int] = {}
    if real_hosts:
        for code, gi in _HOST_SLOTS.items():
            fixed_group_of[code] = gi

    for _ in range(_MAX_RESTARTS):
        groups: list[list[Team]] = [[] for _ in range(12)]
        ok = True
        for pot in (1, 2, 3, 4):
            pot_teams = list(by_pot[pot])
            rng.shuffle(pot_teams)
            if not _place_pot(groups, pot_teams, fixed_group_of):
                ok = False
                break
        if ok and all(len(g) == 4 for g in groups):
            return {GROUP_LABELS[i]: groups[i] for i in range(12)}

    raise RuntimeError(
        "could not complete a valid draw after many attempts; "
        "check the dataset's confederation counts"
    )
