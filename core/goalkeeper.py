"""
goalkeeper.py

Goalkeeper Class

Project : FIFA World Cup 2026 Management System
"""

from core.player import Player


class Goalkeeper(Player):
    """
    Goalkeeper class inherits from Player.
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
            "Goalkeeper",
            preferred_foot,
            overall_rating,
            market_value,
            weekly_salary,
        )

        # Goalkeeper Statistics
        self.clean_sheets = 0
        self.saves = 0
        self.penalty_saves = 0

    # -------------------------
    # Goalkeeper Methods
    # -------------------------

    def save_shot(self):
        self.saves += 1
        print(f"🧤 {self.full_name} made a fantastic save!")

    def save_penalty(self):
        self.penalty_saves += 1
        print(f"❌ {self.full_name} saved a penalty!")

    def keep_clean_sheet(self):
        self.clean_sheets += 1
        print(f"✅ {self.full_name} kept a clean sheet!")

    # -------------------------
    # Method Overriding
    # -------------------------

    def play_match(self, minutes=90):
        super().play_match(minutes)
        print(f"🧤 {self.full_name} played as Goalkeeper.")

    # -------------------------
    # Display
    # -------------------------

    def show_goalkeeper_statistics(self):

        self.show_statistics()

        print("\nGOALKEEPER STATISTICS")
        print("-" * 40)

        print(f"Saves          : {self.saves}")
        print(f"Penalty Saves  : {self.penalty_saves}")
        print(f"Clean Sheets   : {self.clean_sheets}")

        print("=" * 40)