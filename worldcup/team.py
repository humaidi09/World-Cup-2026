"""The tournament team value object.

Deliberately separate from ``core.Team`` (the OOP demo): that class prints
inside its methods and never maintains goal difference, which conflicts with
this engine's rule that the core does no I/O. A ``Team`` here is a small,
immutable record of a real national side — identity plus the single strength
number (Elo) the simulation reads.
"""

from __future__ import annotations

from dataclasses import dataclass

# The six confederations, with the exact member counts of the real 48-team field.
CONFEDERATIONS = {"UEFA", "CAF", "AFC", "CONMEBOL", "CONCACAF", "OFC"}


@dataclass(frozen=True)
class Team:
    code: str
    name: str
    confederation: str
    pot: int
    host: bool
    elo: float

    def __post_init__(self) -> None:
        if self.confederation not in CONFEDERATIONS:
            raise ValueError(
                f"unknown confederation {self.confederation!r} for {self.code}"
            )
        if self.pot not in (1, 2, 3, 4):
            raise ValueError(f"pot must be 1-4, got {self.pot!r} for {self.code}")

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "name": self.name,
            "confederation": self.confederation,
            "pot": self.pot,
            "host": self.host,
            "elo": self.elo,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Team":
        return cls(
            code=data["code"],
            name=data["name"],
            confederation=data["confederation"],
            pot=int(data["pot"]),
            host=bool(data.get("host", False)),
            elo=float(data["elo"]),
        )

    def __str__(self) -> str:
        return self.name
