"""FIFA World Cup 2026 Management System — a runnable demonstration.

Builds one player of each position, plays a short simulated match and prints
the squad and every per-position report, so the inheritance hierarchy
(Person -> Player -> Goalkeeper/Defender/Midfielder/Forward) can be seen in
action from a single run.
"""

import sys

from core.goalkeeper import Goalkeeper
from core.defender import Defender
from core.midfielder import Midfielder
from core.forward import Forward
from core.team import Team

# The reports use emoji (⚽, 🧤, ...). A Windows console defaults to the cp1252
# code page, which cannot encode them and would crash mid-match — so ask stdout
# for UTF-8 wherever the runtime supports it.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def main():

    # ==========================
    # Goalkeeper
    # ==========================
    lloris = Goalkeeper(
        person_id=2,
        first_name="Hugo",
        last_name="Lloris",
        age=38,
        nationality="France",
        height=188,
        weight=82,
        jersey_number=1,
        preferred_foot="Left",
        overall_rating=89,
        market_value=12,
        weekly_salary=180000,
    )

    # ==========================
    # Defender
    # ==========================
    saliba = Defender(
        person_id=3,
        first_name="William",
        last_name="Saliba",
        age=24,
        nationality="France",
        height=192,
        weight=83,
        jersey_number=17,
        preferred_foot="Right",
        overall_rating=89,
        market_value=90,
        weekly_salary=250000,
    )

    # ==========================
    # Midfielder
    # ==========================
    camavinga = Midfielder(
        person_id=4,
        first_name="Eduardo",
        last_name="Camavinga",
        age=22,
        nationality="France",
        height=182,
        weight=68,
        jersey_number=8,
        preferred_foot="Left",
        overall_rating=87,
        market_value=95,
        weekly_salary=220000,
    )

    # ==========================
    # Forward
    # ==========================
    mbappe = Forward(
        person_id=5,
        first_name="Kylian",
        last_name="Mbappe",
        age=27,
        nationality="France",
        height=178,
        weight=75,
        jersey_number=10,
        preferred_foot="Right",
        overall_rating=92,
        market_value=180,
        weekly_salary=500000,
    )

    # ==========================
    # Team
    # ==========================
    france = Team(
        team_name="France National Team",
        country="France",
        fifa_ranking=2,
        formation="4-3-3",
    )

    # Register the squad and appoint the leadership.
    for player in (lloris, saliba, camavinga, mbappe):
        france.add_player(player)
    france.set_captain(mbappe)
    france.set_vice_captain(lloris)

    # ==========================
    # Match Simulation
    # ==========================

    print("\n===== MATCH START =====\n")

    mbappe.play_match()
    mbappe.shoot()
    mbappe.finish()
    mbappe.celebrate_goal()

    camavinga.play_match()
    camavinga.key_pass()
    camavinga.create_chance()
    camavinga.give_assist()

    saliba.play_match()
    saliba.tackle()
    saliba.intercept()
    saliba.clear_ball()
    saliba.block_shot()

    lloris.play_match()
    lloris.save_shot()
    lloris.save_penalty()
    lloris.keep_clean_sheet()

    # ==========================
    # Show Reports
    # ==========================

    print("\n========== TEAM ==========\n")
    france.show_team_info()

    print("\n========== SQUAD ==========\n")
    france.show_squad()


    print("\n========== FORWARD ==========\n")
    mbappe.show_forward_statistics()

    print("\n========== MIDFIELDER ==========\n")
    camavinga.show_midfielder_statistics()

    print("\n========== DEFENDER ==========\n")
    saliba.show_defender_statistics()

    print("\n========== GOALKEEPER ==========\n")
    lloris.show_goalkeeper_statistics()


if __name__ == "__main__":
    main()