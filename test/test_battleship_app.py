"""Test di controller e rendering di Battleship."""

import random

import pygame
import pytest

from battleship_game import config
from battleship_game.app import BattleshipApp, EnemyTurnTimer
from battleship_game.board_view import BoardView
from battleship_game.game import BattleshipGame, Phase
from battleship_game.model import Board

LEFT, RIGHT = 1, 3


def click(pos: tuple[int, int], button: int = LEFT) -> pygame.event.Event:
    """Evento di click del mouse."""
    return pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=button, pos=pos)


def cell_center(view: BoardView, row: int, col: int) -> tuple[int, int]:
    """Centro in pixel di una cella."""
    return view.cell_rect(row, col).center


@pytest.fixture(name="app")
def fixture_app() -> BattleshipApp:
    """Applicazione con partita deterministica."""
    pygame.init()
    return BattleshipApp(game=BattleshipGame(rng=random.Random(5)))


def place_all(app: BattleshipApp) -> None:
    """Piazza la flotta con click del mouse."""
    for row in range(5):
        app.handle_event(click(cell_center(app.renderer.player_view, row * 2, 0)), 0)
    assert app.game.phase is Phase.BATTLE


def enemy_cell(app: BattleshipApp, *, ship: bool) -> tuple[int, int]:
    """Prima cella nemica con o senza nave."""
    return next(
        (r, c)
        for r in range(10)
        for c in range(10)
        if app.game.enemy_board.cell(r, c).has_ship == ship
    )


def test_timer() -> None:
    """Il timer scatta dopo il ritardo."""
    timer = EnemyTurnTimer(delay_ms=100)
    timer.restart(50)
    assert not timer.is_due(149)
    assert timer.is_due(150)


def test_quit_event_stops_loop(app: BattleshipApp) -> None:
    """QUIT ferma il ciclo."""
    app.handle_event(pygame.event.Event(pygame.QUIT), 0)
    assert app.running is False


def test_unrelated_event_is_ignored(app: BattleshipApp) -> None:
    """Eventi non gestiti non hanno effetto."""
    app.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a), 0)
    assert app.running


def test_placement_with_clicks_and_rotation(app: BattleshipApp) -> None:
    """Click sinistro piazza, destro ruota; click fuori plancia è ignorato."""
    app.handle_event(click((0, 0)), 0)
    assert app.game.ships_placed == 0
    app.handle_event(click((0, 0), RIGHT), 0)
    assert app.game.orientation.value == "V"
    app.handle_event(click((0, 0), 2), 0)
    app.handle_event(click((0, 0), RIGHT), 0)
    assert app.game.orientation.value == "H"
    place_all(app)


def test_help_overlay_pauses_and_resumes_enemy_timer(app: BattleshipApp) -> None:
    """Help apre l'overlay; chiuderlo riavvia il timer se tocca al nemico."""
    place_all(app)
    app.game.player_turn = False
    app.handle_event(click(config.HELP_BUTTON.center), 10)
    assert app.show_instructions
    app.handle_event(click(config.HELP_BUTTON.center), 20)
    assert app.show_instructions
    app.update(5000)
    assert app.game.is_enemy_turn
    app.handle_event(click(config.CLOSE_INSTRUCTIONS_BUTTON.center, RIGHT), 30)
    assert app.show_instructions
    app.handle_event(click(config.CLOSE_INSTRUCTIONS_BUTTON.center), 100)
    assert not app.show_instructions
    assert app.timer.started_at == 100


def test_closing_help_on_player_turn_does_not_touch_timer(app: BattleshipApp) -> None:
    """Se è il turno del giocatore il timer non viene toccato."""
    place_all(app)
    app.show_instructions = True
    app.handle_event(click(config.CLOSE_INSTRUCTIONS_BUTTON.center), 77)
    assert app.timer.started_at == 0


def test_player_miss_triggers_delayed_enemy_attack(app: BattleshipApp) -> None:
    """Dopo un colpo a vuoto il nemico spara solo allo scadere del ritardo."""
    place_all(app)
    row, col = enemy_cell(app, ship=False)
    app.handle_event(click(cell_center(app.renderer.enemy_view, row, col)), 1000)
    assert app.game.is_enemy_turn
    app.update(1500)
    assert app.game.is_enemy_turn
    app.update(2000)
    assert not app.game.is_enemy_turn or app.timer.started_at == 2000
    assert len(app.game.player_board.available_targets()) < 100


def test_attack_click_outside_grid_and_on_hit(app: BattleshipApp) -> None:
    """Click fuori griglia o su un colpo che mantiene il turno non avviano il nemico."""
    place_all(app)
    app.handle_event(click((0, 0)), 0)
    row, col = enemy_cell(app, ship=True)
    app.handle_event(click(cell_center(app.renderer.enemy_view, row, col)), 0)
    assert app.game.player_turn
    app.handle_event(click(cell_center(app.renderer.enemy_view, row, col), RIGHT), 0)
    assert app.game.player_turn


def test_game_over_and_restart(app: BattleshipApp) -> None:
    """A partita finita solo il pulsante di restart ha effetto."""
    place_all(app)
    app.game.winner_text = "YOU LOSE!"
    app.handle_event(click((0, 0)), 0)
    assert app.game.is_game_over
    app.handle_event(click(config.RESTART_BUTTON.center, RIGHT), 0)
    assert app.game.is_game_over
    app.handle_event(click(config.RESTART_BUTTON.center), 0)
    assert app.game.phase is Phase.PLACEMENT
    assert not app.show_instructions


def test_update_idle_when_player_turn(app: BattleshipApp) -> None:
    """Se non tocca al nemico update non fa nulla."""
    place_all(app)
    before = len(app.game.player_board.available_targets())
    app.update(10_000)
    assert len(app.game.player_board.available_targets()) == before


def test_run_loop_renders_and_quits(
    app: BattleshipApp, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Il ciclo principale disegna un frame ed esce su QUIT."""
    frames = iter([[], [pygame.event.Event(pygame.QUIT)]])
    monkeypatch.setattr(pygame.event, "get", lambda: next(frames))
    monkeypatch.setattr(pygame.mouse, "get_pos", lambda: (0, 0))
    app.run()
    assert app.running is False


def test_board_view_locate_and_geometry() -> None:
    """Conversione pixel <-> cella."""
    board = Board((2,))
    view = BoardView((100, 50), cell_size=40)
    assert view.locate(board, (99, 60)) is None
    assert view.locate(board, (100, 50)) == (0, 0)
    assert view.locate(board, (100 + 40 * 3 + 1, 50 + 40 * 2 + 1)) == (2, 3)
    assert view.locate(board, (100 + 400, 60)) is None
    assert view.pixel_size(board) == (400, 400)


@pytest.mark.parametrize("phase", ["placement", "battle", "enemy", "help", "over"])
def test_screen_renderer_all_screens(app: BattleshipApp, phase: str) -> None:
    """Ogni schermata si disegna senza errori."""
    mouse = cell_center(app.renderer.player_view, 0, 0)
    show_help = False
    if phase != "placement":
        place_all(app)
        app.game.player_shoot(*enemy_cell(app, ship=False))
        app.game.enemy_shoot()
        app.game.player_board.receive_shot(0, 0)
    if phase == "battle":
        app.game.player_turn = True
    if phase == "enemy":
        app.game.player_turn = False
    if phase == "help":
        show_help = True
    if phase == "over":
        app.game.winner_text = "YOU WIN!"
    app.renderer.draw(app.game, mouse, show_help)
    if phase == "placement":
        app.renderer.draw(app.game, mouse, True)
        app.renderer.draw(app.game, (0, 0), False)
    app.renderer.player_view.draw_ship_preview(app.screen, [], True)
    app.renderer.player_view.draw_ship_preview(app.screen, [(0, 0)], False)
