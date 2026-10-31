"""Strategie di piazzamento della flotta."""

import random
from typing import Protocol

from battleship_game.config import MAX_PLACEMENT_ATTEMPTS
from battleship_game.model import Board, Orientation


class FleetPlacer(Protocol):
    """Interfaccia per un algoritmo di piazzamento della flotta."""

    def place_fleet(self, board: Board) -> None:
        """Posiziona tutte le navi sulla plancia."""


class RandomFleetPlacer:
    """Piazza la flotta in posizioni casuali valide."""

    def __init__(self, rng: random.Random | None = None) -> None:
        self._rng = rng or random.Random()

    def place_fleet(self, board: Board) -> None:
        """Piazza ogni nave in modo casuale, senza sovrapposizioni."""
        for ship in board.ships:
            self._place_ship(board, ship.ship_id, ship.dimension)

    def _place_ship(self, board: Board, ship_id: int, length: int) -> None:
        for _ in range(MAX_PLACEMENT_ATTEMPTS):
            orientation = self._rng.choice(list(Orientation))
            row = self._rng.randint(0, board.rows - 1)
            col = self._rng.randint(0, board.columns - 1)
            if board.place_ship(ship_id, row, col, orientation):
                return
        raise RuntimeError(
            f"Impossibile piazzare la nave {ship_id} (lunghezza {length})"
        )
