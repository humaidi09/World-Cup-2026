"""The tournament façade: a draw survives a JSON save/load round-trip."""

import random

from worldcup.tournament import Tournament


def test_fresh_tournament_has_48_teams():
    t = Tournament()
    assert len(t.teams) == 48
    assert t.groups == {}


def test_save_load_round_trip_preserves_draw(tmp_path):
    path = str(tmp_path / "t.json")
    original = Tournament()
    original.run_draw(random.Random(1))
    original.save(path)

    loaded = Tournament.load(path)
    assert [t.code for t in loaded.teams] == [t.code for t in original.teams]
    original_groups = {g: [t.code for t in m] for g, m in original.groups.items()}
    loaded_groups = {g: [t.code for t in m] for g, m in loaded.groups.items()}
    assert loaded_groups == original_groups


def test_save_is_atomic_no_temp_left(tmp_path):
    path = str(tmp_path / "t.json")
    t = Tournament()
    t.run_draw(random.Random(1))
    t.save(path)
    leftovers = [p for p in tmp_path.iterdir() if p.suffix == ".tmp"]
    assert leftovers == []


def test_team_lookup_by_code():
    t = Tournament()
    assert t.team("BRA").name == "Brazil"


# ---- group stage --------------------------------------------------------


def _simulated(seed=1):
    t = Tournament()
    t.run_draw(random.Random(seed))
    t.simulate_group_stage(random.Random(seed))
    return t


def test_simulate_produces_full_round_robin():
    t = _simulated()
    assert len(t.results) == 72  # 12 groups x 6 matches
    for label in t.group_order:
        assert len(t.group_table(label)) == 4
        assert all(rec.played == 3 for rec in t.group_table(label))


def test_simulate_requires_a_draw():
    t = Tournament()
    try:
        t.simulate_group_stage(random.Random(1))
    except ValueError:
        pass
    else:  # pragma: no cover
        raise AssertionError("expected ValueError when no draw exists")


def test_exactly_32_unique_real_qualifiers():
    t = _simulated()
    qualifiers = t.qualifiers()
    assert len(qualifiers) == 32
    assert len(set(qualifiers)) == 32
    assert len(t.winners()) == 12
    assert len(t.runners_up()) == 12
    assert len(t.best_thirds) == 8
    real_codes = {team.code for team in t.teams}
    assert set(qualifiers) <= real_codes


def test_simulation_is_reproducible_under_seed():
    a = _simulated(7)
    b = _simulated(7)
    assert a.group_order == b.group_order
    assert a.best_thirds == b.best_thirds
    assert [m.to_dict() for m in a.results] == [m.to_dict() for m in b.results]


def test_group_stage_survives_round_trip(tmp_path):
    path = str(tmp_path / "t.json")
    original = _simulated(2)
    original.save(path)
    loaded = Tournament.load(path)
    assert loaded.group_order == original.group_order
    assert loaded.best_thirds == original.best_thirds
    assert loaded.qualifiers() == original.qualifiers()


def test_winners_finish_above_runners_up():
    t = _simulated(4)
    for label in t.group_order:
        table = t.group_table(label)
        assert table[0].points >= table[1].points


# ---- knockout stage -----------------------------------------------------


def _played(seed=1):
    t = _simulated(seed)
    t.simulate_knockout(random.Random(seed))
    return t


def test_knockout_requires_group_stage():
    t = Tournament()
    t.run_draw(random.Random(1))
    try:
        t.simulate_knockout(random.Random(1))
    except ValueError:
        pass
    else:  # pragma: no cover
        raise AssertionError("expected ValueError before the group stage")


def test_champion_is_a_qualifier():
    t = _played()
    assert t.champion in t.qualifiers()
    assert t.is_knockout_done()


def test_round_of_32_uses_only_qualifiers():
    t = _played()
    codes = [code for pair in t.round_of_32() for code in pair]
    assert len(codes) == 32
    assert set(codes) == set(t.qualifiers())


def test_full_run_reproducible_and_survives_round_trip(tmp_path):
    a = _played(6)
    b = _played(6)
    assert a.champion == b.champion
    assert [m.to_dict() for m in a.knockout] == [m.to_dict() for m in b.knockout]

    path = str(tmp_path / "t.json")
    a.save(path)
    loaded = Tournament.load(path)
    assert loaded.champion == a.champion
    assert loaded.runner_up == a.runner_up
    assert loaded.third_place == a.third_place
    assert [m.to_dict() for m in loaded.knockout] == [m.to_dict() for m in a.knockout]


def test_podium_is_four_distinct_teams():
    t = _played(2)
    podium = {t.champion, t.runner_up, t.third_place, t.fourth_place}
    assert len(podium) == 4


# ---- Monte Carlo prediction ---------------------------------------------


def test_predict_probabilities_are_coherent():
    t = Tournament()
    t.run_draw(random.Random(1), real_hosts=True)
    sims = 60
    probs = t.predict(sims, random.Random(1))

    # Every team appears; every probability is in [0, 1].
    assert len(probs) == 48
    for p in probs.values():
        for value in p.values():
            assert 0.0 <= value <= 1.0

    # Exactly one champion per run: champion probabilities sum to ~1.
    total_champion = sum(p["champion"] for p in probs.values())
    assert abs(total_champion - 1.0) < 1e-9

    # Reaching is monotonic: champion <= final <= sf <= qf <= r16 for each team.
    for p in probs.values():
        assert p["champion"] <= p["final"] <= p["sf"] <= p["qf"] <= p["r16"]


def test_predict_is_reproducible_under_seed():
    t = Tournament()
    t.run_draw(random.Random(3), real_hosts=True)
    a = t.predict(40, random.Random(5))
    b = t.predict(40, random.Random(5))
    assert a == b


def test_predict_requires_a_draw():
    t = Tournament()
    try:
        t.predict(10, random.Random(1))
    except ValueError:
        pass
    else:  # pragma: no cover
        raise AssertionError("expected ValueError without a draw")



