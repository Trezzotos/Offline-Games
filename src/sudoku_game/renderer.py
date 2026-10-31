"""Rendering grafico del Sudoku."""

import pygame

from sudoku_game.config import CELL_SIZE, GRID_SIZE, HEIGHT, THEME, WIDTH
from sudoku_game.state import GameState

Fonts = tuple[pygame.font.Font, pygame.font.Font, pygame.font.Font, pygame.font.Font]
NOTE_GRAY = (120, 120, 120)
MODE_GRAY = (150, 150, 150)


class Renderer:
    """Disegna menu e schermata di gioco."""

    def __init__(self, screen: pygame.Surface, fonts: Fonts) -> None:
        self.screen = screen
        self.f_big, self.f_med, self.f_small, self.f_note = fonts

    def draw_menu(self, options: list[str], current_sel: int) -> None:
        """Disegna il menu di selezione della difficoltà."""
        self.screen.fill(THEME["bg"])
        title = self.f_big.render("SUDOKU", True, THEME["accent"])
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, 150)))
        for i, opt in enumerate(options):
            selected = i == current_sel
            color = THEME["select"] if selected else THEME["text"]
            txt = self.f_med.render(opt, True, color)
            rect = txt.get_rect(center=(WIDTH // 2, 350 + i * 80))
            if selected:
                pygame.draw.rect(
                    self.screen, THEME["panel"], rect.inflate(40, 20), border_radius=10
                )
            self.screen.blit(txt, rect)

    def draw_game(self, state: GameState) -> None:
        """Renderizza l'intera schermata di gioco."""
        self.screen.fill(THEME["bg"])
        self._draw_grid()
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                self._draw_cell_content(row, col, state)
        self._draw_footer(state)
        if not state.finished:
            self._draw_selection(state)

    def _draw_grid(self) -> None:
        for i in range(GRID_SIZE + 1):
            thick = 4 if i % 3 == 0 else 1
            offset = i * CELL_SIZE
            pygame.draw.line(
                self.screen, THEME["grid"], (0, offset), (WIDTH, offset), thick
            )
            pygame.draw.line(
                self.screen, THEME["grid"], (offset, 0), (offset, WIDTH), thick
            )

    def _draw_selection(self, state: GameState) -> None:
        color = THEME["note"] if state.note_mode else THEME["select"]
        row, col = state.selected
        rect = (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(self.screen, color, rect, 3)

    def _draw_cell_content(self, row: int, col: int, state: GameState) -> None:
        value = state.grid[row, col]
        rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        if value != 0:
            img = self.f_med.render(
                str(value), True, self._digit_color(row, col, state)
            )
            self.screen.blit(img, img.get_rect(center=rect.center))
            return
        for note in state.notes[row][col]:
            idx = note - 1
            pos = (
                rect.x + (idx % 3) * (CELL_SIZE // 3) + 8,
                rect.y + (idx // 3) * (CELL_SIZE // 3) + 4,
            )
            self.screen.blit(self.f_note.render(str(note), True, THEME["note"]), pos)

    @staticmethod
    def _digit_color(row: int, col: int, state: GameState) -> tuple[int, int, int]:
        if state.won:
            return THEME["win"]
        if state.grid[row, col] != state.solution[row, col]:
            return THEME["error"]
        return THEME["fixed"] if state.is_fixed[row, col] else THEME["accent"]

    def _draw_footer(self, state: GameState) -> None:
        footer_y = WIDTH + 10
        self._draw_lives(state, footer_y)
        self._draw_difficulty(state, footer_y)
        self._draw_note_status(state, footer_y + 45)
        if state.finished:
            self._draw_end_message(state)

    def _draw_lives(self, state: GameState, y: int) -> None:
        color = THEME["error"] if state.lives == 1 else THEME["text"]
        label = self.f_small.render(f"VITE: {'I ' * state.lives}", True, color)
        self.screen.blit(label, (20, y))

    def _draw_difficulty(self, state: GameState, y: int) -> None:
        label = self.f_small.render(
            f"MODALITÀ: {state.difficulty_label}", True, MODE_GRAY
        )
        self.screen.blit(label, (WIDTH - label.get_width() - 20, y))

    def _draw_note_status(self, state: GameState, y: int) -> None:
        status_color = THEME["note"] if state.note_mode else NOTE_GRAY
        label = self.f_small.render("[A] ANNOTAZIONE:", True, THEME["text"])
        status = self.f_small.render(
            "ATTIVA" if state.note_mode else "DISATTIVATA", True, status_color
        )
        start_x = (WIDTH - (label.get_width() + status.get_width())) // 2
        self.screen.blit(label, (start_x, y))
        self.screen.blit(status, (start_x + label.get_width(), y))

    def _draw_end_message(self, state: GameState) -> None:
        message = "VITTORIA!" if state.won else "GAME OVER!"
        color = THEME["win"] if state.won else THEME["error"]
        img = self.f_small.render(f"{message} ESC per Menu", True, color)
        self.screen.blit(img, img.get_rect(center=(WIDTH // 2, HEIGHT - 35)))
