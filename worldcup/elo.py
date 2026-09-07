"""The prediction model: Elo -> match scoreline.

Everything here is a documented modelling choice. The engine turns two real Elo
ratings into a plausible, randomised scoreline, so results are *predictions*,
never claims of fact.

Two steps:

1. **Win expectancy** from the Elo gap, the standard Elo formula::

       E_a = 1 / (1 + 10 ** ((elo_b - elo_a + H) / 400))

   ``H`` is a small, mostly-neutral field advantage (0 for neutral games).

2. **Expected goals** from that expectancy. We spread a league-average total of
   ~2.7 goals across the two sides by how much the stronger team is favoured,
   then sample each side's goals from an independent Poisson. This yields a win,
   draw or loss *and* the goal difference / goals-for the tiebreakers need.

All randomness flows through an injected ``random.Random`` so a given ``--seed``
always reproduces the same tournament, on every machine.
"""

from __future__ import annotations

import math
import random

# League-average goals per team per game; ~2.7 total is typical for men's
# international football, so ~1.35 per side is the neutral baseline.
BASE_GOALS = 1.35

# How strongly the Elo gap tilts the goal split. Tuned so a ~100-point edge
# lifts the favourite to roughly a 1.6-goal expectation and drops the underdog
# to ~1.1 — a realistic spread, not a blowout.
GOAL_TILT = 0.60

# Keep a single team's expected goals in a sane band whatever the gap.
_MIN_LAMBDA = 0.15
_MAX_LAMBDA = 5.0


def win_expectancy(elo_a: float, elo_b: float, advantage: float = 0.0) -> float:
    """Probability-like score in (0, 1) that A is the stronger side."""
    return 1.0 / (1.0 + 10.0 ** ((elo_b - elo_a + advantage) / 400.0))


def expected_goals(elo_a: float, elo_b: float, advantage: float = 0.0) -> tuple[float, float]:
    """Map the Elo gap to (lambda_a, lambda_b) expected-goal rates."""
    e_a = win_expectancy(elo_a, elo_b, advantage)
    # Centre the split on 0.5: equal ratings -> equal BASE_GOALS each.
    lam_a = BASE_GOALS * math.exp(GOAL_TILT * (e_a - 0.5) * 2.0)
    lam_b = BASE_GOALS * math.exp(GOAL_TILT * ((1.0 - e_a) - 0.5) * 2.0)
    lam_a = min(_MAX_LAMBDA, max(_MIN_LAMBDA, lam_a))
    lam_b = min(_MAX_LAMBDA, max(_MIN_LAMBDA, lam_b))
    return lam_a, lam_b


def _poisson(lam: float, rng: random.Random) -> int:
    """Sample a Poisson count using Knuth's algorithm on the injected RNG."""
    limit = math.exp(-lam)
    k = 0
    product = 1.0
    while True:
        product *= rng.random()
        if product <= limit:
            return k
        k += 1


def simulate_scoreline(
    elo_a: float,
    elo_b: float,
    rng: random.Random,
    advantage: float = 0.0,
) -> tuple[int, int]:
    """Return a sampled (goals_a, goals_b) for one match."""
    lam_a, lam_b = expected_goals(elo_a, elo_b, advantage)
    return _poisson(lam_a, rng), _poisson(lam_b, rng)


def knockout_winner_is_a(
    elo_a: float,
    elo_b: float,
    rng: random.Random,
    advantage: float = 0.0,
) -> bool:
    """Resolve a drawn knockout by an Elo-weighted coin flip.

    Draws aren't allowed past the group stage, so when regulation is level we
    decide extra-time/penalties in proportion to the two sides' win expectancy
    (renormalised to exclude the draw). Reproducible under the injected RNG.
    """
    e_a = win_expectancy(elo_a, elo_b, advantage)
    return rng.random() < e_a
