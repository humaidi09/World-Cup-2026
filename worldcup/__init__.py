"""A real, offline FIFA World Cup 2026 simulation & prediction engine.

The package is layered so each part has one job and the core does no I/O:

    team        the tournament team value object (real side + Elo)
    data        load the bundled real 48-team dataset (with provenance)
    elo         the Elo -> scoreline prediction model
    draw        the pot-based, rule-correct group draw
    standings   group tables, official tiebreakers, best-thirds ranking
    knockout    the real published bracket, played to a champion
    tournament  the façade tying it together, with JSON persistence
    cli         the command-line interface (all printing lives here)

Every simulated result is a PREDICTION, not a claim of fact. Runs are
reproducible under a --seed.
"""

from __future__ import annotations

__version__ = "1.0.0"

from .team import Team
from .data import load_dataset, load_teams
from .standings import Match, TeamRecord
from .knockout import KnockoutMatch
from .tournament import Tournament

__all__ = [
    "Team",
    "load_dataset",
    "load_teams",
    "Match",
    "TeamRecord",
    "KnockoutMatch",
    "Tournament",
    "__version__",
]
