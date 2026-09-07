"""Load the bundled real-team dataset.

The data file (``data/teams_2026.json``, next to the repo root) holds the 48
real 2026 World Cup teams and a real published Elo snapshot, plus provenance
(source and date). This module turns it into ``Team`` objects and validates
that the field really is the tournament we expect: 48 teams, 12 per pot, and
the exact confederation counts of the real draw.
"""

from __future__ import annotations

import json
import os
from collections import Counter

from .team import Team

# data/teams_2026.json lives at the repo root, one level up from this package.
_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "teams_2026.json")

# The real 48-team field: totals that a valid dataset must match exactly.
EXPECTED_TEAMS = 48
EXPECTED_PER_POT = 12
EXPECTED_CONFEDERATIONS = {
    "UEFA": 16,
    "CAF": 10,
    "AFC": 9,
    "CONMEBOL": 6,
    "CONCACAF": 6,
    "OFC": 1,
}


def _validate(teams: list[Team]) -> None:
    if len(teams) != EXPECTED_TEAMS:
        raise ValueError(f"expected {EXPECTED_TEAMS} teams, found {len(teams)}")

    codes = [t.code for t in teams]
    duplicates = [code for code, n in Counter(codes).items() if n > 1]
    if duplicates:
        raise ValueError(f"duplicate team codes: {', '.join(sorted(duplicates))}")

    per_pot = Counter(t.pot for t in teams)
    for pot in (1, 2, 3, 4):
        if per_pot[pot] != EXPECTED_PER_POT:
            raise ValueError(
                f"pot {pot} has {per_pot[pot]} teams, expected {EXPECTED_PER_POT}"
            )

    per_conf = Counter(t.confederation for t in teams)
    if dict(per_conf) != EXPECTED_CONFEDERATIONS:
        raise ValueError(
            f"confederation counts {dict(per_conf)} do not match the real field "
            f"{EXPECTED_CONFEDERATIONS}"
        )


def load_dataset(path: str | None = None) -> tuple[list[Team], dict]:
    """Return ``(teams, provenance)`` from the bundled JSON (or ``path``)."""
    target = path or _DATA_PATH
    with open(target, encoding="utf-8") as handle:
        data = json.load(handle)
    teams = [Team.from_dict(row) for row in data["teams"]]
    _validate(teams)
    return teams, data.get("provenance", {})


def load_teams(path: str | None = None) -> list[Team]:
    """Return just the 48 validated teams."""
    teams, _ = load_dataset(path)
    return teams
