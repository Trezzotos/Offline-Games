"""Controller di Battleship: input, temporizzazione dei turni e ciclo principale."""

from __future__ import annotations

import pygame

from battleship_game import config
from battleship_game.game import BattleshipGame, Phase
from battleship_game.screens import ScreenRenderer

LEFT_BUTTON = 1
RIGHT_BUTTON = 3


class EnemyTurnTimer:
    """Ritardo tra due colpi consecutivi del nemico."""

    def __init__(self, delay_ms: int = config.ENEMY_ATTACK_DELAY_MS) -> None:
        self.delay_ms = delay_ms
        self.started_at = 0

    def restart(self, now: int) -> None:
        """Riparte il conteggio dall'istante indicato."""
        self.started_at = now

    def is_due(self, now: int) -> bool:
        """True quando il ritardo è trascorso."""
        return now - self.started_at >= self.delay_ms


class BattleshipApp:
    """Collega eventi Pygame, logica di gioco e rendering."""

    def __init__(
        self,
        game: BattleshipGame | None = None,
        screen: pygame.Surface | None = None,
    ) -> None:
        pygame.init()
        self.screen = screen or pygame.display.set_mode((config.WIDTH, config.HEIGHT))
        pygame.display.set_caption("Battleship")
        self.game = game or BattleshipGame()
        self.renderer = ScreenRenderer(self.screen)
        self.timer = EnemyTurnTimer()
        self.show_instructions = False
        self.running = True

    # --- Eventi ----------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event, now: int) -> None:
        """Smista un singolo evento Pygame."""
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_click(event.button, event.pos, now)

    def _handle_click(self, button: int, pos: config.Coord, now: int) -> None:
        if self.game.is_game_over:
            if button == LEFT_BUTTON and config.RESTART_BUTTON.collidepoint(pos):
                self._restart()
            return
        if self.show_instructions:
            self._handle_instructions_click(button, pos, now)
        elif button == LEFT_BUTTON and config.HELP_BUTTON.collidepoint(pos):
            self.show_instructions = True
        elif self.game.phase is Phase.PLACEMENT:
            self._handle_placement_click(button, pos)
        elif button == LEFT_BUTTON:
            self._handle_attack_click(pos, now)

    def _handle_instructions_click(
        self, button: int, pos: config.Coord, now: int
    ) -> None:
        if button == LEFT_BUTTON and config.CLOSE_INSTRUCTIONS_BUTTON.collidepoint(pos):
            self.show_instructions = False
            if self.game.is_enemy_turn:
                self.timer.restart(now)

    def _handle_placement_click(self, button: int, pos: config.Coord) -> None:
        if button == RIGHT_BUTTON:
            self.game.rotate()
        elif button == LEFT_BUTTON:
            located = self.renderer.player_view.locate(self.game.player_board, pos)
            if located is not None:
                self.game.place_current_ship(*located)

    def _handle_attack_click(self, pos: config.Coord, now: int) -> None:
        located = self.renderer.enemy_view.locate(self.game.enemy_board, pos)
        if located is None:
            return
        self.game.player_shoot(*located)
        if self.game.is_enemy_turn:
            self.timer.restart(now)

    def _restart(self) -> None:
        self.game.reset()
        self.show_instructions = False
        self.timer.restart(0)

    # --- Aggiornamento e ciclo principale ------------------------------------------
    def update(self, now: int) -> None:
        """Fa sparare il nemico quando il ritardo è scaduto."""
        if self.show_instructions or not self.game.is_enemy_turn:
            return
        if self.timer.is_due(now):
            self.game.enemy_shoot()
            self.timer.restart(now)

    def run(self) -> None:
        """Esegue il ciclo principale finché la finestra non viene chiusa."""
        clock = pygame.time.Clock()
        while self.running:
            now = pygame.time.get_ticks()
            for event in pygame.event.get():
                self.handle_event(event, now)
            self.update(now)
            self.renderer.draw(
                self.game, pygame.mouse.get_pos(), self.show_instructions
            )
            pygame.display.flip()
            clock.tick(config.FPS)
        pygame.quit()
