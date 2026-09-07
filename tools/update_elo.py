"""Optional developer tool: refresh the bundled Elo snapshot.

The engine itself never runs this — it ships a dated, source-cited snapshot in
``data/teams_2026.json`` so simulations are reproducible and fully offline. This
script is only for a maintainer who wants to pull newer published ratings.

It fetches the World Football Elo table from eloratings.net (stdlib ``urllib``
only), matches each bundled team by name, and updates just the ``elo`` field —
never the team list, pots or confederations. Names that do not match are
reported and left untouched, so nothing is ever silently invented. It prints a
dry run by default; pass ``--write`` to save (atomically) and it also refreshes
the provenance date.

    python tools/update_elo.py            # dry run: show what would change
    python tools/update_elo.py --write    # apply and update the snapshot date

Matching is best-effort: eloratings' spellings differ from several of ours
(e.g. "USA", "Czechia", "Korea South"), so expect a few unmatched teams to
update by hand. This is a convenience, not part of the engine's guarantees.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import sys
import tempfile
import urllib.request

WORLD_TSV_URL = "https://www.eloratings.net/World.tsv"
_DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "teams_2026.json"
)
_RATING = re.compile(r"\b(1[0-9]{3}|2[0-4][0-9]{2})\b")  # a plausible Elo, 1000-2499


def fetch_ratings(url: str = WORLD_TSV_URL) -> dict[str, int]:
    """Return ``{lowercased country name: rating}`` parsed from the Elo TSV."""
    with urllib.request.urlopen(url, timeout=30) as response:  # noqa: S310 - fixed https URL
        text = response.read().decode("utf-8", errors="replace")

    ratings: dict[str, int] = {}
    for line in text.splitlines():
        cells = [c.strip() for c in line.split("\t") if c.strip()]
        if not cells:
            continue
        name = next((c for c in cells if not _RATING.fullmatch(c) and any(ch.isalpha() for ch in c)), None)
        rating = next((int(m.group()) for c in cells if (m := _RATING.fullmatch(c))), None)
        if name and rating is not None:
            ratings.setdefault(name.lower(), rating)
    return ratings


def apply_updates(dataset: dict, ratings: dict[str, int]) -> tuple[list[tuple], list[str]]:
    """Update elo in-place where a name matches. Return (changes, unmatched)."""
    changes: list[tuple] = []
    unmatched: list[str] = []
    for team in dataset["teams"]:
        new = ratings.get(team["name"].lower())
        if new is None:
            unmatched.append(team["name"])
        elif new != team["elo"]:
            changes.append((team["name"], team["elo"], new))
            team["elo"] = new
    return changes, unmatched


def _save(path: str, dataset: dict) -> None:
    directory = os.path.dirname(os.path.abspath(path))
    fd, tmp = tempfile.mkstemp(dir=directory, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(dataset, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Refresh the bundled Elo snapshot (dev tool).")
    parser.add_argument("--write", action="store_true", help="apply changes to data/teams_2026.json")
    parser.add_argument("--url", default=WORLD_TSV_URL, help="Elo TSV source URL")
    args = parser.parse_args(argv)

    with open(_DATA_PATH, encoding="utf-8") as handle:
        dataset = json.load(handle)

    try:
        ratings = fetch_ratings(args.url)
    except Exception as exc:  # network/parse errors — report, do not crash noisily
        print(f"  error: could not fetch ratings: {exc}", file=sys.stderr)
        return 1
    if not ratings:
        print("  error: no ratings parsed from source", file=sys.stderr)
        return 1

    changes, unmatched = apply_updates(dataset, ratings)
    for name, old, new in changes:
        print(f"  {name:<26} {old} -> {new}")
    print(f"\n  {len(changes)} rating(s) would change; {len(unmatched)} team(s) unmatched.")
    if unmatched:
        print("  Unmatched (update by hand): " + ", ".join(sorted(unmatched)))

    if args.write:
        if changes:
            dataset.setdefault("provenance", {})["elo_as_of"] = _dt.date.today().isoformat()
            _save(_DATA_PATH, dataset)
            print(f"\n  Wrote {_DATA_PATH} (provenance date updated).")
        else:
            print("\n  Nothing to write.")
    else:
        print("\n  Dry run. Re-run with --write to apply.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
