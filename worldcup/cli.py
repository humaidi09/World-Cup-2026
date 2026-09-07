"""Command-line interface for the World Cup 2026 engine.

Subcommands each load the tournament file, do one thing, save if they changed
anything, and return an exit code (0 ok, 1 refused, 2 usage) — so the tool is
scriptable and the tests can drive it without any interactive prompt. All
printing lives here; the rest of the package is silent and testable.

Every simulated result is labelled a PREDICTION, never presented as fact.
"""

from __future__ import annotations

import argparse
import random
import sys

from .tournament import Tournament

DEFAULT_DB = "tournament.json"

# Reports use a few non-ASCII characters; keep them from crashing or mojibaking
# a Windows console whose default cp1252 code page cannot encode them.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


# ---- loading / saving ---------------------------------------------------


def _load(path: str) -> Tournament:
    """Load a tournament from ``path``, or start a fresh one (real teams) if missing."""
    try:
        return Tournament.load(path)
    except FileNotFoundError:
        return Tournament()


def _rng(args: argparse.Namespace) -> random.Random:
    """A seeded RNG when --seed is given, else an unseeded one."""
    return random.Random(args.seed)


# ---- rendering ----------------------------------------------------------


def _print_teams(tournament: Tournament) -> None:
    prov = tournament.provenance
    print("\n  48 real teams — Elo snapshot"
          + (f" (source: {prov.get('elo_source')}, as of {prov.get('elo_as_of')})"
             if prov.get("elo_source") else ""))
    print("  " + "-" * 58)
    print(f"  {'Code':<5}{'Team':<26}{'Conf':<11}{'Pot':<4}{'Elo':>6}")
    print("  " + "-" * 58)
    for team in sorted(tournament.teams, key=lambda t: (-t.elo, t.name)):
        host = " *" if team.host else ""
        print(f"  {team.code:<5}{team.name:<26}{team.confederation:<11}"
              f"{team.pot:<4}{team.elo:>6.0f}{host}")
    print("  " + "-" * 58)
    print("  * = host nation\n")


def _print_groups(tournament: Tournament) -> None:
    if not tournament.groups:
        print("  No draw yet. Run 'draw' first.")
        return
    print("\n  GROUP DRAW")
    for label, members in tournament.groups.items():
        print(f"\n  Group {label}")
        for team in members:
            print(f"    {team.code:<5}{team.name:<26}{team.confederation:<11}"
                  f"Pot {team.pot}  Elo {team.elo:>4.0f}")


def _print_standings(tournament: Tournament) -> None:
    print("\n  GROUP STAGE — PREDICTED standings")
    print("  (simulated from Elo ratings; not real results)")
    qualifying_thirds = set(tournament.best_thirds)
    header = (f"    {'#':<2}{'Team':<24}{'P':>2}{'W':>3}{'D':>3}{'L':>3}"
              f"{'GF':>4}{'GA':>4}{'GD':>5}{'Pts':>5}")
    for label in tournament.group_order:
        print(f"\n  Group {label}")
        print(header)
        for pos, rec in enumerate(tournament.group_table(label), start=1):
            name = tournament.team(rec.code).name
            if pos <= 2:
                mark = "  Q"
            elif pos == 3 and rec.code in qualifying_thirds:
                mark = "  q"
            else:
                mark = ""
            print(f"    {pos:<2}{name:<24}{rec.played:>2}{rec.won:>3}{rec.drawn:>3}"
                  f"{rec.lost:>3}{rec.goals_for:>4}{rec.goals_against:>4}"
                  f"{rec.goal_difference:>+5}{rec.points:>5}{mark}")

    print("\n  QUALIFIED FOR THE ROUND OF 32 (PREDICTION)")
    print("  " + "-" * 58)
    _print_code_line("Group winners ", tournament.winners(), tournament)
    _print_code_line("Runners-up    ", tournament.runners_up(), tournament)
    _print_code_line("Best thirds   ", tournament.best_thirds, tournament)
    total = len(tournament.qualifiers())
    print(f"  {total} teams qualify.  Q = winner/runner-up, q = best third-placed.\n")


def _print_code_line(label: str, codes: list[str], tournament: Tournament) -> None:
    names = ", ".join(tournament.team(code).name for code in codes)
    print(f"  {label}({len(codes)}): {names}")


def _print_knockout(tournament: Tournament) -> None:
    print("\n  KNOCKOUT STAGE — PREDICTED bracket")
    print("  (simulated from Elo ratings; not real results)")
    for round_name, matches in tournament.knockout_rounds().items():
        print(f"\n  {round_name}")
        for m in matches:
            a = tournament.team(m.a).name
            b = tournament.team(m.b).name
            note = " (a.e.t./pens)" if m.decided_on == "penalties" else ""
            winner = tournament.team(m.winner).name
            print(f"    {a:>24} {m.goals_a}-{m.goals_b} {b:<24}{note}  ->  {winner}")

    if tournament.champion is not None:
        print("\n  FINAL RESULT (PREDICTION)")
        print("  " + "-" * 40)
        print(f"    Champion       {tournament.team(tournament.champion).name}")
        print(f"    Runner-up      {tournament.team(tournament.runner_up).name}")
        print(f"    Third place    {tournament.team(tournament.third_place).name}")
        print(f"    Fourth place   {tournament.team(tournament.fourth_place).name}")
        print()


# ---- subcommand handlers ------------------------------------------------


def _cmd_teams(tournament: Tournament, args: argparse.Namespace) -> int:
    _print_teams(tournament)
    return 0


def _cmd_draw(tournament: Tournament, args: argparse.Namespace) -> int:
    tournament.run_draw(_rng(args), real_hosts=args.real_hosts)
    tournament.save(args.db)
    kind = "real host placement" if args.real_hosts else "fully random"
    seed = f", seed={args.seed}" if args.seed is not None else ""
    print(f"  Drew 12 groups ({kind}{seed}).")
    _print_groups(tournament)
    return 0


def _cmd_groups(tournament: Tournament, args: argparse.Namespace) -> int:
    if tournament.is_group_stage_done():
        _print_standings(tournament)
    else:
        _print_groups(tournament)
    return 0


def _cmd_simulate(tournament: Tournament, args: argparse.Namespace) -> int:
    if not tournament.groups:
        print("  error: no draw yet — run 'draw' first", file=sys.stderr)
        return 1
    tournament.simulate_group_stage(_rng(args))
    tournament.save(args.db)
    seed = f" (seed={args.seed})" if args.seed is not None else ""
    print(f"  Simulated the group stage{seed}. PREDICTION — not real results.")
    _print_standings(tournament)
    return 0


def _cmd_knockout(tournament: Tournament, args: argparse.Namespace) -> int:
    if not tournament.is_group_stage_done():
        print("  error: no group stage yet — run 'simulate' first", file=sys.stderr)
        return 1
    tournament.simulate_knockout(_rng(args))
    tournament.save(args.db)
    seed = f" (seed={args.seed})" if args.seed is not None else ""
    print(f"  Simulated the knockout stage{seed}. PREDICTION — not real results.")
    _print_knockout(tournament)
    return 0


def _cmd_run(tournament: Tournament, args: argparse.Namespace) -> int:
    """Draw, group stage and knockout end-to-end under one seed."""
    rng = _rng(args)
    tournament.run_draw(rng, real_hosts=args.real_hosts)
    tournament.simulate_group_stage(rng)
    tournament.simulate_knockout(rng)
    tournament.save(args.db)
    seed = f" (seed={args.seed})" if args.seed is not None else ""
    hosts = "real host placement" if args.real_hosts else "fully random draw"
    print(f"  Ran the whole tournament{seed} — {hosts}. PREDICTION — not real results.")
    _print_standings(tournament)
    _print_knockout(tournament)
    return 0


def _print_predictions(
    tournament: Tournament, probs: dict, sims: int
) -> None:
    print(f"\n  MONTE CARLO PREDICTION — {sims} simulated tournaments")
    print("  (probabilities from the Elo model over a fixed draw; not real odds)")
    print("  " + "-" * 70)
    print(f"    {'Team':<24}{'WinGrp':>8}{'R16':>8}{'QF':>8}{'SF':>8}"
          f"{'Final':>8}{'Champion':>10}")
    print("  " + "-" * 70)
    ranked = sorted(
        tournament.teams,
        key=lambda t: (probs[t.code]["champion"], probs[t.code]["final"]),
        reverse=True,
    )

    def pct(value: float) -> str:
        return f"{value * 100:.1f}"

    for team in ranked:
        p = probs[team.code]
        print(f"    {team.name:<24}{pct(p['group']):>8}{pct(p['r16']):>8}"
              f"{pct(p['qf']):>8}{pct(p['sf']):>8}{pct(p['final']):>8}"
              f"{pct(p['champion']):>10}")
    print("  " + "-" * 70)
    print("  Percentages. WinGrp = wins its group; the rest = reaches that "
          "round or wins the cup.\n")


def _cmd_predict(tournament: Tournament, args: argparse.Namespace) -> int:
    if not tournament.groups:
        # Hold a fixed real-host draw so "win group" is meaningful across runs.
        tournament.run_draw(_rng(args), real_hosts=True)
        tournament.save(args.db)
        print("  No draw found — made a fixed real-host draw for this prediction.")
    probs = tournament.predict(args.sims, _rng(args))
    seed = f", seed={args.seed}" if args.seed is not None else ""
    print(f"  Predicting from {args.sims} simulations{seed}.")
    _print_predictions(tournament, probs, args.sims)
    return 0


# ---- argument parsing ---------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="worldcup",
        description="Real FIFA World Cup 2026 simulation & prediction engine. "
                    "All simulated results are predictions, not facts.",
    )
    parser.add_argument(
        "--db", default=DEFAULT_DB, help=f"tournament data file (default: {DEFAULT_DB})"
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("teams", help="list the 48 real teams with Elo ratings")

    p = sub.add_parser("draw", help="draw the 12 groups")
    p.add_argument("--seed", type=int, default=None, help="seed for a reproducible draw")
    p.add_argument("--real-hosts", action="store_true",
                   help="pre-place Mexico/Canada/USA in groups A/B/D as in the real draw")

    sub.add_parser("groups", help="show the current groups (draw, or standings once simulated)")

    p = sub.add_parser("simulate", help="play the group stage and rank every group")
    p.add_argument("--seed", type=int, default=None, help="seed for a reproducible simulation")

    p = sub.add_parser("knockout", help="play the knockout bracket to a champion")
    p.add_argument("--seed", type=int, default=None, help="seed for a reproducible bracket")

    p = sub.add_parser("run", help="draw + group stage + knockout, end to end")
    p.add_argument("--seed", type=int, default=None, help="seed for a reproducible tournament")
    p.add_argument("--real-hosts", action="store_true",
                   help="pre-place Mexico/Canada/USA in groups A/B/D as in the real draw")

    p = sub.add_parser("predict", help="Monte Carlo: per-team round-by-round probabilities")
    p.add_argument("--sims", type=int, default=1000, help="number of simulated tournaments (default: 1000)")
    p.add_argument("--seed", type=int, default=None, help="seed for a reproducible prediction")

    return parser


_HANDLERS = {
    "teams": _cmd_teams,
    "draw": _cmd_draw,
    "groups": _cmd_groups,
    "simulate": _cmd_simulate,
    "knockout": _cmd_knockout,
    "run": _cmd_run,
    "predict": _cmd_predict,
}


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    tournament = _load(args.db)
    handler = _HANDLERS.get(args.command)
    if handler is None:  # pragma: no cover - argparse rejects unknown commands
        parser.error(f"unknown command {args.command!r}")
    return handler(tournament, args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
