"""Each position sets its own ``position`` label, keeps its own specialised
statistics, and overrides ``play_match`` while still counting the match."""

import pytest

from core.defender import Defender
from core.forward import Forward
from core.goalkeeper import Goalkeeper
from core.midfielder import Midfielder
from core.player import Player

COMMON = dict(
    first_name="Test", last_name="Player", age=25, nationality="France",
    height=180, weight=75, jersey_number=7, preferred_foot="Right",
    overall_rating=85, market_value=50, weekly_salary=100000,
)


def make(cls, person_id):
    return cls(person_id=person_id, **COMMON)


@pytest.mark.parametrize(
    "cls, label",
    [
        (Goalkeeper, "Goalkeeper"),
        (Defender, "Defender"),
        (Midfielder, "Midfielder"),
        (Forward, "Forward"),
    ],
)
def test_position_label_is_set(cls, label):
    player = make(cls, 1)
    assert player.position == label
    assert isinstance(player, Player)


def test_forward_shooting_stats():
    fw = make(Forward, 1)
    fw.shoot()
    fw.shot_on_target()
    fw.finish()
    fw.header_goal()
    fw.volley_goal()
    assert fw.shots == 2            # shoot() + shot_on_target()
    assert fw.shots_on_target == 1
    assert fw.header_goals == 1
    assert fw.volley_goals == 1
    assert fw.goals == 3            # finish + header + volley


def test_defender_stats():
    d = make(Defender, 1)
    d.tackle()
    d.intercept()
    d.clear_ball()
    d.block_shot()
    assert (d.tackles, d.interceptions, d.clearances, d.blocks) == (1, 1, 1, 1)


def test_midfielder_stats():
    m = make(Midfielder, 1)
    m.key_pass()
    m.long_pass()
    m.through_ball()
    m.create_chance()
    assert (m.key_passes, m.long_passes, m.through_balls, m.chances_created) == (1, 1, 1, 1)


def test_goalkeeper_stats():
    gk = make(Goalkeeper, 1)
    gk.save_shot()
    gk.save_penalty()
    gk.keep_clean_sheet()
    assert (gk.saves, gk.penalty_saves, gk.clean_sheets) == (1, 1, 1)


@pytest.mark.parametrize("cls", [Goalkeeper, Defender, Midfielder, Forward])
def test_play_match_override_still_counts_the_match(cls):
    # Overriding play_match must still call up into Player via super().
    player = make(cls, 1)
    player.play_match()
    assert player.matches_played == 1
    assert player.minutes_played == 90
