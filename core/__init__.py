"""Core domain model for the FIFA World Cup 2026 Management System.

The package models a small football domain through a clear inheritance chain:

    Person                      name, age, nationality, physique
      └── Player                jersey, rating, career stats, match actions
            ├── Goalkeeper      saves, penalty saves, clean sheets
            ├── Defender        tackles, interceptions, clearances, blocks
            ├── Midfielder      key passes, through balls, chances created
            └── Forward         shots, headers, volleys, finishes

A Team owns a squad of Players and tracks its competition record. Every
subclass overrides ``play_match`` to add its position-specific line, which is
the polymorphism the demo in ``main.py`` shows off.
"""

from core.defender import Defender
from core.forward import Forward
from core.goalkeeper import Goalkeeper
from core.midfielder import Midfielder
from core.person import Person
from core.player import Player
from core.team import Team

__all__ = [
    "Person",
    "Player",
    "Goalkeeper",
    "Defender",
    "Midfielder",
    "Forward",
    "Team",
]
