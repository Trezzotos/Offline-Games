"""Intelligenza artificiale dell'avversario (strategia hunt & target)."""

import random
from typing import Protocol

from battleship_game.config import Coord
from battleship_game.model import Board, Orientation, ShotResult


class ShootingStrategy(Protocol):
    """Interfaccia di una strategia di tiro."""

    def choose_shot(self, board: Board) -> Coord | None:
        """Sceglie la prossima cella da colpire (None se non ce ne sono)."""

    def record_result(self, result: ShotResult) -> None:
        """Aggiorna la strategia con l'esito dell'ultimo colpo."""

    def reset(self) -> None:
        """Riporta la strategia allo stato iniziale."""


class HuntTargetStrategy:
    """Spara a scacchiera (hunt) e, dopo un colpo a segno, insegue la nave (target)."""

    def __init__(self, rng: random.Random | None = None) -> None:
        self._rng = rng or random.Random()
        self.target_ship_id: int | None = None
        self.hits: list[Coord] = []
        self.orientation: Orientation | None = None

    def reset(self) -> None:
        """Dimentica il bersaglio corrente."""
        self.target_ship_id = None
        self.hits = []
        self.orientation = None

    def choose_shot(self, board: Board) -> Coord | None:
        """Sceglie il prossimo colpo, preferendo il bersaglio in corso."""
        self._drop_sunk_target(board)
        shot = self._choose_target_shot(board)
        if shot is not None:
            return shot
        return self._choose_hunt_shot(board)

    def record_result(self, result: ShotResult) -> None:
        """Aggiorna bersaglio e orientamento in base all'esito del colpo."""
        if not result.hit or result.ship_id is None:
            return
        if self.target_ship_id != result.ship_id:
            self.target_ship_id = result.ship_id
            self.hits = [result.coord]
            self.orientation = None
        elif result.coord not in self.hits:
            self.hits.append(result.coord)
        self._infer_orientation()
        if result.sunk:
            self.reset()

    def _drop_sunk_target(self, board: Board) -> None:
        if self.target_ship_id is None:
            return
        if 0 <= self.target_ship_id < len(board.ships):
            if board.ships[self.target_ship_id].is_sunk():
                self.reset()

    def _infer_orientation(self) -> None:
        if len(self.hits) < 2:
            return
        first_row, first_col = self.hits[0]
        if all(row == first_row for row, _ in self.hits):
            self.orientation = Orientation.HORIZONTAL
        elif all(col == first_col for _, col in self.hits):
            self.orientation = Orientation.VERTICAL

    def _target_candidates(self) -> list[Coord]:
        self.hits = list(dict.fromkeys(self.hits))
        self._infer_orientation()
        if self.orientation is Orientation.HORIZONTAL:
            row = self.hits[0][0]
            cols = sorted(col for _, col in self.hits)
            return [(row, cols[0] - 1), (row, cols[-1] + 1)]
        if self.orientation is Orientation.VERTICAL:
            col = self.hits[0][1]
            rows = sorted(row for row, _ in self.hits)
            return [(rows[0] - 1, col), (rows[-1] + 1, col)]
        row, col = self.hits[0]
        neighbours = [(row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)]
        self._rng.shuffle(neighbours)
        return neighbours

    def _choose_target_shot(self, board: Board) -> Coord | None:
        if self.target_ship_id is None or not self.hits:
            return None
        for row, col in self._target_candidates():
            if board.in_bounds(row, col) and not board.cell(row, col).is_hit:
                return (row, col)
        self.reset()
        return None

    def _choose_hunt_shot(self, board: Board) -> Coord | None:
        available = board.available_targets()
        if not available:
            return None
        parity = [(r, c) for r, c in available if (r + c) % 2 == 0]
        return self._rng.choice(parity or available)
