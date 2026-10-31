"""Catalogo dei giochi disponibili nel menu."""

from dataclasses import dataclass


@dataclass(frozen=True)
class GameEntry:
    """Voce del catalogo: etichetta mostrata e script da avviare."""

    label: str
    script: str


DEFAULT_CATALOG: tuple[GameEntry, ...] = (
    GameEntry("SUDOKU", "sudoku.py"),
    GameEntry("BATTAGLIA NAVALE", "battleship.py"),
)
