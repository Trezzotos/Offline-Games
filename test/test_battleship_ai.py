"""Test della strategia di tiro hunt & target."""

import random

from battleship_game.ai import HuntTargetStrategy
from battleship_game.config import FLEET_SIZES
from battleship_game.model import Board, Orientation, ShotResult


def make_board_with_ship(
    coords_start: tuple[int, int], orientation: Orientation, ship: int
) -> Board:
    """Plancia con una nave posizionata."""
    board = Board(FLEET_SIZES)
    board.place_ship(ship, *coords_start, orientation)
    return board


def shoot(
    strategy: HuntTargetStrategy, board: Board, coord: tuple[int, int]
) -> ShotResult:
    """Spara e comunica l'esito alla strategia."""
    result = board.receive_shot(*coord)
    strategy.record_result(result)
    return result


def test_hunt_uses_parity_cells() -> None:
    """Senza bersaglio la strategia spara su celle a scacchiera."""
    strategy = HuntTargetStrategy(random.Random(3))
    board = Board(FLEET_SIZES)
    for _ in range(20):
        row, col = strategy.choose_shot(board)  # type: ignore[misc]
        assert (row + col) % 2 == 0
        board.receive_shot(row, col)


def test_hunt_falls_back_when_parity_exhausted() -> None:
    """Esaurite le celle di parità si usano le altre."""
    strategy = HuntTargetStrategy(random.Random(3))
    board = Board(FLEET_SIZES)
    for r in range(10):
        for c in range(10):
            if (r + c) % 2 == 0:
                board.receive_shot(r, c)
    row, col = strategy.choose_shot(board)  # type: ignore[misc]
    assert (row + col) % 2 == 1


def test_no_shot_when_board_is_exhausted() -> None:
    """Senza celle libere non c'è alcun colpo."""
    strategy = HuntTargetStrategy(random.Random(0))
    board = Board(FLEET_SIZES)
    for r in range(10):
        for c in range(10):
            board.receive_shot(r, c)
    assert strategy.choose_shot(board) is None


def test_miss_does_not_create_target() -> None:
    """Un colpo a vuoto non cambia il bersaglio."""
    strategy = HuntTargetStrategy(random.Random(0))
    board = Board(FLEET_SIZES)
    shoot(strategy, board, (5, 5))
    assert strategy.target_ship_id is None


def test_horizontal_targeting_until_sunk() -> None:
    """Dopo due colpi in riga la strategia segue l'asse orizzontale e poi si resetta."""
    strategy = HuntTargetStrategy(random.Random(0))
    board = make_board_with_ship((0, 0), Orientation.HORIZONTAL, 2)
    shoot(strategy, board, (0, 0))
    assert strategy.target_ship_id == 2 and strategy.orientation is None
    shoot(strategy, board, (0, 1))
    assert strategy.orientation is Orientation.HORIZONTAL
    assert strategy.choose_shot(board) == (0, 2)
    result = shoot(strategy, board, (0, 2))
    assert result.sunk
    assert strategy.target_ship_id is None
    assert not strategy.hits and strategy.orientation is None


def test_vertical_targeting() -> None:
    """Due colpi in colonna fanno inseguire in verticale."""
    strategy = HuntTargetStrategy(random.Random(0))
    board = make_board_with_ship((2, 3), Orientation.VERTICAL, 3)
    shoot(strategy, board, (3, 3))
    shoot(strategy, board, (4, 3))
    assert strategy.orientation is Orientation.VERTICAL
    assert strategy.choose_shot(board) in {(2, 3), (5, 3)}


def test_single_hit_tries_neighbours() -> None:
    """Con un solo colpo a segno si provano le celle adiacenti."""
    strategy = HuntTargetStrategy(random.Random(0))
    board = make_board_with_ship((5, 5), Orientation.HORIZONTAL, 3)
    shoot(strategy, board, (5, 6))
    assert strategy.choose_shot(board) in {(4, 6), (6, 6), (5, 5), (5, 7)}


def test_switching_to_other_ship_replaces_target() -> None:
    """Colpire un'altra nave sposta il bersaglio."""
    strategy = HuntTargetStrategy(random.Random(0))
    board = make_board_with_ship((0, 0), Orientation.HORIZONTAL, 0)
    board.place_ship(1, 5, 0, Orientation.HORIZONTAL)
    shoot(strategy, board, (0, 0))
    shoot(strategy, board, (5, 0))
    assert strategy.target_ship_id == 1
    assert strategy.hits == [(5, 0)]


def test_exhausted_candidates_reset_target() -> None:
    """Se i vicini sono già colpiti si torna alla caccia."""
    strategy = HuntTargetStrategy(random.Random(0))
    board = make_board_with_ship((0, 0), Orientation.VERTICAL, 4)
    shoot(strategy, board, (0, 0))
    board.receive_shot(0, 1)
    board.receive_shot(1, 0)
    shot = strategy.choose_shot(board)
    assert shot is not None
    assert strategy.target_ship_id is None


def test_sunk_target_is_dropped_before_choosing() -> None:
    """Un bersaglio già affondato viene dimenticato."""
    strategy = HuntTargetStrategy(random.Random(0))
    board = Board(FLEET_SIZES)
    board.ships[1].remaining_cells = 0
    strategy.target_ship_id = 1
    strategy.hits = [(5, 5)]
    strategy.choose_shot(board)
    assert strategy.target_ship_id is None


def test_duplicate_hits_are_ignored() -> None:
    """Lo stesso colpo registrato due volte conta una volta."""
    strategy = HuntTargetStrategy(random.Random(0))
    result = ShotResult((0, 0), hit=True, ship_id=1)
    strategy.record_result(result)
    strategy.record_result(result)
    assert strategy.hits == [(0, 0)]
