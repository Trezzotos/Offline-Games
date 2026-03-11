# pylint: disable=line-too-long, missing-final-newline
"""Unit test per il modulo Sudoku."""

# pylint: disable=no-member,protected-access,redefined-outer-name,import-error

import os

import numpy as np
import pygame
import pytest

from sudoku import SudokuEngine, SudokuGame

# Forza Pygame a non aprire finestre reali durante i test
os.environ["SDL_VIDEODRIVER"] = "dummy"


# =========================
# FIXTURES
# =========================

@pytest.fixture
def game():
    """Inizializza l'istanza principale del gioco."""
    pygame.init()
    return SudokuGame()


@pytest.fixture
def engine():
    """Restituisce il motore logico Sudoku."""
    return SudokuEngine()


# =========================
# TEST LOGICA (ENGINE)
# =========================

def test_engine_logic(engine):
    """Test delle funzioni principali del motore Sudoku."""
    board = np.zeros((9, 9), dtype="int8")

    assert engine.find_empty(board) == (0, 0)

    board[0, 0] = 5
    assert engine.is_valid(board, 0, 1, 5) is False
    assert engine.is_valid(board, 1, 0, 5) is False
    assert engine.is_valid(board, 1, 1, 5) is False
    assert engine.is_valid(board, 0, 1, 1) is True

    assert engine.solve(board) is True

    sol, puzzle = engine.generate_puzzle("FACILE")
    assert sol.shape == (9, 9)
    assert 0 in puzzle


# =========================
# TEST STATO GIOCO
# =========================

def test_game_setup(game):
    """Test inizializzazione stato gioco."""
    game.setup_game("MEDIO")

    assert game.state.difficulty_label == "MEDIO"
    assert game.state.lives == 3
    assert game.state_mode == "PLAYING"
    assert game.state.grid.shape == (9, 9)


def test_move_selection(game):
    """Test movimento selezione griglia."""
    game.setup_game("FACILE")
    game.state.selected = [4, 4]

    game._move_selection(pygame.K_UP)
    assert game.state.selected == [3, 4]

    game._move_selection(pygame.K_LEFT)
    assert game.state.selected == [3, 3]

    game.state.selected = [0, 0]
    game._move_selection(pygame.K_UP)

    assert game.state.selected == [8, 0]


def test_input_number_and_notes(game):
    """Test inserimento numeri e modalità note."""
    game.setup_game("FACILE")

    st = game.state
    st.is_fixed[0, 0] = False
    st.selected = [0, 0]

    correct_val = st.solution[0, 0]
    wrong_val = 1 if correct_val != 1 else 2

    game._input_number(wrong_val)

    assert st.lives == 2

    st.note_mode = True
    game._input_number(5)

    assert 5 in st.notes[0][0]

    game._input_number(5)

    assert 5 not in st.notes[0][0]


def test_handle_events(game):
    """Test gestione eventi di gioco."""
    game.setup_game("FACILE")

    event_a = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a)
    game._handle_play_events(event_a)

    assert game.state.note_mode is True

    game.state.is_fixed[0, 0] = False
    game.state.selected = [0, 0]
    game.state.grid[0, 0] = 5

    event_back = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_BACKSPACE)
    game._handle_play_events(event_back)

    assert game.state.grid[0, 0] == 0


def test_global_keys_menu(game):
    """Test navigazione menu."""
    game.state_mode = "MENU"
    game.menu_sel = 1

    event_down = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
    game._handle_global_keys(event_down)

    assert game.menu_sel == 2

    event_enter = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
    game._handle_global_keys(event_enter)

    assert game.state_mode == "PLAYING"


def test_renderer_calls(game):
    """Esegue i metodi di rendering per coverage."""
    game.setup_game("FACILE")

    game.renderer.draw_menu(game.menu_options, game.menu_sel)
    game.renderer.draw_game(game.state)