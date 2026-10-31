"""Catalogo dei giochi disponibili nel menu."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GameEntry:
    """Voce del catalogo: etichetta mostrata e script da avviare."""

    label: str
    script: str


DEFAULT_CATALOG: tuple[GameEntry, ...] = (
    GameEntry("SUDOKU", "sudoku.py"),
    GameEntry("BATTLESHIP", "battleship.py"),
)
