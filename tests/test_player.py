"""Player inherits Person and tracks its own career statistics."""

from core.person import Person
from core.player import Player


def a_player(**kw):
    defaults = dict(
        person_id=10, first_name="Kylian", last_name="Mbappe", age=27,
        nationality="France", height=178, weight=75, jersey_number=10,
        position="Forward", preferred_foot="Right", overall_rating=92,
        market_value=180, weekly_salary=500000,
    )
    defaults.update(kw)
    return Player(**defaults)


def test_player_is_a_person():
    assert isinstance(a_player(), Person)


def test_full_name_comes_from_person():
    assert a_player().full_name == "Kylian Mbappe"


def test_new_player_starts_with_zeroed_stats():
    p = a_player()
    assert p.matches_played == 0
    assert p.goals == 0
    assert p.assists == 0
    assert p.minutes_played == 0


def test_play_match_accumulates_matches_and_minutes():
    p = a_player()
    p.play_match()
    p.play_match(45)
    assert p.matches_played == 2
    assert p.minutes_played == 135


def test_score_and_assist_increment():
    p = a_player()
    p.score_goal()
    p.score_goal()
    p.give_assist()
    assert p.goals == 2
    assert p.assists == 1


def test_cards_are_tracked():
    p = a_player()
    p.receive_yellow_card()
    p.receive_red_card()
    assert p.yellow_cards == 1
    assert p.red_cards == 1


def test_str_is_the_name():
    assert str(a_player()) == "Kylian Mbappe"
