"""
midfielder.py

Midfielder Class

Project : FIFA World Cup 2026 Management System
"""

from core.player import Player


class Midfielder(Player):
    """
    Midfielder class inherits from Player.
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
            "Midfielder",
            preferred_foot,
            overall_rating,
            market_value,
            weekly_salary,
        )

        # Midfielder Statistics
        self.key_passes = 0
        self.long_passes = 0
        self.through_balls = 0
        self.chances_created = 0

    # -------------------------
    # Midfielder Methods
    # -------------------------

    def key_pass(self):
        self.key_passes += 1
        print(f"🎯 {self.full_name} delivered a key pass!")

    def long_pass(self):
        self.long_passes += 1
        print(f"🚀 {self.full_name} made a long pass!")

    def through_ball(self):
        self.through_balls += 1
        print(f"⚽ {self.full_name} played a perfect through ball!")

    def create_chance(self):
        self.chances_created += 1
        print(f"✨ {self.full_name} created a goal-scoring chance!")

    # -------------------------
    # Method Overriding
    # -------------------------

    def play_match(self, minutes=90):
        super().play_match(minutes)
        print(f"🎮 {self.full_name} controlled the midfield.")

    # -------------------------
    # Display
    # -------------------------

    def show_midfielder_statistics(self):

        self.show_statistics()

        print("\nMIDFIELDER STATISTICS")
        print("-" * 40)

        print(f"Key Passes      : {self.key_passes}")
        print(f"Long Passes     : {self.long_passes}")
        print(f"Through Balls   : {self.through_balls}")
        print(f"Chances Created : {self.chances_created}")

        print("=" * 40)