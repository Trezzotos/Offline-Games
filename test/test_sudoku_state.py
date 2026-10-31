"""Test dello stato di gioco del Sudoku."""

import numpy as np
import pytest

from sudoku_game.engine import SudokuEngine
from sudoku_game.state import GameState


@pytest.fixture(name="state")
def fixture_state() -> GameState:
    """Stato con una cella (0, 0) libera."""
    solution, grid = SudokuEngine().generate_puzzle("FACILE")
    grid[0, 0] = 0
    return GameState(solution, grid, "FACILE")


def wrong_value(state: GameState) -> int:
    """Un valore sbagliato per la cella (0, 0)."""
    return 1 if state.solution[0, 0] != 1 else 2


def test_initial_state(state: GameState) -> None:
    """Valori iniziali."""
    assert state.lives == 3
    assert state.selected == [4, 4]
    assert not state.finished and not state.note_mode
    assert state.difficulty_label == "FACILE"


def test_move_selection_wraps(state: GameState) -> None:
    """La selezione si avvolge ai bordi."""
    state.selected = [0, 0]
    state.move_selection(-1, 0)
    assert state.selected == [8, 0]
    state.move_selection(0, -1)
    assert state.selected == [8, 8]
    state.move_selection(1, 1)
    assert state.selected == [0, 0]


def test_wrong_number_costs_life_until_game_over(state: GameState) -> None:
    """Ogni errore toglie una vita; a zero la partita è persa."""
    state.selected = [0, 0]
    for expected in (2, 1):
        state.input_number(wrong_value(state))
        state.erase_selected()
        assert state.lives == expected and not state.game_over
    state.input_number(wrong_value(state))
    assert state.lives == 0 and state.game_over and state.finished


def test_notes_toggle_and_clear_on_input(state: GameState) -> None:
    """Le note si alternano e vengono cancellate quando si inserisce un numero."""
    state.selected = [0, 0]
    state.toggle_note_mode()
    state.input_number(5)
    assert 5 in state.notes[0][0]
    state.input_number(5)
    assert 5 not in state.notes[0][0]
    state.input_number(3)
    state.toggle_note_mode()
    state.input_number(int(state.solution[0, 0]))
    assert not state.notes[0][0]


def test_fixed_cells_and_same_value_are_ignored(state: GameState) -> None:
    """Le celle fisse e i valori identici non cambiano nulla."""
    state.selected = [0, 1]
    before = state.grid.copy()
    state.input_number(wrong_value(state))
    state.erase_selected()
    assert np.array_equal(before, state.grid) and state.lives == 3
    state.selected = [0, 0]
    state.input_number(int(state.solution[0, 0]))
    assert state.grid[0, 0] == state.solution[0, 0]
    state.input_number(int(state.solution[0, 0]))
    assert state.lives == 3


def test_winning(state: GameState) -> None:
    """Completare la griglia corretta vince la partita."""
    state.grid[:] = state.solution
    state.grid[0, 0] = 0
    state.selected = [0, 0]
    state.input_number(int(state.solution[0, 0]))
    assert state.won and state.finished


def test_erase_selected(state: GameState) -> None:
    """Cancellare svuota cella e note."""
    state.selected = [0, 0]
    state.input_number(wrong_value(state))
    state.notes[0][0].add(4)
    state.erase_selected()
    assert state.grid[0, 0] == 0 and not state.notes[0][0]
