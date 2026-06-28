"""
forward.py

Forward Class

Project : FIFA World Cup 2026 Management System
"""

from core.player import Player


class Forward(Player):
    """
    Forward class inherits from Player.
    """

    def __init__(
        self,
        person_id: int,
        first_name: str,
        last_name: str,
        age: int,
        nationality: str,
        height: float,
        weight: float,
        jersey_number: int,
        preferred_foot: str,
        overall_rating: int,
        market_value: float,
        weekly_salary: float,
    ):

        super().__init__(
            person_id,
            first_name,
            last_name,
            age,
            nationality,
            height,
            weight,
            jersey_number,
            "Forward",
            preferred_foot,
            overall_rating,
            market_value,
            weekly_salary,
        )

        # Forward Statistics
        self.shots = 0
        self.shots_on_target = 0
        self.header_goals = 0
        self.volley_goals = 0

    # -------------------------
    # Forward Methods
    # -------------------------

    def shoot(self):
        self.shots += 1
        print(f"🚀 {self.full_name} takes a powerful shot!")

    def shot_on_target(self):
        self.shots += 1
        self.shots_on_target += 1
        print(f"🎯 {self.full_name}'s shot is on target!")

    def finish(self):
        self.goals += 1
        print(f"⚽ {self.full_name} finishes brilliantly!")

    def header_goal(self):
        self.goals += 1
        self.header_goals += 1
        print(f"🤕 {self.full_name} scores with a header!")

    def volley_goal(self):
        self.goals += 1
        self.volley_goals += 1
        print(f"🔥 {self.full_name} scores an amazing volley!")

    def celebrate_goal(self):
        print(f"🎉 {self.full_name} celebrates with the fans!")

    # -------------------------
    # Method Overriding
    # -------------------------

    def play_match(self, minutes=90):
        super().play_match(minutes)
        print(f"⚽ {self.full_name} played as Forward.")

    # -------------------------
    # Display
    # -------------------------

    def show_forward_statistics(self):

        self.show_statistics()

        print("\nFORWARD STATISTICS")
        print("-" * 40)

        print(f"Shots            : {self.shots}")
        print(f"Shots On Target  : {self.shots_on_target}")
        print(f"Header Goals     : {self.header_goals}")
        print(f"Volley Goals     : {self.volley_goals}")

        print("=" * 40)