"""The knockout bracket: the real R32 skeleton resolves correctly, the
third-place allocation honours the published eligibility, and a full run always
yields one champion drawn from the qualifiers — reproducibly under a seed."""

import random

from worldcup.knockout import (
    ROUND_OF_32,
    THIRD_SLOT_ELIGIBILITY,
    allocate_thirds,
    build_round_of_32,
    simulate_knockout,
)


def test_allocation_respects_real_eligibility():
    # The actual 2026 case: thirds from groups B, D, E, F, I, J, K, L advanced.
    groups = ["B", "D", "E", "F", "I", "J", "K", "L"]
    slot_to_group = allocate_thirds(groups)
    assert sorted(slot_to_group.values()) == sorted(groups)  # a bijection
    for slot, group in slot_to_group.items():
        assert group in THIRD_SLOT_ELIGIBILITY[slot]


def test_allocation_is_deterministic():
    groups = ["A", "C", "E", "F", "H", "I", "J", "K"]
    assert allocate_thirds(groups) == allocate_thirds(groups)


def test_allocation_rejects_wrong_count():
    try:
        allocate_thirds(["A", "B", "C"])
    except ValueError:
        pass
    else:  # pragma: no cover
        raise AssertionError("expected ValueError for too few groups")


def _fake_qualifiers():
    labels = "ABCDEFGHIJKL"
    winners = {g: f"W{g}" for g in labels}
    runners = {g: f"R{g}" for g in labels}
    # Eight groups whose thirds advance (a real, satisfiable combination).
    thirds = {g: f"T{g}" for g in "BDEFIJKL"}
    return winners, runners, thirds


def test_build_round_of_32_has_16_pairs_of_32_teams():
    winners, runners, thirds = _fake_qualifiers()
    pairs = build_round_of_32(winners, runners, thirds)
    assert len(pairs) == len(ROUND_OF_32) == 16
    teams = [code for pair in pairs for code in pair]
    assert len(teams) == 32
    assert len(set(teams)) == 32  # every qualifier appears exactly once


def _elo_of(code):
    # Deterministic pseudo-Elo so tests need no dataset: spread by the code text.
    return 1400 + (sum(ord(c) for c in code) % 800)


def test_full_bracket_yields_one_champion_from_the_field():
    winners, runners, thirds = _fake_qualifiers()
    r32 = build_round_of_32(winners, runners, thirds)
    field = {code for pair in r32 for code in pair}
    result = simulate_knockout(r32, _elo_of, random.Random(1))
    # 16 + 8 + 4 + 2 + third-place + final = 32 matches.
    assert len(result.matches) == 32
    for code in (result.champion, result.runner_up, result.third, result.fourth):
        assert code in field
    podium = {result.champion, result.runner_up, result.third, result.fourth}
    assert len(podium) == 4  # four distinct teams on the podium


def test_knockout_is_reproducible_under_seed():
    winners, runners, thirds = _fake_qualifiers()
    r32 = build_round_of_32(winners, runners, thirds)
    a = simulate_knockout(r32, _elo_of, random.Random(9))
    b = simulate_knockout(r32, _elo_of, random.Random(9))
    assert a.champion == b.champion
    assert [m.to_dict() for m in a.matches] == [m.to_dict() for m in b.matches]


def test_no_knockout_match_is_drawn():
    winners, runners, thirds = _fake_qualifiers()
    r32 = build_round_of_32(winners, runners, thirds)
    result = simulate_knockout(r32, _elo_of, random.Random(3))
    for m in result.matches:
        assert m.winner in (m.a, m.b)
        if m.goals_a == m.goals_b:
            assert m.decided_on == "penalties"
