"""Test del modello di dominio di Battleship."""

import pytest

from battleship_game.config import FLEET_SIZES
from battleship_game.model import Board, Cell, Orientation, Ship


@pytest.fixture(name="board")
def fixture_board() -> Board:
    """Plancia con la flotta standard."""
    return Board(FLEET_SIZES)


def test_orientation_toggle_and_cells() -> None:
    """L'orientamento si inverte e genera le celle corrette."""
    assert Orientation.HORIZONTAL.toggled() is Orientation.VERTICAL
    assert Orientation.VERTICAL.toggled() is Orientation.HORIZONTAL
    assert Orientation.HORIZONTAL.cells(1, 2, 3) == [(1, 2), (1, 3), (1, 4)]
    assert Orientation.VERTICAL.cells(1, 2, 3) == [(1, 2), (2, 2), (3, 2)]


def test_cell_properties() -> None:
    """Le proprietà della cella riflettono nave e colpo."""
    cell = Cell()
    assert not cell.has_ship and not cell.is_ship_hit
    cell.ship_id = 0
    cell.is_hit = True
    assert cell.has_ship and cell.is_ship_hit


@pytest.mark.parametrize(
    ("size", "name"),
    [
        (2, "Destroyer"),
        (3, "Cruiser"),
        (4, "Submarine"),
        (5, "Carrier"),
        (7, "invalid_name"),
    ],
)
def test_ship_names(size: int, name: str) -> None:
    """Ogni dimensione ha il nome atteso."""
    assert Ship(0, size).name == name


def test_ship_sinks_after_all_hits() -> None:
    """Una nave affonda quando perde tutte le celle."""
    ship = Ship(0, 2)
    ship.register_hit()
    assert not ship.is_sunk()
    ship.register_hit()
    assert ship.is_sunk()


def test_board_fleet_and_lives(board: Board) -> None:
    """La flotta ha id progressivi e 16 celle totali."""
    assert [s.ship_id for s in board.ships] == [0, 1, 2, 3, 4]
    assert board.remaining_ship_cells == 16


def test_can_place_rules(board: Board) -> None:
    """Controlla confini e sovrapposizioni."""
    assert board.can_place(0, 0, 2, Orientation.HORIZONTAL)
    assert board.can_place(0, 0, 2, Orientation.VERTICAL)
    assert not board.can_place(-1, 0, 2, Orientation.HORIZONTAL)
    assert not board.can_place(9, 9, 3, Orientation.HORIZONTAL)
    assert not board.can_place(9, 9, 3, Orientation.VERTICAL)
    board.place_ship(0, 0, 0, Orientation.HORIZONTAL)
    assert not board.can_place(0, 1, 2, Orientation.VERTICAL)


def test_place_ship_marks_cells(board: Board) -> None:
    """Il piazzamento valido marca le celle, quello invalido no."""
    assert board.place_ship(2, 4, 4, Orientation.VERTICAL)
    assert [board.cell(r, 4).ship_id for r in (4, 5, 6)] == [2, 2, 2]
    assert not board.place_ship(3, 9, 9, Orientation.HORIZONTAL)
    assert not board.cell(9, 9).has_ship


def test_receive_shot_miss_hit_and_sunk(board: Board) -> None:
    """Gestisce acqua, colpo e affondamento."""
    board.place_ship(0, 0, 0, Orientation.HORIZONTAL)
    miss = board.receive_shot(5, 5)
    assert not miss.hit and board.cell(5, 5).is_hit
    first = board.receive_shot(0, 0)
    assert first.hit and not first.sunk and first.ship_id == 0
    second = board.receive_shot(0, 1)
    assert second.sunk
    assert board.remaining_ship_cells == 14


def test_available_targets_and_all_sunk(board: Board) -> None:
    """Le celle colpite escono dai bersagli; all_sunk richiede ogni nave affondata."""
    assert len(board.available_targets()) == 100
    board.receive_shot(0, 0)
    assert (0, 0) not in board.available_targets()
    assert not board.all_sunk()
    for ship in board.ships:
        ship.remaining_cells = 0
    assert board.all_sunk()
