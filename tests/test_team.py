"""A Team owns a squad and records its competition results."""

from core.forward import Forward
from core.goalkeeper import Goalkeeper
from core.team import Team

COMMON = dict(
    age=25, nationality="France", height=180, weight=75,
    preferred_foot="Right", overall_rating=85, market_value=50,
    weekly_salary=100000,
)


def a_team():
    return Team(team_name="France", country="France", fifa_ranking=2, formation="4-3-3")


def a_forward(person_id=1, jersey_number=10):
    return Forward(person_id=person_id, first_name="Kylian", last_name="Mbappe",
                   jersey_number=jersey_number, **COMMON)


def test_new_team_has_empty_squad_and_zero_record():
    t = a_team()
    assert t.players == []
    assert t.points == 0
    assert t.matches == 0


def test_add_player_grows_the_squad():
    t = a_team()
    t.add_player(a_forward())
    assert len(t.players) == 1


def test_remove_player_by_jersey():
    t = a_team()
    t.add_player(a_forward(jersey_number=10))
    t.add_player(Goalkeeper(person_id=2, first_name="Hugo", last_name="Lloris",
                            jersey_number=1, **COMMON))
    t.remove_player(10)
    assert [p.jersey_number for p in t.players] == [1]


def test_captaincy():
    t = a_team()
    fw = a_forward()
    t.set_captain(fw)
    assert t.captain is fw


def test_record_win_draw_loss_update_points():
    t = a_team()
    t.record_win()      # +3
    t.record_draw()     # +1
    t.record_loss()     # +0
    assert t.points == 4
    assert t.matches == 3
    assert (t.wins, t.draws, t.losses) == (1, 1, 1)
