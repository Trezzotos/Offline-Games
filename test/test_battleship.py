"""Test coverage migliorato per il gioco Battleship."""

# pylint: disable=no-member,protected-access,import-error,redefined-outer-name,line-too-long
import importlib.util
import os
import sys
from pathlib import Path

import pygame
import pytest


os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")


MODULE_NAME = "battleship_attached"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = PROJECT_ROOT / "src" / "battleship.py"


def load_module():
    """Importa il file allegato come modulo isolato."""
    pygame.init()
    if MODULE_NAME in sys.modules:
        del sys.modules[MODULE_NAME]

    spec = importlib.util.spec_from_file_location(MODULE_NAME, MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[MODULE_NAME] = module
    spec.loader.exec_module(module)
    return module


def run_main(
    monkeypatch, module, event_frames=None, mouse_positions=None, tick_values=None
):
    """Esegue main() con eventi e tempi controllati."""
    pygame.init()
    event_frames = event_frames or [[pygame.event.Event(pygame.QUIT)]]
    mouse_positions = mouse_positions or [(0, 0)]
    tick_values = tick_values or [0] * 30

    frame_iter = iter(event_frames)
    pos_iter = iter(mouse_positions)
    tick_iter = iter(tick_values)
    last_pos = [mouse_positions[-1]]

    def fake_event_get():
        try:
            return next(frame_iter)
        except StopIteration:
            return [pygame.event.Event(pygame.QUIT)]

    def fake_mouse_get_pos():
        try:
            last_pos[0] = next(pos_iter)
        except StopIteration:
            pass
        return last_pos[0]

    def fake_get_ticks():
        try:
            return next(tick_iter)
        except StopIteration:
            return tick_values[-1] if tick_values else 0

    monkeypatch.setattr(pygame.event, "get", fake_event_get)
    monkeypatch.setattr(pygame.mouse, "get_pos", fake_mouse_get_pos)
    monkeypatch.setattr(pygame.time, "get_ticks", fake_get_ticks)

    module.main()
    pygame.init()


def set_player_ship(module, coords, ship_id=0):
    """Inserisce una nave del giocatore in coordinate note."""
    for row, col in coords:
        module.player_grid[row][col].contains_ship = True
        module.player_grid[row][col].set_ship_id(ship_id)
    module.player_ships[ship_id].remaining_cells = len(coords)


@pytest.fixture(name="game_module")
def fixture_game_module():
    """Restituisce il modulo pronto per i test."""
    module = load_module()
    module.reset_game()
    return module


def test_import_and_basic_state(game_module):
    """Controlla import e stato iniziale."""
    assert MODULE_PATH.exists()
    assert game_module.WIDTH == 800
    assert game_module.HEIGHT == 900
    assert len(game_module.player_grid) == 10
    assert len(game_module.enemy_grid) == 10
    assert len(game_module.player_ships) == 5
    assert len(game_module.enemy_ships) == 5
    assert game_module.player_lives == 16
    assert game_module.enemy_lives == 16


def test_cell_and_ship_methods_and_names(game_module):
    """Copre Cell, Ship, nomi nave e set_coords su entrambe le griglie."""
    game_module.reset_game()

    cell = game_module.Cell(True, False, False)
    cell.set_ship_id(77)
    assert cell.contains_ship is True
    assert cell.hitted is False
    assert cell.sunk is False
    assert cell.ship_id == 77

    destroyer = game_module.Ship(2)
    cruiser = game_module.Ship(3)
    submarine = game_module.Ship(4)
    carrier = game_module.Ship(5)
    invalid = game_module.Ship(7)

    assert destroyer.name == "Destroyer"
    assert cruiser.name == "Cruiser"
    assert submarine.name == "Submarine"
    assert carrier.name == "Carrier"
    assert invalid.name == "invalid_name"

    destroyer.set_direction(1)
    destroyer.set_coords(0, 0, 0)
    assert game_module.player_grid[0][0].ship_id == destroyer.ship_id
    assert game_module.player_grid[0][1].ship_id == destroyer.ship_id

    cruiser.set_direction(0)
    cruiser.set_coords(3, 1, 1)
    assert game_module.enemy_grid[1][3].ship_id == cruiser.ship_id
    assert game_module.enemy_grid[2][3].ship_id == cruiser.ship_id
    assert game_module.enemy_grid[3][3].ship_id == cruiser.ship_id

    destroyer.remaining_cells = 0
    assert destroyer.is_sunk() is True
    assert carrier.is_sunk() is False


def test_can_place_preview_and_draw(game_module):
    """Copre validazione piazzamento e preview."""
    game_module.reset_game()

    assert game_module.can_place_ship(game_module.player_grid, 0, 0, 2, 1) is True
    assert game_module.can_place_ship(game_module.player_grid, 0, 0, 2, -1) is True
    assert game_module.can_place_ship(game_module.player_grid, -1, 0, 2, 1) is False
    assert game_module.can_place_ship(game_module.player_grid, 9, 9, 3, 1) is False
    assert game_module.can_place_ship(game_module.player_grid, 9, 9, 3, -1) is False

    game_module.player_grid[0][0].contains_ship = True
    assert game_module.can_place_ship(game_module.player_grid, 0, 0, 2, 1) is False
    assert game_module.can_place_ship(game_module.player_grid, 0, 0, 2, -1) is False

    game_module.reset_game()
    mx = game_module.player_grid_x + 5
    my = game_module.player_grid_y + 5
    cells, valid = game_module.get_preview_cells(mx, my, 2, 1)
    assert cells == [(0, 0), (0, 1)]
    assert valid is True

    vertical_cells, vertical_valid = game_module.get_preview_cells(mx, my, 3, -1)
    assert vertical_cells == [(0, 0), (1, 0), (2, 0)]
    assert vertical_valid is True

    edge_x = game_module.player_grid_x + 9 * game_module.cell_dimension + 5
    edge_y = game_module.player_grid_y + 9 * game_module.cell_dimension + 5
    partial_cells, partial_valid = game_module.get_preview_cells(edge_x, edge_y, 3, -1)
    assert partial_cells == [(9, 9)]
    assert partial_valid is False

    outside_cells, outside_valid = game_module.get_preview_cells(0, 0, 2, 1)
    assert outside_cells == []
    assert outside_valid is False

    game_module.draw_ship_preview(game_module.display, [], True)
    game_module.draw_ship_preview(game_module.display, cells, True)
    game_module.draw_ship_preview(game_module.display, cells, False)


def test_place_ship_and_place_enemy_ships(game_module):
    """Controlla piazzamento orizzontale, verticale e navi nemiche."""
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
    mapped = sum(
        cell.ship_id != -1
        for row in game_module.enemy_grid
        for cell in row
        if cell.contains_ship
    )
    assert occupied == 16
    assert mapped == 16
    assert game_module.enemy_ships_placed is True


def test_enemy_attack_horizontal_targeting_and_sink(game_module, monkeypatch):
    """Copre hit, orientamento orizzontale e reset target dopo affondamento."""
    game_module.reset_game()
    game_module.player_lives = 6
    set_player_ship(game_module, [(0, 0), (0, 1), (0, 2)], ship_id=0)

    monkeypatch.setattr(game_module.random, "choice", lambda seq: (0, 0))
    monkeypatch.setattr(
        game_module.random,
        "shuffle",
        lambda seq: seq.__setitem__(slice(None), [(0, 1), (1, 0), (0, -1), (-1, 0)]),
    )

    assert game_module.enemy_attack() is True
    assert game_module.player_grid[0][0].hitted is True
    assert game_module.player_lives == 5
    assert game_module.enemy_attack.target_ship_id == 0
    assert game_module.enemy_attack.orientation is None

    assert game_module.enemy_attack() is True
    assert game_module.player_grid[0][1].hitted is True
    assert game_module.enemy_attack.orientation == "H"

    assert game_module.enemy_attack() is True
    assert game_module.player_grid[0][2].hitted is True
    assert game_module.player_ships[0].remaining_cells == 0
    assert game_module.enemy_attack.target_ship_id is None
    assert game_module.enemy_attack.hits == []
    assert game_module.enemy_attack.orientation is None
    assert game_module.enemy_attack_mode == 1


def test_enemy_attack_vertical_reset_target_and_game_over(game_module, monkeypatch):
    """Copre reset di un target già affondato, orientamento verticale e sconfitta."""
    game_module.reset_game()
    game_module.player_lives = 2
    set_player_ship(game_module, [(0, 0), (1, 0)], ship_id=0)

    game_module.enemy_attack.target_ship_id = 1
    game_module.enemy_attack.hits = [(5, 5)]
    game_module.enemy_attack.orientation = "H"
    game_module.player_ships[1].remaining_cells = 0

    monkeypatch.setattr(game_module.random, "choice", lambda seq: (0, 0))
    monkeypatch.setattr(
        game_module.random,
        "shuffle",
        lambda seq: seq.__setitem__(slice(None), [(1, 0), (0, 1), (0, -1), (-1, 0)]),
    )

    assert game_module.enemy_attack() is True
    assert game_module.enemy_attack.target_ship_id == 0
    assert game_module.enemy_attack.orientation is None

    assert game_module.enemy_attack() is True
    assert game_module.enemy_attack.orientation is None
    assert game_module.player_lives == 0
    assert game_module.game_over is True
    assert game_module.winner_text == "YOU LOSE!"


def test_enemy_attack_miss_and_no_available_cells(game_module, monkeypatch):
    """Copre ramo di miss e ramo senza celle disponibili."""
    game_module.reset_game()
    game_module.PLAYER_TURN = False
    monkeypatch.setattr(game_module.random, "choice", lambda seq: (0, 0))

    assert game_module.enemy_attack() is True
    assert game_module.player_grid[0][0].hitted is True
    assert game_module.player_grid[0][0].sunk is False
    assert game_module.PLAYER_TURN is True

    for row in game_module.player_grid:
        for cell in row:
            cell.hitted = True

    game_module.PLAYER_TURN = False
    assert game_module.enemy_attack() is True
    assert game_module.PLAYER_TURN is True


def test_reset_game_and_draw_helpers(game_module):
    """Controlla reset completo e funzioni di disegno."""
    game_module.player_lives = 1
    game_module.enemy_lives = 1
    game_module.PLAYER_TURN = False
    game_module.ships_placed = 4
    game_module.toggle = -1
    game_module.game_over = True
    game_module.winner_text = "TEST"
    game_module.show_instructions = True
    game_module.enemy_attack_pending = True
    game_module.enemy_attack_start = 555
    game_module.enemy_attack.target_ship_id = 0
    game_module.enemy_attack.hits = [(0, 0)]
    game_module.enemy_attack.orientation = "H"

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
    assert game_module.enemy_attack_pending is False
    assert game_module.enemy_attack_start == 0
    assert game_module.enemy_attack.target_ship_id is None
    assert game_module.enemy_attack.hits == []
    assert game_module.enemy_attack.orientation is None


def test_main_help_overlay_open_and_close_resume(monkeypatch):
    """Copre apertura help, chiusura overlay e ripresa del timer."""
    module = load_module()
    module.reset_game()
    module.enemy_attack_pending = True
    module.show_instructions = False

    help_click = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN, button=1, pos=module.help_button.center
    )
    close_click = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN, button=1, pos=module.close_instructions_button.center
    )

    run_main(
        monkeypatch,
        module,
        event_frames=[[help_click], [close_click], [pygame.event.Event(pygame.QUIT)]],
        mouse_positions=[
            module.help_button.center,
            module.close_instructions_button.center,
            (0, 0),
        ],
        tick_values=[0, 100, 200, 300],
    )

    assert module.show_instructions is False
    assert module.enemy_attack_start == 100


def test_main_restart_button(monkeypatch):
    """Copre il pulsante di restart quando la partita è finita."""
    module = load_module()
    module.reset_game()
    module.game_over = True
    module.winner_text = "YOU LOSE!"
    module.player_lives = 1
    module.ships_placed = 3

    restart_click = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN, button=1, pos=module.restart_button.center
    )

    run_main(
        monkeypatch,
        module,
        event_frames=[[restart_click], [pygame.event.Event(pygame.QUIT)]],
        mouse_positions=[module.restart_button.center, (0, 0)],
        tick_values=[0, 100, 200],
    )

    assert module.game_over is False
    assert module.winner_text == ""
    assert module.player_lives == 16
    assert module.ships_placed == 0


def test_main_place_ships_and_player_hit(monkeypatch):
    """Copre piazzamento completo e colpo riuscito del giocatore."""
    module = load_module()
    module.reset_game()

    def fixed_enemy_ships():
        module.enemy_grid[0][0].contains_ship = True
        module.enemy_ships_placed = True

    monkeypatch.setattr(module, "place_enemy_ships", fixed_enemy_ships)

    px, py = module.player_grid_x, module.player_grid_y
    ex, ey = module.enemy_grid_x, module.enemy_grid_y
    events = [
        [pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(px + 5, py + 5))],
        [pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(px + 5, py + 45))],
        [pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(px + 5, py + 85))],
        [pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(px + 5, py + 125))],
        [pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(px + 5, py + 165))],
        [pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(ex + 5, ey + 5))],
        [pygame.event.Event(pygame.QUIT)],
    ]
    positions = [
        (px + 5, py + 5),
        (px + 5, py + 45),
        (px + 5, py + 85),
        (px + 5, py + 125),
        (px + 5, py + 165),
        (ex + 5, ey + 5),
        (0, 0),
    ]

    run_main(
        monkeypatch, module, events, positions, [0, 100, 200, 300, 400, 500, 600, 700]
    )

    assert module.ships_placed == len(module.player_ships)
    assert module.enemy_grid[0][0].hitted is True
    assert module.enemy_grid[0][0].sunk is True
    assert module.enemy_lives == 15


def test_main_place_ships_player_miss_triggers_enemy_attack(monkeypatch):
    """Copre miss del giocatore e attacco ritardato del nemico."""
    module = load_module()
    module.reset_game()

    def fixed_enemy_ships():
        module.enemy_ships_placed = True

    monkeypatch.setattr(module, "place_enemy_ships", fixed_enemy_ships)
    monkeypatch.setattr(module.random, "choice", lambda seq: (0, 0))

    px, py = module.player_grid_x, module.player_grid_y
    ex, ey = module.enemy_grid_x, module.enemy_grid_y
    events = [
        [pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(px + 5, py + 5))],
        [pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(px + 5, py + 45))],
        [pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(px + 5, py + 85))],
        [pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(px + 5, py + 125))],
        [pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(px + 5, py + 165))],
        [pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(ex + 5, ey + 5))],
        [],
        [pygame.event.Event(pygame.QUIT)],
    ]
    positions = [
        (px + 5, py + 5),
        (px + 5, py + 45),
        (px + 5, py + 85),
        (px + 5, py + 125),
        (px + 5, py + 165),
        (ex + 5, ey + 5),
        (0, 0),
        (0, 0),
    ]
    ticks = [0, 100, 200, 300, 400, 500, 1601, 1700, 1800]

    run_main(monkeypatch, module, events, positions, ticks)

    assert module.enemy_grid[0][0].hitted is True
    assert module.enemy_grid[0][0].sunk is False
    assert module.player_grid[0][0].hitted is True
