"""
player.py

Player class of the FIFA World Cup 2026 Management System.

Author : Hussain
"""

from core.person import Person


class Player(Person):
    """
    Represents a football player.

    Inherits all common information from Person.
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
        position: str,
        preferred_foot: str,
        overall_rating: int,
        market_value: float,
        weekly_salary: float,
    ):

        # Initialize Person class
        super().__init__(
            person_id,
            first_name,
            last_name,
            age,
            nationality,
            height,
            weight,
        )

        # Player Information
        self.jersey_number = jersey_number
        self.position = position
        self.preferred_foot = preferred_foot
        self.overall_rating = overall_rating
        self.market_value = market_value
        self.weekly_salary = weekly_salary

        # Career Statistics
        self.matches_played = 0
        self.goals = 0
        self.assists = 0
        self.yellow_cards = 0
        self.red_cards = 0
        self.minutes_played = 0

    # -------------------------
    # Match Methods
    # -------------------------

    def play_match(self, minutes=90):
        self.matches_played += 1
        self.minutes_played += minutes

        print(f"{self.full_name} played {minutes} minutes.")

    def score_goal(self):

        self.goals += 1

        print(f"⚽ {self.full_name} scored!")

    def give_assist(self):

        self.assists += 1

        print(f"🎯 {self.full_name} made an assist!")

    def receive_yellow_card(self):

        self.yellow_cards += 1

        print(f"🟨 {self.full_name} received a yellow card.")

    def receive_red_card(self):

        self.red_cards += 1

        print(f"🟥 {self.full_name} received a red card.")

    # -------------------------
    # Display Methods
    # -------------------------

    def show_statistics(self):

        print("\n========== PLAYER STATISTICS ==========")

        print(f"Player : {self.full_name}")

        print(f"Matches : {self.matches_played}")

        print(f"Minutes : {self.minutes_played}")

        print(f"Goals   : {self.goals}")

        print(f"Assists : {self.assists}")

        print(f"Yellow  : {self.yellow_cards}")

        print(f"Red     : {self.red_cards}")

        print("=" * 40)

    def show_player_profile(self):

        self.show_info()

        print("PLAYER PROFILE")
        print("-" * 40)

        print(f"Jersey Number : {self.jersey_number}")

        print(f"Position      : {self.position}")

        print(f"PreferredFoot : {self.preferred_foot}")

        print(f"Overall Rating: {self.overall_rating}")

        print(f"Market Value  : €{self.market_value} Million")

        print(f"Weekly Salary : €{self.weekly_salary}")

        print("=" * 40)