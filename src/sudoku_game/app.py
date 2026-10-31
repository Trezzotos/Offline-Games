"""Controller del Sudoku: eventi, modalità (menu/gioco) e ciclo principale."""

from __future__ import annotations

import sys
from enum import Enum

import pygame

from common.launcher import MENU_SCRIPT, GameLauncher, SubprocessLauncher
from sudoku_game.config import DIFFICULTIES, HEIGHT, WIDTH
from sudoku_game.engine import SudokuEngine
from sudoku_game.renderer import Fonts, Renderer
from sudoku_game.state import GameState

ARROW_DELTAS = {
    pygame.K_UP: (-1, 0),
    pygame.K_DOWN: (1, 0),
    pygame.K_LEFT: (0, -1),
    pygame.K_RIGHT: (0, 1),
}


class Mode(Enum):
    """Modalità dell'applicazione."""

    MENU = "MENU"
    PLAYING = "PLAYING"


def _default_fonts() -> Fonts:
    return (
        pygame.font.SysFont("Verdana", 40, bold=True),
        pygame.font.SysFont("Verdana", 30, bold=True),
        pygame.font.SysFont("Verdana", 18),
        pygame.font.SysFont("Verdana", 14),
    )


class SudokuGame:
    """Controller principale del gioco."""

    def __init__(
        self,
        engine: SudokuEngine | None = None,
        launcher: GameLauncher | None = None,
    ) -> None:
        pygame.init()
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("SUDOKU")
        self.engine = engine or SudokuEngine()
        self.launcher = launcher or SubprocessLauncher()
        self.renderer = Renderer(screen, _default_fonts())
        self.state: GameState | None = None
        self.mode = Mode.MENU
        self.menu_options = list(DIFFICULTIES)
        self.menu_sel = 1

    def setup_game(self, difficulty: str) -> None:
        """Inizializza una nuova partita."""
        solution, grid = self.engine.generate_puzzle(difficulty)
        self.state = GameState(solution, grid, difficulty)
        self.mode = Mode.PLAYING

    def handle_key(self, key: int, unicode: str = "") -> None:
        """Gestisce la pressione di un tasto in base alla modalità corrente."""
        if key == pygame.K_ESCAPE:
            self._handle_escape()
        elif self.mode is Mode.MENU:
            self._handle_menu_key(key)
        elif self.state is not None and not self.state.game_over:
            self._handle_play_key(self.state, key, unicode)

    def _handle_escape(self) -> None:
        if self.mode is Mode.PLAYING:
            self.mode = Mode.MENU
            return
        self.launcher.launch(MENU_SCRIPT)
        self.quit()

    def _handle_menu_key(self, key: int) -> None:
        if key == pygame.K_UP:
            self.menu_sel = (self.menu_sel - 1) % len(self.menu_options)
        elif key == pygame.K_DOWN:
            self.menu_sel = (self.menu_sel + 1) % len(self.menu_options)
        elif key == pygame.K_RETURN:
            self.setup_game(self.menu_options[self.menu_sel])

    @staticmethod
    def _handle_play_key(state: GameState, key: int, unicode: str) -> None:
        if key == pygame.K_a:
            state.toggle_note_mode()
        elif key in ARROW_DELTAS:
            state.move_selection(*ARROW_DELTAS[key])
        elif pygame.K_1 <= key <= pygame.K_9:
            state.input_number(int(unicode) if unicode.isdigit() else key - pygame.K_0)
        elif key in (pygame.K_BACKSPACE, pygame.K_0):
            state.erase_selected()

    @staticmethod
    def quit() -> None:
        """Chiude Pygame ed esce dal processo."""
        pygame.quit()
        sys.exit()

    def draw(self) -> None:
        """Disegna il frame corrente."""
        if self.mode is Mode.MENU or self.state is None:
            self.renderer.draw_menu(self.menu_options, self.menu_sel)
        else:
            self.renderer.draw_game(self.state)
        pygame.display.flip()

    def run(self) -> None:
        """Ciclo principale."""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                if event.type == pygame.KEYDOWN:
                    self.handle_key(event.key, event.unicode)
            self.draw()
