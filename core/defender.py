"""
defender.py

Defender Class

Project : FIFA World Cup 2026 Management System
"""

from core.player import Player


class Defender(Player):
    """
    Defender class inherits from Player.
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
            "Defender",
            preferred_foot,
            overall_rating,
            market_value,
            weekly_salary,
        )

        # Defender Statistics
        self.tackles = 0
        self.interceptions = 0
        self.clearances = 0
        self.blocks = 0

    # -------------------------
    # Defender Methods
    # -------------------------

    def tackle(self):
        self.tackles += 1
        print(f"🛡 {self.full_name} made a perfect tackle!")

    def intercept(self):
        self.interceptions += 1
        print(f"⚽ {self.full_name} intercepted the ball!")

    def clear_ball(self):
        self.clearances += 1
        print(f"🚀 {self.full_name} cleared the ball!")

    def block_shot(self):
        self.blocks += 1
        print(f"🧱 {self.full_name} blocked a dangerous shot!")

    # -------------------------
    # Method Overriding
    # -------------------------

    def play_match(self, minutes=90):
        super().play_match(minutes)
        print(f"🛡 {self.full_name} played as Defender.")

    # -------------------------
    # Display
    # -------------------------

    def show_defender_statistics(self):

        self.show_statistics()

        print("\nDEFENDER STATISTICS")
        print("-" * 40)

        print(f"Tackles      : {self.tackles}")
        print(f"Interceptions: {self.interceptions}")
        print(f"Clearances   : {self.clearances}")
        print(f"Blocks       : {self.blocks}")

        print("=" * 40)