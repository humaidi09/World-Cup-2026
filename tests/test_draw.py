"""The draw must always be rule-valid: 12 groups of 4, one team per pot per
group, the confederation constraint (UEFA up to two, everyone else at most
one), reproducible under a seed, and honouring real host placement."""

import random

import pytest

from worldcup.data import load_teams
from worldcup.draw import draw_groups


def _draw(seed, real_hosts=False):
    return draw_groups(load_teams(), random.Random(seed), real_hosts=real_hosts)


def test_twelve_groups_of_four():
    groups = _draw(1)
    assert len(groups) == 12
    assert all(len(members) == 4 for members in groups.values())


def test_one_team_per_pot_per_group():
    groups = _draw(2)
    for members in groups.values():
        assert sorted(t.pot for t in members) == [1, 2, 3, 4]


@pytest.mark.parametrize("seed", range(25))
def test_confederation_constraint_holds(seed):
    groups = _draw(seed)
    for members in groups.values():
        confs = [t.confederation for t in members]
        for conf in set(confs):
            limit = 2 if conf == "UEFA" else 1
            assert confs.count(conf) <= limit


def test_all_48_teams_placed_exactly_once():
    groups = _draw(3)
    codes = [t.code for members in groups.values() for t in members]
    assert len(codes) == 48
    assert len(set(codes)) == 48


def test_reproducible_under_seed():
    a = _draw(11)
    b = _draw(11)
    a_codes = {g: [t.code for t in m] for g, m in a.items()}
    b_codes = {g: [t.code for t in m] for g, m in b.items()}
    assert a_codes == b_codes


def test_real_hosts_placement():
    groups = _draw(5, real_hosts=True)
    assert groups["A"][0].code == "MEX"
    assert groups["B"][0].code == "CAN"
    assert groups["D"][0].code == "USA"
