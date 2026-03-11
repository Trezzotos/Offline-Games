"""Unit test per il modulo Battleship."""

# pylint: disable=no-member,protected-access,import-error
# pylint: disable=line-too-long, missing-final-newline

import importlib
import os
import sys

import pygame
import pytest

os.environ["SDL_VIDEODRIVER"] = "dummy"


def load_module(monkeypatch, event_frames=None, mouse_positions=None, tick_values=None):
    """Importa il modulo di gioco con eventi e timer controllati nei test."""
    pygame.init()
    event_frames = event_frames or [[pygame.event.Event(pygame.QUIT)]]
    mouse_positions = mouse_positions or [(0, 0)]
    tick_values = tick_values or [0] * 50

    frame_iter = iter(event_frames)
    pos_iter = iter(mouse_positions)
    tick_iter = iter(tick_values)
    last_pos = [mouse_positions[-1]]

    def fake_event_get():
        """Restituisce una sequenza controllata di eventi pygame."""
        try:
            return next(frame_iter)
        except StopIteration:
            return [pygame.event.Event(pygame.QUIT)]

    def fake_mouse_get_pos():
        """Restituisce posizioni del mouse predefinite."""
        try:
            last_pos[0] = next(pos_iter)
        except StopIteration:
            pass
        return last_pos[0]

    def fake_get_ticks():
        """Restituisce tempi predefiniti per simulare il clock di gioco."""
        try:
            return next(tick_iter)
        except StopIteration:
            return tick_values[-1] if tick_values else 0

    monkeypatch.setattr(pygame.event, "get", fake_event_get)
    monkeypatch.setattr(pygame.mouse, "get_pos", fake_mouse_get_pos)
    monkeypatch.setattr(pygame.time, "get_ticks", fake_get_ticks)

    if "battleship_fixed" in sys.modules:
        del sys.modules["battleship_fixed"]

    module = importlib.import_module("battleship_fixed")
    pygame.init()
    return module


@pytest.fixture(name="game_module")
def fixture_game_module(monkeypatch):
    """Fornisce il modulo Battleship già importato per i test."""
    return load_module(monkeypatch)


def test_module_import_and_basic_state(game_module):
    """Controlla che il modulo venga importato con lo stato iniziale atteso."""
    assert game_module.WIDTH == 800
    assert game_module.HEIGHT == 900
    assert len(game_module.player_grid) == 10
    assert len(game_module.enemy_grid) == 10
    assert len(game_module.player_ships) == 5
    assert game_module.enemy_ships_placed is True


def test_cell_and_ship_methods(game_module):
    """Verifica i metodi base delle classi Cell e Ship."""
    game_module.reset_game()

    cell = game_module.Cell(True, False, False)
    cell.set_ship_id(99)
    assert cell.contains_ship is True
    assert cell.ship_id == 99

    ship = game_module.Ship(3)
    assert ship.name == "Cruiser"
    assert ship.is_sunk() is False

    ship.set_direction(1)
    ship.set_coords(0, 0, 0)
    assert game_module.player_grid[0][0].ship_id == ship.ship_id
    assert game_module.player_grid[0][1].ship_id == ship.ship_id
    assert game_module.player_grid[0][2].ship_id == ship.ship_id

    ship.remaining_cells = 0
    assert ship.is_sunk() is True


def test_can_place_preview_and_draw(game_module):
    """Testa validazione del piazzamento, anteprima e disegno preview."""
    game_module.reset_game()

    assert game_module.can_place_ship(game_module.player_grid, 0, 0, 2, 1) is True
    game_module.player_grid[0][0].contains_ship = True
    assert game_module.can_place_ship(game_module.player_grid, 0, 0, 2, 1) is False
    assert game_module.can_place_ship(game_module.player_grid, 9, 9, 3, 1) is False
    assert game_module.can_place_ship(game_module.player_grid, 9, 9, 3, -1) is False

    game_module.reset_game()
    mouse_x = game_module.player_grid_x + 5
    mouse_y = game_module.player_grid_y + 5
    cells, valid = game_module.get_preview_cells(mouse_x, mouse_y, 2, 1)
    assert cells == [(0, 0), (0, 1)]
    assert valid is True

    outside_cells, outside_valid = game_module.get_preview_cells(0, 0, 2, 1)
    assert outside_cells == []
    assert outside_valid is False

    game_module.draw_ship_preview(game_module.display, cells, True)
    game_module.draw_ship_preview(game_module.display, cells, False)


def test_place_ship_and_enemy_ships(game_module):
    """Controlla il piazzamento del giocatore e quello casuale del nemico."""
    game_module.reset_game()

    game_module.place_ship(0, 0, 0, 1)
    assert game_module.player_grid[0][0].contains_ship is True
    assert game_module.player_grid[0][1].contains_ship is True
    assert game_module.player_ships[0].direction == 1

    game_module.reset_game()
    game_module.place_ship(0, 0, 0, -1)
    assert game_module.player_grid[0][0].contains_ship is True
    assert game_module.player_grid[1][0].contains_ship is True
    assert game_module.player_ships[0].direction == 0

    game_module.reset_game()
    game_module.place_enemy_ships()
    occupied = sum(cell.contains_ship for row in game_module.enemy_grid for cell in row)
    assert occupied == 16
    assert game_module.enemy_ships_placed is True


def test_enemy_attack_paths(game_module, monkeypatch):
    """Verifica diversi rami della logica di attacco del nemico."""
    game_module.reset_game()
    pygame.init()

    game_module.player_lives = 3
    game_module.player_grid[0][0].contains_ship = True
    game_module.player_grid[0][0].set_ship_id(0)
    game_module.player_ships[0].remaining_cells = 2

    monkeypatch.setattr(game_module.random, "choice", lambda seq: (0, 0))
    result = game_module.enemy_attack()
    assert result is True
    assert game_module.player_grid[0][0].hitted is True
    assert game_module.player_grid[0][0].sunk is True
    assert game_module.player_lives == 2
    assert game_module.enemy_attack.target_ship_id == 0
    assert (0, 0) in game_module.enemy_attack.hits

    game_module.player_grid[0][1].contains_ship = True
    game_module.player_grid[0][1].set_ship_id(0)
    result = game_module.enemy_attack()
    assert result is True
    assert game_module.player_grid[0][1].hitted is True
    assert game_module.enemy_attack.orientation == "H"

    result = game_module.enemy_attack()
    assert result is True
    assert game_module.player_grid[0][2].hitted is True

    for row_cells in game_module.player_grid:
        for cell in row_cells:
            cell.hitted = True
    game_module.PLAYER_TURN = False
    result = game_module.enemy_attack()
    assert result is True
    assert game_module.PLAYER_TURN is True


def test_reset_and_draw_helpers(game_module):
    """Controlla reset completo e funzioni di disegno di supporto."""
    game_module.player_lives = 1
    game_module.enemy_lives = 1
    game_module.PLAYER_TURN = False
    game_module.ships_placed = 4
    game_module.toggle = -1
    game_module.game_over = True
    game_module.winner_text = "TEST"
    game_module.show_instructions = True

    pygame.init()
    game_module.draw_help_button()
    game_module.draw_instructions_overlay()
    game_module.reset_game()

    assert game_module.player_lives == 16
    assert game_module.enemy_lives == 16
    assert game_module.PLAYER_TURN is True
    assert game_module.ships_placed == 0
    assert game_module.toggle == 1
    assert game_module.game_over is False
    assert game_module.winner_text == ""
    assert game_module.show_instructions is False


def test_import_flow_help_overlay(monkeypatch):
    """Simula il click sul pulsante Help durante il loop principale."""
    help_click = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN,
        button=1,
        pos=(705, 450),
    )
    module = load_module(
        monkeypatch,
        event_frames=[[help_click], [pygame.event.Event(pygame.QUIT)]],
        mouse_positions=[(705, 450), (705, 450)],
        tick_values=[0, 100, 200, 300],
    )
    assert module.show_instructions is True


def test_import_flow_placement_and_attack(monkeypatch):
    """Simula piazzamento navi e un attacco del giocatore nel loop principale."""
    player_x = 200
    player_y = 490
    enemy_x = 200
    enemy_y = 10

    frames = [
        [
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN, button=3, pos=(player_x + 5, player_y + 5)
            )
        ],
        [
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN, button=1, pos=(player_x + 5, player_y + 5)
            )
        ],
        [
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN, button=1, pos=(player_x + 85, player_y + 5)
            )
        ],
        [
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN, button=3, pos=(player_x + 5, player_y + 85)
            )
        ],
        [
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN, button=1, pos=(player_x + 5, player_y + 85)
            )
        ],
        [
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN, button=1, pos=(player_x + 5, player_y + 165)
            )
        ],
        [
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN, button=1, pos=(player_x + 5, player_y + 245)
            )
        ],
        [
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN, button=1, pos=(enemy_x + 5, enemy_y + 5)
            )
        ],
        [pygame.event.Event(pygame.QUIT)],
    ]
    positions = [
        (player_x + 5, player_y + 5),
        (player_x + 5, player_y + 5),
        (player_x + 85, player_y + 5),
        (player_x + 5, player_y + 85),
        (player_x + 5, player_y + 85),
        (player_x + 5, player_y + 165),
        (player_x + 5, player_y + 245),
        (enemy_x + 5, enemy_y + 5),
        (enemy_x + 5, enemy_y + 5),
    ]
    ticks = [0, 100, 200, 300, 400, 500, 600, 700, 1900, 2500]

    module = load_module(monkeypatch, frames, positions, ticks)

    assert module.ships_placed == len(module.player_ships)
    assert any(cell.hitted for row in module.enemy_grid for cell in row)
