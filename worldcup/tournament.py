"""The tournament façade: state plus JSON persistence.

This is what the CLI talks to. In Phase 1 it holds the 48 real teams, the data
provenance, and (once drawn) the twelve groups. Later phases add fixtures,
results and the knockout bracket to the same object and the same JSON file.

Saving is atomic — write a temp file, then rename over the target — so an
interrupted save can never corrupt an existing tournament file.
"""

from __future__ import annotations

import json
import os
import tempfile

from . import __version__
from .data import load_dataset
from .draw import GROUP_LABELS, draw_groups
from .elo import simulate_scoreline
from .knockout import (
    KnockoutMatch,
    build_round_of_32,
    simulate_knockout,
)
from .standings import (
    Match,
    TeamRecord,
    build_table,
    order_group,
    rank_third_placed,
)
from .team import Team

# Number of best third-placed teams that also advance to the Round of 32.
BEST_THIRDS = 8


def round_robin(codes: list[str]) -> list[tuple[str, str]]:
    """Every pairing in a group, in a fixed order (4 teams → 6 matches)."""
    return [
        (codes[i], codes[j])
        for i in range(len(codes))
        for j in range(i + 1, len(codes))
    ]


class Tournament:
    def __init__(
        self,
        teams: list[Team] | None = None,
        provenance: dict | None = None,
    ) -> None:
        if teams is None:
            teams, provenance = load_dataset()
        self.teams = teams
        self.provenance = provenance or {}
        self.groups: dict[str, list[Team]] = {}
        # Group-stage results and the finishing order they produce.
        self.results: list[Match] = []
        self.group_order: dict[str, list[str]] = {}
        self.best_thirds: list[str] = []
        # Knockout bracket and its outcome.
        self.knockout: list[KnockoutMatch] = []
        self.champion: str | None = None
        self.runner_up: str | None = None
        self.third_place: str | None = None
        self.fourth_place: str | None = None

    # ---- lookups --------------------------------------------------------

    def team(self, code: str) -> Team:
        for t in self.teams:
            if t.code == code:
                return t
        raise KeyError(f"no team with code {code!r}")

    # ---- draw -----------------------------------------------------------

    def run_draw(self, rng, real_hosts: bool = False) -> dict[str, list[Team]]:
        self.groups = draw_groups(self.teams, rng, real_hosts=real_hosts)
        # A fresh draw invalidates any previous group-stage or knockout results.
        self.results = []
        self.group_order = {}
        self.best_thirds = []
        self._clear_knockout()
        return self.groups

    # ---- group stage ----------------------------------------------------

    def simulate_group_stage(self, rng) -> dict[str, list[str]]:
        """Play every group match (seeded), then rank each group and the thirds.

        The scorelines are a PREDICTION sampled from the Elo model, not real
        results. Reproducible for a given RNG seed.
        """
        if not self.groups:
            raise ValueError("draw the groups first")
        self.results = []
        for label, members in self.groups.items():
            codes = [t.code for t in members]
            for a, b in round_robin(codes):
                goals_a, goals_b = simulate_scoreline(
                    self.team(a).elo, self.team(b).elo, rng
                )
                self.results.append(Match(a, b, goals_a, goals_b, group=label))
        self._rank_groups(rng)
        self._clear_knockout()  # a new group stage invalidates the old bracket
        return self.group_order

    def _rank_groups(self, rng) -> None:
        """Order every group and pick the eight best third-placed teams."""
        self.group_order = {}
        thirds: list[tuple[str, TeamRecord]] = []
        for label, members in self.groups.items():
            codes = [t.code for t in members]
            matches = [m for m in self.results if m.group == label]
            ordered = order_group(codes, matches, rng)
            self.group_order[label] = [rec.code for rec in ordered]
            thirds.append((label, ordered[2]))
        ranked = rank_third_placed(thirds, rng)
        self.best_thirds = [rec.code for _label, rec in ranked[:BEST_THIRDS]]

    # ---- reading the group stage ---------------------------------------

    def is_group_stage_done(self) -> bool:
        return bool(self.group_order)

    def group_table(self, label: str) -> list[TeamRecord]:
        """The group's table in finishing order (records built from results)."""
        codes = [t.code for t in self.groups[label]]
        matches = [m for m in self.results if m.group == label]
        table = build_table(codes, matches)
        return [table[code] for code in self.group_order[label]]

    def winners(self) -> list[str]:
        return [self.group_order[label][0] for label in self.group_order]

    def runners_up(self) -> list[str]:
        return [self.group_order[label][1] for label in self.group_order]

    def qualifiers(self) -> list[str]:
        """The 32 teams into the Round of 32: winners + runners-up + best thirds."""
        return self.winners() + self.runners_up() + list(self.best_thirds)

    # ---- knockout stage -------------------------------------------------

    def _clear_knockout(self) -> None:
        self.knockout = []
        self.champion = None
        self.runner_up = None
        self.third_place = None
        self.fourth_place = None

    def _thirds_by_group(self) -> dict[str, str]:
        """{group_label: third-placed code} for the eight groups whose thirds advanced."""
        qualifying = set(self.best_thirds)
        return {
            label: order[2]
            for label, order in self.group_order.items()
            if order[2] in qualifying
        }

    def round_of_32(self) -> list[tuple[str, str]]:
        """The 16 Round-of-32 pairings (team codes) from the group-stage result."""
        winners = {label: order[0] for label, order in self.group_order.items()}
        runners = {label: order[1] for label, order in self.group_order.items()}
        return build_round_of_32(winners, runners, self._thirds_by_group())

    def simulate_knockout(self, rng) -> str:
        """Play the bracket to a champion (seeded). Returns the champion's code.

        Every result is a PREDICTION sampled from the Elo model.
        """
        if not self.is_group_stage_done():
            raise ValueError("simulate the group stage first")
        elo_of = lambda code: self.team(code).elo  # noqa: E731 - tiny local lookup
        result = simulate_knockout(self.round_of_32(), elo_of, rng)
        self.knockout = result.matches
        self.champion = result.champion
        self.runner_up = result.runner_up
        self.third_place = result.third
        self.fourth_place = result.fourth
        return self.champion

    def is_knockout_done(self) -> bool:
        return self.champion is not None

    def knockout_rounds(self) -> dict[str, list[KnockoutMatch]]:
        """Knockout matches grouped by round, in bracket order."""
        rounds: dict[str, list[KnockoutMatch]] = {}
        for match in self.knockout:
            rounds.setdefault(match.round, []).append(match)
        return rounds

    # ---- Monte Carlo prediction ----------------------------------------

    # The round-reached keys tallied for each team, in bracket order.
    PREDICTION_KEYS = ("group", "r16", "qf", "sf", "final", "champion")

    def predict(self, sims: int, rng) -> dict[str, dict[str, float]]:
        """Run ``sims`` full tournaments over the fixed groups and return, per
        team, the fraction of runs in which it won its group and reached each
        knockout round / won the cup. Every number is a PREDICTION.

        The draw is held fixed so "win group" is meaningful; only the matches
        are re-sampled each run. Reproducible for a given RNG seed.
        """
        if not self.groups:
            raise ValueError("draw the groups first")
        if sims < 1:
            raise ValueError("sims must be at least 1")

        counts = {t.code: dict.fromkeys(self.PREDICTION_KEYS, 0) for t in self.teams}
        _round_key = {
            "Round of 16": "r16",
            "Quarter-final": "qf",
            "Semi-final": "sf",
            "Final": "final",
        }
        for _ in range(sims):
            sim = Tournament(self.teams, self.provenance)
            sim.groups = self.groups
            sim.simulate_group_stage(rng)
            sim.simulate_knockout(rng)
            for order in sim.group_order.values():
                counts[order[0]]["group"] += 1  # group winner
            for round_name, matches in sim.knockout_rounds().items():
                key = _round_key.get(round_name)
                if key is None:
                    continue  # Round of 32 == qualifiers; third-place adds no round
                for match in matches:  # participants reached this round
                    counts[match.a][key] += 1
                    counts[match.b][key] += 1
            counts[sim.champion]["champion"] += 1

        return {
            code: {key: value / sims for key, value in tally.items()}
            for code, tally in counts.items()
        }

    # ---- persistence ----------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "version": __version__,
            "kind": "prediction",
            "provenance": self.provenance,
            "teams": [t.to_dict() for t in self.teams],
            "groups": {
                label: [t.code for t in members]
                for label, members in self.groups.items()
            },
            "results": [m.to_dict() for m in self.results],
            "group_order": self.group_order,
            "best_thirds": list(self.best_thirds),
            "knockout": [m.to_dict() for m in self.knockout],
            "podium": {
                "champion": self.champion,
                "runner_up": self.runner_up,
                "third_place": self.third_place,
                "fourth_place": self.fourth_place,
            },
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Tournament":
        teams = [Team.from_dict(row) for row in data["teams"]]
        tournament = cls(teams=teams, provenance=data.get("provenance", {}))
        by_code = {t.code: t for t in teams}
        groups_data = data.get("groups", {})
        tournament.groups = {
            label: [by_code[code] for code in groups_data[label]]
            for label in GROUP_LABELS
            if label in groups_data
        }
        tournament.results = [Match.from_dict(row) for row in data.get("results", [])]
        tournament.group_order = {
            label: list(order) for label, order in data.get("group_order", {}).items()
        }
        tournament.best_thirds = list(data.get("best_thirds", []))
        tournament.knockout = [
            KnockoutMatch.from_dict(row) for row in data.get("knockout", [])
        ]
        podium = data.get("podium", {})
        tournament.champion = podium.get("champion")
        tournament.runner_up = podium.get("runner_up")
        tournament.third_place = podium.get("third_place")
        tournament.fourth_place = podium.get("fourth_place")
        return tournament

    def save(self, path: str) -> None:
        directory = os.path.dirname(os.path.abspath(path))
        os.makedirs(directory, exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(dir=directory, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(self.to_dict(), handle, indent=2)
            os.replace(tmp_path, path)  # atomic on a single filesystem
        except BaseException:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            raise

    @classmethod
    def load(cls, path: str) -> "Tournament":
        with open(path, encoding="utf-8") as handle:
            return cls.from_dict(json.load(handle))
