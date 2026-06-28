"""
team.py

Team Class

Project : FIFA World Cup 2026 Management System
"""

from core.player import Player


class Team:

    def __init__(
        self,
        team_name: str,
        country: str,
        fifa_ranking: int,
        formation: str,
    ):

        self.team_name = team_name
        self.country = country
        self.fifa_ranking = fifa_ranking
        self.formation = formation



        self.players = []

        self.captain = None
        self.vice_captain = None

        self.points = 0
        self.matches = 0
        self.wins = 0
        self.draws = 0
        self.losses = 0

        self.goals_for = 0
        self.goals_against = 0
        self.goal_difference = 0

    # ==========================
    # Player Management
    # ==========================

    def add_player(self, player: Player):

        self.players.append(player)

        print(f"{player.full_name} added to {self.team_name}")

    def remove_player(self, jersey_number: int):

        for player in self.players:

            if player.jersey_number == jersey_number:

                self.players.remove(player)

                print(f"{player.full_name} removed from squad.")

                return

        print("Player not found.")

    # ==========================
    # Captain
    # ==========================

    def set_captain(self, player: Player):

        self.captain = player

        print(f"{player.full_name} is now Captain.")

    def set_vice_captain(self, player: Player):

        self.vice_captain = player

        print(f"{player.full_name} is now Vice Captain.")

    # ==========================
    # Statistics
    # ==========================

    def record_win(self):

        self.matches += 1
        self.wins += 1
        self.points += 3

    def record_draw(self):

        self.matches += 1
        self.draws += 1
        self.points += 1

    def record_loss(self):

        self.matches += 1
        self.losses += 1

    # ==========================
    # Display
    # ==========================

    def show_team_info(self):

        print("\n" + "=" * 50)
        print("TEAM INFORMATION")
        print("=" * 50)

        print(f"Team Name      : {self.team_name}")
        print(f"Country        : {self.country}")
        print(f"FIFA Ranking   : {self.fifa_ranking}")
        print(f"Formation      : {self.formation}")
      

        if self.captain:
            print(f"Captain        : {self.captain.full_name}")

        if self.vice_captain:
            print(f"Vice Captain   : {self.vice_captain.full_name}")

        print(f"Total Players  : {len(self.players)}")

    def show_squad(self):

        print("\n" + "=" * 50)
        print(f"{self.team_name} SQUAD")
        print("=" * 50)

        for player in self.players:

            print(
                f"{player.jersey_number:>2} | "
                f"{player.full_name:<25} | "
                f"{player.position}"
            )

    def show_statistics(self):

        print("\n" + "=" * 50)
        print("TEAM STATISTICS")
        print("=" * 50)

        print(f"Matches         : {self.matches}")
        print(f"Wins            : {self.wins}")
        print(f"Draws           : {self.draws}")
        print(f"Losses          : {self.losses}")
        print(f"Points          : {self.points}")
        print(f"Goals For       : {self.goals_for}")
        print(f"Goals Against   : {self.goals_against}")
        print(f"Goal Difference : {self.goal_difference}")