import os
import pytest
import numpy as np
import pygame

# Forza Pygame a non aprire finestre reali durante i test
os.environ['SDL_VIDEODRIVER'] = 'dummy'

from sudoku import SudokuEngine, GameState, SudokuGame

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
    return SudokuEngine()

# =========================
# TEST LOGICA (SUDOKU ENGINE)
# =========================

def test_engine_logic(engine):
    board = np.zeros((9, 9), dtype="int8")
    # Test find_empty
    assert engine.find_empty(board) == (0, 0)
    
    # Test is_valid
    board[0, 0] = 5
    assert engine.is_valid(board, 0, 1, 5) is False # Stessa riga
    assert engine.is_valid(board, 1, 0, 5) is False # Stessa colonna
    assert engine.is_valid(board, 1, 1, 5) is False # Stesso quadrante
    assert engine.is_valid(board, 0, 1, 1) is True  # Valido
    
    # Test solve e generate
    assert engine.solve(board) is True
    sol, puzzle = engine.generate_puzzle("FACILE")
    assert sol.shape == (9, 9)
    assert 0 in puzzle # Un puzzle deve avere celle vuote

# =========================
# TEST STATO E CONTROLLER (COVERAGE AGGIUNTIVA)
# =========================

def test_game_setup(game):
    """Copre setup_game e l'inizializzazione di GameState."""
    game.setup_game("MEDIO")
    assert game.state.difficulty_label == "MEDIO"
    assert game.state.lives == 3
    assert game.state_mode == "PLAYING"
    assert game.state.grid.shape == (9, 9)

def test_move_selection(game):
    """Copre la funzione _move_selection."""
    game.setup_game("FACILE")
    game.state.selected = [4, 4]
    
    game._move_selection(pygame.K_UP)
    assert game.state.selected == [3, 4]
    
    game._move_selection(pygame.K_LEFT)
    assert game.state.selected == [3, 3]
    
    # Test wrap-around (bordi griglia)
    game.state.selected = [0, 0]
    game._move_selection(pygame.K_UP)
    assert game.state.selected == [8, 0]

def test_input_number_and_notes(game):
    """Copre _input_number e la logica delle annotazioni (W0106 fix)."""
    game.setup_game("FACILE")
    st = game.state
    # Forza una cella non fissa per il test
    st.is_fixed[0, 0] = False
    st.selected = [0, 0]
    
    # Test inserimento numero corretto/errato
    correct_val = st.solution[0, 0]
    wrong_val = 1 if correct_val != 1 else 2
    
    # Inserimento errato -> perde vita
    game._input_number(wrong_val)
    assert st.lives == 2
    
    # Test Modalità Note (Copre le righe rimosse dal ternario)
    st.note_mode = True
    game._input_number(5)
    assert 5 in st.notes[0][0]
    game._input_number(5) # Rimuove la nota se già presente
    assert 5 not in st.notes[0][0]

def test_handle_events(game):
    """Simula la pressione dei tasti per coprire _handle_play_events."""
    game.setup_game("FACILE")
    # Simulo pressione tasto 'A' per le note
    event_a = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a)
    game._handle_play_events(event_a)
    assert game.state.note_mode is True
    
    # Simulo tasto Backspace
    game.state.is_fixed[0, 0] = False
    game.state.selected = [0, 0]
    game.state.grid[0, 0] = 5
    event_back = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_BACKSPACE)
    game._handle_play_events(event_back)
    assert game.state.grid[0, 0] == 0

def test_global_keys_menu(game):
    """Testa la navigazione nel menu."""
    game.state_mode = "MENU"
    game.menu_sel = 1
    event_down = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
    game._handle_global_keys(event_down)
    assert game.menu_sel == 2
    
    # Test invio per iniziare partita
    event_enter = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
    game._handle_global_keys(event_enter)
    assert game.state_mode == "PLAYING"

def test_renderer_calls(game):
    """Copre le funzioni di disegno (senza verificare l'output visivo)."""
    game.setup_game("FACILE")
    # Chiamare i metodi di disegno aumenta la coverage delle righe del Renderer
    game.renderer.draw_menu(game.menu_options, game.menu_sel)
    game.renderer.draw_game(game.state)
    # Non assertiamo nulla, ci serve solo che il codice venga eseguito senza errori