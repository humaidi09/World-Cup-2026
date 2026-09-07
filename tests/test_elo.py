"""The Elo prediction model: expectancy symmetry, goal mapping, and that a
seeded RNG makes scorelines reproducible."""

import random

from worldcup.elo import (
    expected_goals,
    knockout_winner_is_a,
    simulate_scoreline,
    win_expectancy,
)


def test_equal_ratings_are_a_coin_flip():
    assert win_expectancy(1800, 1800) == 0.5


def test_expectancy_is_symmetric():
    a = win_expectancy(2000, 1600)
    b = win_expectancy(1600, 2000)
    assert abs((a + b) - 1.0) < 1e-9


def test_stronger_team_favoured():
    assert win_expectancy(2000, 1600) > 0.5


def test_equal_ratings_give_equal_goal_rates():
    lam_a, lam_b = expected_goals(1800, 1800)
    assert abs(lam_a - lam_b) < 1e-9


def test_stronger_team_has_higher_goal_rate():
    lam_a, lam_b = expected_goals(2100, 1500)
    assert lam_a > lam_b


def test_scoreline_reproducible_under_seed():
    r1 = random.Random(42)
    r2 = random.Random(42)
    seq1 = [simulate_scoreline(1900, 1700, r1) for _ in range(20)]
    seq2 = [simulate_scoreline(1900, 1700, r2) for _ in range(20)]
    assert seq1 == seq2


def test_scoreline_returns_two_nonnegative_ints():
    rng = random.Random(1)
    gh, ga = simulate_scoreline(1800, 1800, rng)
    assert isinstance(gh, int) and isinstance(ga, int)
    assert gh >= 0 and ga >= 0


def test_knockout_flip_reproducible_and_favours_strong():
    r1 = random.Random(7)
    r2 = random.Random(7)
    a = [knockout_winner_is_a(2100, 1500, r1) for _ in range(200)]
    b = [knockout_winner_is_a(2100, 1500, r2) for _ in range(200)]
    assert a == b
    # The far stronger side should advance in the clear majority of flips.
    assert sum(a) > 150
