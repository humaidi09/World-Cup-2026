"""The bundled dataset must really be the 2026 field: 48 real teams, 12 per
pot, and the exact confederation counts of the real draw."""

import pytest

from worldcup.data import EXPECTED_CONFEDERATIONS, load_dataset, load_teams
from worldcup.team import Team


def test_loads_48_teams():
    teams = load_teams()
    assert len(teams) == 48
    assert all(isinstance(t, Team) for t in teams)


def test_twelve_per_pot():
    teams = load_teams()
    for pot in (1, 2, 3, 4):
        assert sum(1 for t in teams if t.pot == pot) == 12


def test_confederation_counts_match_real_field():
    teams = load_teams()
    counts = {}
    for t in teams:
        counts[t.confederation] = counts.get(t.confederation, 0) + 1
    assert counts == EXPECTED_CONFEDERATIONS


def test_three_hosts_present():
    teams = load_teams()
    hosts = {t.code for t in teams if t.host}
    assert hosts == {"USA", "MEX", "CAN"}


def test_codes_unique():
    teams = load_teams()
    codes = [t.code for t in teams]
    assert len(codes) == len(set(codes))


def test_provenance_cites_source_and_date():
    _, provenance = load_dataset()
    assert "eloratings.net" in provenance["elo_source"]
    assert provenance["elo_as_of"]


def test_validation_rejects_wrong_count(tmp_path):
    import json
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"teams": [
        {"code": "AAA", "name": "A", "confederation": "UEFA", "pot": 1,
         "host": False, "elo": 1500},
    ]}), encoding="utf-8")
    with pytest.raises(ValueError):
        load_teams(str(bad))
