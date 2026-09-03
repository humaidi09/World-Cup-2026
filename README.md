# FIFA World Cup 2026 Management System

[![CI](https://github.com/humaidi09/World-Cup-2026/actions/workflows/ci.yml/badge.svg)](https://github.com/humaidi09/World-Cup-2026/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-25%20passing-brightgreen.svg)](tests/)

An object-oriented model of a football squad, built to demonstrate the four
pillars of OOP in plain Python: **encapsulation, inheritance, polymorphism and
abstraction**. Each player position is its own class, sharing a common core and
overriding only what makes it different — so a `Goalkeeper` and a `Forward` are
driven through the same interface but behave like themselves.

No dependencies. Run one file and watch a simulated match print every squad and
per-position report.

## The class hierarchy

The whole design is one inheritance chain plus a `Team` that owns a squad:

```
Person                         id, name, age, nationality, height, weight
  └── Player                   jersey, rating, value, salary + career stats
        ├── Goalkeeper         saves, penalty saves, clean sheets
        ├── Defender           tackles, interceptions, clearances, blocks
        ├── Midfielder         key passes, through balls, chances created
        └── Forward            shots, headers, volleys, finishes

Team  ──owns──▶  [ Player, Player, ... ]
```

- **`Person`** ([core/person.py](core/person.py)) holds what every human in the
  system shares, and exposes `full_name` as a computed property rather than a
  stored field.
- **`Player`** ([core/player.py](core/player.py)) extends `Person` with football
  identity and a career ledger — matches, minutes, goals, assists and cards —
  that its match methods keep up to date.
- **Each position** extends `Player`, fixes its own `position` label, and adds
  the statistics that only make sense for that role.
- **`Team`** ([core/team.py](core/team.py)) manages the squad, the captaincy and
  the competition record (points from wins and draws).

## Polymorphism: one call, four behaviours

Every position overrides `play_match()` to add its own line, but each override
still calls up into `Player` with `super()`, so the shared bookkeeping (matches
and minutes) happens exactly once regardless of position:

```python
def play_match(self, minutes=90):
    super().play_match(minutes)                 # counts the match once
    print(f"🧤 {self.full_name} played as Goalkeeper.")
```

The demo loops over a mixed list of players and calls the same method on each —
the object decides how to respond. That is the point the project is built to
make.

## Run it

Requires Python 3.10 or newer. No installation or third-party packages.

```bash
git clone https://github.com/humaidi09/World-Cup-2026.git
cd World-Cup-2026
python main.py
```

`main.py` builds France's spine — Lloris, Saliba, Camavinga and Mbappé —
registers them in a `Team`, plays a short match and prints the reports:

```
========== TEAM ==========

==================================================
TEAM INFORMATION
==================================================
Team Name      : France National Team
Country        : France
FIFA Ranking   : 2
Formation      : 4-3-3
Captain        : Kylian Mbappe
Vice Captain   : Hugo Lloris
Total Players  : 4
```

> The reports use emoji, so `main.py` switches stdout to UTF-8 on start-up —
> which keeps it from crashing on a Windows console (whose default cp1252 code
> page cannot encode them).

## Project layout

```
core/
  person.py       base class: identity and physique
  player.py       a football player + career statistics
  goalkeeper.py   \
  defender.py      >  one class per position, each extending Player
  midfielder.py   /
  forward.py      /
  team.py         a squad, its leadership and its competition record
main.py           a runnable match-day demonstration
tests/            25 tests covering inheritance, stats and the demo
```

## Tests

```bash
pip install pytest
pytest
```

```
25 passed
```

The suite checks that each position really is a `Player`, that the specialised
statistics count correctly, that every overridden `play_match` still records the
match through `super()`, that a `Team` manages its squad and record, and that
the `main.py` demo runs end to end.

## License

[MIT](LICENSE) © 2026 Hussain Ahmed Humaidi
