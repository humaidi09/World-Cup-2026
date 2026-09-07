# FIFA World Cup 2026 — Simulation & Prediction Engine

[![CI](https://github.com/humaidi09/World-Cup-2026/actions/workflows/ci.yml/badge.svg)](https://github.com/humaidi09/World-Cup-2026/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-102%20passing-brightgreen.svg)](tests/)

An offline engine that simulates the **real** 48-team FIFA World Cup 2026 and
predicts it. It uses only real data — the 48 qualified national teams and a
dated snapshot of published World Football Elo ratings — to run a fair,
rule-correct group draw, play the whole tournament (group stage → knockout →
champion), and run Monte Carlo to report each team's chances round by round.

> **Everything the engine outputs is a PREDICTION, not a claim of fact.** No real
> results are asserted. Every run is reproducible under `--seed`, and there are
> **no third-party dependencies** — the whole engine is the Python standard library.

*(This repository also contains a separate, self-contained OOP teaching demo —
see [The OOP demo](#the-oop-demo-coremainpy) near the end.)*

## Quick start

Requires Python 3.10 or newer. No installation needed.

```bash
git clone https://github.com/humaidi09/World-Cup-2026.git
cd World-Cup-2026
python -m worldcup run --seed 1 --real-hosts
```

That draws the groups, plays the group stage, resolves the knockout bracket and
prints a champion. To see the odds instead of a single outcome:

```bash
python -m worldcup predict --sims 1000 --seed 7
```

A full narrated walk-through — with real seeded output — is in
[`examples/session.md`](examples/session.md), alongside a saved tournament in
[`examples/tournament_seed1.json`](examples/tournament_seed1.json).

## Commands

All commands share `--db <file>` (default `tournament.json` in the current
directory) and persist state between calls, so you can `draw`, then `simulate`,
then `knockout` step by step — or `run` them all at once.

| Command | What it does |
|---|---|
| `teams` | List the 48 real teams with pot, confederation and Elo (+ data provenance) |
| `draw [--seed N] [--real-hosts]` | Draw the 12 groups (fair, rule-correct; `--real-hosts` fixes MEX→A, CAN→B, USA→D) |
| `groups` | Show the current groups — the draw, or the standings once simulated |
| `simulate [--seed N]` | Play the group stage, rank every group, pick the 8 best third-placed teams |
| `knockout [--seed N]` | Play the bracket to a champion (+ third-place play-off) |
| `run [--seed N] [--real-hosts]` | Draw + group stage + knockout, end to end, under one seed |
| `predict --sims N [--seed N]` | Monte Carlo: per-team P(win group / reach R16 / QF / SF / Final / win cup) |

## How it works

**The prediction model.** Each match is sampled from the two teams' Elo gap. The
Elo win expectancy `E_A = 1 / (1 + 10^((R_B − R_A) / 400))` is mapped to expected
goals, and independent Poisson goal counts are drawn with a seeded RNG — giving
wins, draws and the goal difference / goals-for the tiebreakers need. A drawn
knockout tie is settled by an Elo-weighted coin flip (the model's stand-in for
extra time and penalties). See [`worldcup/elo.py`](worldcup/elo.py).

**The draw** ([`worldcup/draw.py`](worldcup/draw.py)) is pot-based with
backtracking so every group ends valid: one team per pot, and no group has two
teams from the same confederation **except UEFA** (up to two, since 16 UEFA teams
span 12 groups). Hosts can be pre-placed with `--real-hosts`.

**Group standings** ([`worldcup/standings.py`](worldcup/standings.py)) apply the
official FIFA order: points → goal difference → goals for → head-to-head among the
level teams → drawing of lots (a seeded stand-in for the real draw).

**The knockout bracket** ([`worldcup/knockout.py`](worldcup/knockout.py)) is the
real published 2026 skeleton — the fixed Round-of-32 schedule (Matches 73–88) and
how every later round connects.

### Honest modelling notes

Where real published structure exists, this engine uses it. Two places are
deliberate, documented simplifications rather than official procedure:

- **Best-thirds allocation.** FIFA publishes a 495-row table mapping every
  combination of qualifying third-placed groups to bracket slots. That table is
  impractical to bundle, so the eight thirds are assigned by a deterministic
  solver that honours the **real** per-slot eligibility — correct constraints, a
  simplified choice among valid fills.
- **Fair-play tiebreaker & venues.** Bookings aren't modelled, so FIFA's
  fair-play criterion is omitted (inventing card counts would break the real-data
  rule); group matches are treated as neutral-venue for the same reason.

## Data & provenance

[`data/teams_2026.json`](data/teams_2026.json) carries the 48 real teams — the 42
direct qualifiers plus the six March 2026 play-off winners (Bosnia, Sweden,
Turkey, Czech Republic, DR Congo, Iraq) — with a **dated Elo snapshot** citing its
source (`eloratings.net`, as of 2026-07-19). The file records this provenance
inline. Ratings are a fixed snapshot for reproducibility, not live values;
[`tools/update_elo.py`](tools/update_elo.py) is an optional maintainer script to
refresh them (dry-run by default).

## Project layout

```
worldcup/            the prediction engine (packaged, python -m worldcup)
  team.py            team value object: real side + Elo (no I/O)
  data.py            load & validate the bundled real dataset
  elo.py             Elo -> scoreline prediction model
  draw.py            pot-based, rule-correct group draw
  standings.py       group tables, official tiebreakers, best-thirds ranking
  knockout.py        the real published bracket, played to a champion
  tournament.py      façade: state + Monte Carlo + atomic JSON persistence
  cli.py             argparse subcommands + rendering (all printing lives here)
data/teams_2026.json 48 real teams + real Elo snapshot (with provenance)
tools/update_elo.py  optional snapshot refresher (dev tool; not used at runtime)
examples/            a seeded tournament JSON + a narrated transcript
core/ + main.py      the separate OOP teaching demo (below)
tests/               102 tests, one file per module
```

## Tests

```bash
pip install pytest
pytest
```

```
102 passed
```

The suite covers the dataset (48 real teams, 12 per pot, exact confederation
counts), the Elo model, the draw's constraints over many seeds, the official
tiebreakers, the bracket's structure and reproducibility, JSON round-trips, and
that Monte Carlo probabilities are coherent (champion odds sum to 100%, and
reaching rounds is monotonic).

---

## The OOP demo (`core/` + `main.py`)

The repository began as — and still contains — a small, self-contained
object-oriented model of a football squad, built to demonstrate the four pillars
of OOP in plain Python: **encapsulation, inheritance, polymorphism and
abstraction**. It is independent of the engine above and runs on its own:

```bash
python main.py
```

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

- **`Person`** ([core/person.py](core/person.py)) holds what every human shares,
  exposing `full_name` as a computed property.
- **`Player`** ([core/player.py](core/player.py)) extends `Person` with football
  identity and a career ledger its match methods keep up to date.
- **Each position** extends `Player`, fixes its own `position`, and adds the
  statistics that only make sense for that role.
- **`Team`** ([core/team.py](core/team.py)) manages the squad, captaincy and
  competition record.

Polymorphism is the point: every position overrides `play_match()` to add its own
line, but each override calls up into `Player` with `super()`, so the shared
bookkeeping happens exactly once regardless of position. `main.py` builds France's
spine — Lloris, Saliba, Camavinga and Mbappé — plays a short match and prints the
per-position reports. (It switches stdout to UTF-8 on start-up so its emoji don't
crash a Windows cp1252 console.)

## License

[MIT](LICENSE) © 2026 Hussain Ahmed Humaidi
