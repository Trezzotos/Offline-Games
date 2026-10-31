"""Test del piazzamento casuale della flotta."""

import random

import pytest

from battleship_game import placement
from battleship_game.config import FLEET_SIZES
from battleship_game.model import Board
from battleship_game.placement import RandomFleetPlacer


def test_random_placer_places_whole_fleet() -> None:
    """Tutte le 16 celle di nave vengono piazzate senza sovrapposizioni."""
    board = Board(FLEET_SIZES)
    RandomFleetPlacer(random.Random(1)).place_fleet(board)
    occupied = sum(cell.has_ship for row in board.grid for cell in row)
    assert occupied == 16


def test_random_placer_is_deterministic_with_seed() -> None:
    """Lo stesso seed produce la stessa disposizione."""
    first, second = Board(FLEET_SIZES), Board(FLEET_SIZES)
    RandomFleetPlacer(random.Random(7)).place_fleet(first)
    RandomFleetPlacer(random.Random(7)).place_fleet(second)
    assert [[c.ship_id for c in r] for r in first.grid] == [
        [c.ship_id for c in r] for r in second.grid
    ]


def test_random_placer_raises_when_impossible(monkeypatch: pytest.MonkeyPatch) -> None:
    """Se non c'è posto la nave non viene ignorata in silenzio."""
    monkeypatch.setattr(placement, "MAX_PLACEMENT_ATTEMPTS", 3)
    board = Board((5,), rows=1, columns=1)
    with pytest.raises(RuntimeError):
        RandomFleetPlacer(random.Random(0)).place_fleet(board)
