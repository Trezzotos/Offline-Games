"""Test del motore logico del Sudoku."""

import numpy as np
import pytest

from sudoku_game.engine import Board, SudokuEngine


@pytest.fixture(name="engine")
def fixture_engine() -> SudokuEngine:
    """Motore Sudoku."""
    return SudokuEngine()


def empty_board() -> Board:
    """Griglia vuota."""
    return np.zeros((9, 9), dtype="int8")


def test_find_empty(engine: SudokuEngine) -> None:
    """Trova la prima cella vuota in ordine di riga e None se piena."""
    board = empty_board()
    assert engine.find_empty(board) == (0, 0)
    board[0, 0] = 5
    assert engine.find_empty(board) == (0, 1)
    board[:] = 1
    assert engine.find_empty(board) is None


def test_is_valid_rules(engine: SudokuEngine) -> None:
    """Riga, colonna e box vengono controllati."""
    board = empty_board()
    board[0, 0] = 5
    assert engine.is_valid(board, 0, 1, 5) is False
    assert engine.is_valid(board, 1, 0, 5) is False
    assert engine.is_valid(board, 1, 1, 5) is False
    assert engine.is_valid(board, 0, 1, 1) is True
    assert engine.is_valid(board, 4, 4, 5) is True


def test_solve_produces_valid_grid(engine: SudokuEngine) -> None:
    """La griglia risolta ha 1..9 in ogni riga e colonna."""
    board = empty_board()
    assert engine.solve(board) is True
    expected = set(range(1, 10))
    for i in range(9):
        assert set(board[i, :]) == expected
        assert set(board[:, i]) == expected


def test_solve_fails_on_unsolvable_board(engine: SudokuEngine) -> None:
    """Una griglia senza soluzione restituisce False."""
    board = empty_board()
    board[0, :8] = range(1, 9)
    board[1, 8] = 9
    assert engine.solve(board) is False


@pytest.mark.parametrize(
    ("difficulty", "removed"),
    [("EASY", 30), ("MEDIUM", 45), ("HARD", 60), ("???", 45)],
)
def test_generate_puzzle_removes_cells(
    engine: SudokuEngine, difficulty: str, removed: int
) -> None:
    """Il numero di celle rimosse dipende dalla difficoltà."""
    solution, puzzle = engine.generate_puzzle(difficulty)
    assert int((puzzle == 0).sum()) == removed
    assert np.all(solution[puzzle != 0] == puzzle[puzzle != 0])
