# A narrated session

Everything below is a **PREDICTION** produced by the Elo model — not a real
result. Runs are reproducible: the same `--seed` always gives the same output.
The saved state for the end-to-end run is in
[`tournament_seed1.json`](tournament_seed1.json).

## 1. The real field

```
python -m worldcup teams
```

Lists all 48 real qualified teams with their pot, confederation and the bundled
Elo snapshot (source and date shown in the header). Spain (2259) and Argentina
(2173) top the ratings; the hosts USA, Mexico and Canada are marked.

## 2. One whole tournament, end to end

```
python -m worldcup run --seed 1 --real-hosts
```

`--real-hosts` pre-places Mexico, Canada and the USA into groups A, B and D as in
the real draw; the rest is a fair, rule-correct draw. The command plays the group
stage, ranks every group with the official tiebreakers, picks the eight best
third-placed teams, then plays the whole knockout bracket. Under seed 1 it ends:

```
  FINAL RESULT (PREDICTION)
  ----------------------------------------
    Champion       Colombia
    Runner-up      Japan
    Third place    Argentina
    Fourth place   Spain
```

A single seeded run is one *possible* tournament — upsets and all. To ask how
likely each outcome is, run many.

## 3. Thousands of tournaments — the odds

```
python -m worldcup predict --sims 1000 --seed 7
```

Holds the drawn groups fixed and re-simulates 1000 tournaments, then reports how
often each team wins its group and reaches each round. The strongest sides by Elo
come out on top, as they should:

```
    Team                      WinGrp     R16      QF      SF   Final  Champion
    ----------------------------------------------------------------------
    Spain                       73.4    82.9    68.1    56.7    42.2      32.9
    Argentina                   59.8    79.6    62.8    47.6    35.0      20.4
    England                     65.6    74.6    52.6    37.0    20.7      12.4
    France                      60.3    74.5    56.3    31.8    17.8       8.8
    Portugal                    59.8    57.0    39.4    17.0     7.5       4.0
```

Champion probabilities across all 48 teams sum to 100%. Change `--seed` for a
different but equally reproducible sample; raise `--sims` to tighten the numbers.
