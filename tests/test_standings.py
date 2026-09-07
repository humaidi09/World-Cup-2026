"""Group standings: tables tally correctly, the official tiebreakers apply in
order (goal difference, goals for, head-to-head), and drawing of lots is
reproducible under a seed."""

import random

from worldcup.standings import (
    Match,
    TeamRecord,
    build_table,
    order_group,
    rank_third_placed,
)

GROUP = ["A", "B", "C", "D"]


def _order(matches, seed=0):
    return [rec.code for rec in order_group(GROUP, matches, random.Random(seed))]


def test_match_winner_and_round_trip():
    m = Match("A", "B", 2, 1, group="A")
    assert m.winner() == "A"
    assert Match("A", "B", 0, 0).winner() is None
    assert Match.from_dict(m.to_dict()) == m


def test_build_table_tallies_points_and_goals():
    matches = [Match("A", "B", 3, 1, group="A")]
    table = build_table(["A", "B"], matches)
    assert table["A"].points == 3
    assert table["A"].goal_difference == 2
    assert table["A"].goals_for == 3
    assert table["B"].points == 0
    assert table["B"].goal_difference == -2


def test_order_by_points_then_gd_then_gf():
    # A wins all, B beats C and D, C beats D, D loses all.
    matches = [
        Match("A", "B", 1, 0, group="A"),
        Match("A", "C", 1, 0, group="A"),
        Match("A", "D", 1, 0, group="A"),
        Match("B", "C", 1, 0, group="A"),
        Match("B", "D", 1, 0, group="A"),
        Match("C", "D", 1, 0, group="A"),
    ]
    assert _order(matches) == ["A", "B", "C", "D"]


def test_head_to_head_breaks_tie_on_overall_key():
    # A and B finish level on points, GD and GF; A won the head-to-head, so A
    # must rank above B regardless of the RNG used for lots.
    matches = [
        Match("A", "B", 1, 0, group="A"),  # A wins the head-to-head
        Match("A", "C", 0, 1, group="A"),
        Match("A", "D", 3, 0, group="A"),
        Match("B", "C", 1, 0, group="A"),
        Match("B", "D", 3, 0, group="A"),
        Match("C", "D", 0, 0, group="A"),
    ]
    # A and B: played 3, won 2, lost 1, GF 4, GA 1 — identical overall.
    for seed in range(10):
        assert _order(matches, seed)[:2] == ["A", "B"]


def test_drawing_of_lots_is_reproducible():
    # A and B are identical on everything, including a drawn head-to-head:
    # only lots can separate them, and the same seed must give the same order.
    matches = [
        Match("A", "B", 1, 1, group="A"),  # head-to-head drawn
        Match("A", "C", 1, 0, group="A"),
        Match("A", "D", 1, 0, group="A"),
        Match("B", "C", 1, 0, group="A"),
        Match("B", "D", 1, 0, group="A"),
        Match("C", "D", 0, 0, group="A"),
    ]
    first = _order(matches, seed=3)
    assert _order(matches, seed=3) == first
    assert set(first[:2]) == {"A", "B"}


def test_rank_third_placed_orders_by_overall_key():
    thirds = [
        ("A", TeamRecord("AAA", played=3, won=1, drawn=1, lost=1, goals_for=3, goals_against=3)),  # 4 pts
        ("B", TeamRecord("BBB", played=3, won=2, drawn=0, lost=1, goals_for=5, goals_against=2)),  # 6 pts
        ("C", TeamRecord("CCC", played=3, won=0, drawn=1, lost=2, goals_for=1, goals_against=6)),  # 1 pt
    ]
    ordered = [code for _label, rec in rank_third_placed(thirds, random.Random(0)) for code in [rec.code]]
    assert ordered == ["BBB", "AAA", "CCC"]


def test_rank_third_placed_lots_reproducible():
    thirds = [
        ("A", TeamRecord("AAA", played=3, won=1, drawn=0, lost=2, goals_for=2, goals_against=4)),
        ("B", TeamRecord("BBB", played=3, won=1, drawn=0, lost=2, goals_for=2, goals_against=4)),
    ]
    a = [rec.code for _l, rec in rank_third_placed(thirds, random.Random(5))]
    b = [rec.code for _l, rec in rank_third_placed(thirds, random.Random(5))]
    assert a == b
    assert set(a) == {"AAA", "BBB"}
