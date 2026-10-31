"""Schermate di Battleship: piazzamento, battaglia e overlay."""

from __future__ import annotations

from dataclasses import dataclass

import pygame

from battleship_game import config
from battleship_game.board_view import BoardView
from battleship_game.game import BattleshipGame, Phase
from battleship_game.model import Orientation


@dataclass(frozen=True)
class Fonts:
    """Insieme dei font usati dalle schermate."""

    ship: pygame.font.Font
    title: pygame.font.Font
    big: pygame.font.Font
    button: pygame.font.Font
    small: pygame.font.Font

    @classmethod
    def load(cls, spec: config.FontSpec | None = None) -> "Fonts":
        """Crea i font a partire dalle dimensioni indicate (Pygame già inizializzato)."""
        spec = spec or config.FontSpec()
        return cls(
            ship=pygame.font.SysFont(None, spec.ship),
            title=pygame.font.SysFont(None, spec.title),
            big=pygame.font.SysFont(None, spec.big),
            button=pygame.font.SysFont(None, spec.button),
            small=pygame.font.SysFont(None, spec.small),
        )


class ScreenRenderer:
    """Compone le schermate a partire dallo stato della partita."""

    def __init__(self, surface: pygame.Surface, fonts: Fonts | None = None) -> None:
        self.surface = surface
        self.fonts = fonts or Fonts.load()
        self.player_view = BoardView(config.PLAYER_GRID_ORIGIN)
        self.enemy_view = BoardView(config.ENEMY_GRID_ORIGIN)

    def draw(
        self,
        game: BattleshipGame,
        mouse_pos: config.Coord,
        show_instructions: bool,
    ) -> None:
        """Disegna un frame completo."""
        self.surface.fill(config.BACKGROUND_COLOR)
        if game.phase is Phase.PLACEMENT:
            self._draw_placement(game, mouse_pos, show_instructions)
            self._draw_esc_hint()
            return
        self._draw_battle(game)
        if not game.is_game_over:
            self._draw_help_button()
            self._draw_esc_hint()
        if show_instructions and not game.is_game_over:
            self._draw_instructions_overlay()
        if game.is_game_over:
            self._draw_game_over(game.winner_text)

    # --- Piazzamento -------------------------------------------------------
    def _draw_placement(
        self, game: BattleshipGame, mouse_pos: config.Coord, show_instructions: bool
    ) -> None:
        length = game.current_ship_length
        if length is None:
            return
        ship = game.player_board.ships[game.ships_placed]
        self._center_text(
            "Place your ships", self.fonts.title, (config.WIDTH / 2, config.HEIGHT / 9)
        )
        self._center_text(
            ship.name, self.fonts.ship, (config.WIDTH / 2, config.HEIGHT / 5)
        )
        self._draw_ship_sample(length, game)
        self.player_view.draw(self.surface, game.player_board, reveal_ships=True)
        if not show_instructions:
            located = self.player_view.locate(game.player_board, mouse_pos)
            if located is not None:
                cells, valid = game.preview_cells(*located)
                self.player_view.draw_ship_preview(self.surface, cells, valid)

    def _draw_ship_sample(self, length: int, game: BattleshipGame) -> None:
        size = config.CELL_SIZE
        horizontal = game.orientation is Orientation.HORIZONTAL
        width = length * size if horizontal else size
        start_x = config.WIDTH / 2 - width / 2
        start_y = config.HEIGHT / 4
        for i in range(length):
            x = start_x + (i * size if horizontal else 0)
            y = start_y + (0 if horizontal else i * size)
            pygame.draw.rect(self.surface, config.SHIPS_COLOR, (x, y, size, size))
            pygame.draw.rect(self.surface, config.BLACK, (x, y, size, size), 1)

    # --- Battaglia -----------------------------------------------------------
    def _draw_battle(self, game: BattleshipGame) -> None:
        pygame.draw.line(
            self.surface,
            config.BLACK,
            (0, config.DIVIDER_Y),
            (config.WIDTH, config.DIVIDER_Y),
            3,
        )
        self.player_view.draw(self.surface, game.player_board, reveal_ships=True)
        self.enemy_view.draw(self.surface, game.enemy_board, reveal_ships=False)
        if game.player_turn:
            self.player_view.draw_dim_overlay(self.surface, game.player_board)
        else:
            self.enemy_view.draw_dim_overlay(self.surface, game.enemy_board)
        if not game.is_game_over:
            self._draw_turn_indicator(game)

    def _draw_esc_hint(self) -> None:
        """Mostra il suggerimento ESC in fondo allo schermo."""
        hint = self.fonts.small.render(
            config.ESC_HINT_TEXT, True, config.ESC_HINT_COLOR
        )
        self.surface.blit(
            hint, hint.get_rect(center=(config.WIDTH // 2, config.ESC_HINT_Y))
        )

    def _draw_turn_indicator(self, game: BattleshipGame) -> None:
        """Mostra lo stato del turno tra le due griglie."""
        if game.player_turn:
            label = config.TURN_YOUR_TEXT
            color = config.TURN_YOUR_COLOR
        else:
            label = config.TURN_AI_TEXT
            color = config.TURN_AI_COLOR
        text = self.fonts.button.render(label, True, color)
        self.surface.blit(text, text.get_rect(midleft=(20, config.STATUS_BAR_Y)))

    # --- Overlay ---------------------------------------------------------------
    def _draw_help_button(self) -> None:
        button = config.HELP_BUTTON
        pygame.draw.rect(self.surface, config.BUTTON_BLUE, button, border_radius=10)
        pygame.draw.rect(self.surface, config.WHITE, button, 2, border_radius=10)
        self._center_text("Help", self.fonts.button, button.center)

    def _draw_instructions_overlay(self) -> None:
        shade = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 170))
        self.surface.blit(shade, (0, 0))

        panel = pygame.Rect(0, 0, 420, 300)
        panel.center = (config.WIDTH // 2, config.HEIGHT // 2)
        pygame.draw.rect(self.surface, config.DARK_PANEL, panel, border_radius=16)
        pygame.draw.rect(self.surface, config.WHITE, panel, 2, border_radius=16)
        self._draw_close_button(panel)
        self._center_text(
            "Instructions", self.fonts.big, (config.WIDTH // 2, panel.top + 35)
        )
        line_y = panel.top + 70
        for line in config.INSTRUCTION_LINES:
            if line == "":
                line_y += 8
                continue
            text = self.fonts.small.render(line, True, (240, 240, 240))
            self.surface.blit(text, (panel.left + 24, line_y))
            line_y += 22

    def _draw_close_button(self, panel: pygame.Rect) -> None:
        button = pygame.Rect(panel.right - 44, panel.top + 8, 36, 36)
        config.CLOSE_INSTRUCTIONS_BUTTON.update(button)
        pygame.draw.rect(self.surface, config.BUTTON_RED, button, border_radius=8)
        pygame.draw.rect(self.surface, config.WHITE, button, 2, border_radius=8)
        margin = 10
        top_left = (button.x + margin, button.y + margin)
        bottom_right = (button.right - margin, button.bottom - margin)
        top_right = (button.right - margin, button.y + margin)
        bottom_left = (button.x + margin, button.bottom - margin)
        pygame.draw.line(self.surface, config.WHITE, top_left, bottom_right, 3)
        pygame.draw.line(self.surface, config.WHITE, top_right, bottom_left, 3)

    def _draw_game_over(self, message: str) -> None:
        shade = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 120))
        self.surface.blit(shade, (0, 0))
        self._center_text(
            message, self.fonts.big, (config.WIDTH // 2, config.HEIGHT // 2 - 40)
        )
        button = config.RESTART_BUTTON
        pygame.draw.rect(self.surface, config.BUTTON_GREEN, button)
        pygame.draw.rect(self.surface, config.BLACK, button, 2)
        self._center_text("Restart", self.fonts.button, button.center)

    def _center_text(
        self, text: str, font: pygame.font.Font, center: tuple[float, float]
    ) -> None:
        image = font.render(text, True, config.WHITE)
        self.surface.blit(image, image.get_rect(center=center))
