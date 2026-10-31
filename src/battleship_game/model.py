"""Modello di dominio di Battleship: celle, navi e plance (nessuna dipendenza UI)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from battleship_game.config import (
    GRID_COLUMNS,
    GRID_ROWS,
    INVALID_SHIP_NAME,
    SHIP_NAMES,
    Coord,
)


class Orientation(Enum):
    """Orientamento di una nave sulla plancia."""

    HORIZONTAL = "H"
    VERTICAL = "V"

    def toggled(self) -> "Orientation":
        """Restituisce l'orientamento opposto."""
        if self is Orientation.HORIZONTAL:
            return Orientation.VERTICAL
        return Orientation.HORIZONTAL

    def cells(self, row: int, col: int, length: int) -> list[Coord]:
        """Coordinate occupate da una nave di data lunghezza a partire da (row, col)."""
        if self is Orientation.HORIZONTAL:
            return [(row, col + offset) for offset in range(length)]
        return [(row + offset, col) for offset in range(length)]


@dataclass
class Cell:
    """Singola cella della plancia."""

    ship_id: int | None = None
    is_hit: bool = False

    @property
    def has_ship(self) -> bool:
        """True se la cella è occupata da una nave."""
        return self.ship_id is not None

    @property
    def is_ship_hit(self) -> bool:
        """True se la cella contiene una nave già colpita."""
        return self.is_hit and self.has_ship


class Ship:
    """Nave con dimensione e celle ancora integre."""

    def __init__(self, ship_id: int, dimension: int) -> None:
        self.ship_id = ship_id
        self.dimension = dimension
        self.remaining_cells = dimension
        self.placed = False
        self.name = SHIP_NAMES.get(dimension, INVALID_SHIP_NAME)

    def is_sunk(self) -> bool:
        """True quando la nave non ha più celle integre."""
        return self.remaining_cells <= 0

    def register_hit(self) -> None:
        """Registra un colpo subito dalla nave."""
        self.remaining_cells -= 1


@dataclass(frozen=True)
class ShotResult:
    """Esito di un colpo sparato su una plancia."""

    coord: Coord
    hit: bool
    ship_id: int | None = None
    sunk: bool = False


class Board:
    """Plancia di gioco con la propria flotta."""

    def __init__(
        self,
        fleet_sizes: tuple[int, ...],
        rows: int = GRID_ROWS,
        columns: int = GRID_COLUMNS,
    ) -> None:
        self.rows = rows
        self.columns = columns
        self.grid = [[Cell() for _ in range(columns)] for _ in range(rows)]
        self.ships = [Ship(idx, size) for idx, size in enumerate(fleet_sizes)]

    def in_bounds(self, row: int, col: int) -> bool:
        """True se la coordinata appartiene alla plancia."""
        return 0 <= row < self.rows and 0 <= col < self.columns

    def cell(self, row: int, col: int) -> Cell:
        """Restituisce la cella alla coordinata indicata."""
        return self.grid[row][col]

    def can_place(
        self, row: int, col: int, length: int, orientation: Orientation
    ) -> bool:
        """Verifica che una nave stia nella plancia senza sovrapporsi ad altre."""
        cells = orientation.cells(row, col, length)
        return all(
            self.in_bounds(r, c) and not self.grid[r][c].has_ship for r, c in cells
        )

    def place_ship(
        self, ship_id: int, row: int, col: int, orientation: Orientation
    ) -> bool:
        """Posiziona la nave indicata; restituisce False se la posizione non è valida."""
        ship = self.ships[ship_id]
        if not self.can_place(row, col, ship.dimension, orientation):
            return False
        for r, c in orientation.cells(row, col, ship.dimension):
            self.grid[r][c].ship_id = ship_id
        ship.placed = True
        return True

    def receive_shot(self, row: int, col: int) -> ShotResult:
        """Applica un colpo alla plancia e ne restituisce l'esito."""
        cell = self.grid[row][col]
        cell.is_hit = True
        if cell.ship_id is None:
            return ShotResult((row, col), hit=False)
        ship = self.ships[cell.ship_id]
        ship.register_hit()
        return ShotResult(
            (row, col), hit=True, ship_id=ship.ship_id, sunk=ship.is_sunk()
        )

    def available_targets(self) -> list[Coord]:
        """Celle non ancora colpite."""
        return [
            (r, c)
            for r in range(self.rows)
            for c in range(self.columns)
            if not self.grid[r][c].is_hit
        ]

    @property
    def remaining_ship_cells(self) -> int:
        """Numero totale di celle di nave ancora integre."""
        return sum(ship.remaining_cells for ship in self.ships)

    @property
    def placed_count(self) -> int:
        """Numero di navi già posizionate."""
        return sum(ship.placed for ship in self.ships)

    def all_sunk(self) -> bool:
        """True quando l'intera flotta è affondata."""
        return all(ship.is_sunk() for ship in self.ships)
