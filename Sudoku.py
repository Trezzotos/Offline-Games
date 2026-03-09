"""
Sudoku game sviluppato con pygame.

Funzionalità:
- generazione puzzle
- tre livelli di difficoltà
- modalità annotazione
- sistema vite
"""

import random
import subprocess
import sys

import numpy as np
import pygame


WIDTH = 600
HEIGHT = 780
GRID_SIZE = 9
CELL_SIZE = WIDTH // GRID_SIZE


THEME = {
    "bg": (30, 35, 45),
    "grid": (240, 240, 240),
    "text": (255, 255, 255),
    "accent": (0, 180, 255),
    "fixed": (150, 150, 150),
    "error": (255, 80, 80),
    "select": (255, 170, 0),
    "note": (255, 255, 100),
    "win": (50, 255, 50),
    "panel": (40, 45, 60),
}


class SudokuEngine:
    """Motore logico per generare e risolvere Sudoku."""

    @staticmethod
    def find_empty(board):
        """Trova la prima cella vuota."""
        for i in range(9):
            for j in range(9):
                if board[i, j] == 0:
                    return i, j
        return None

    @staticmethod
    def is_valid(board, row, col, num):
        """Controlla se un numero è valido."""
        if num in board[row, :] or num in board[:, col]:
            return False

        r_start = (row // 3) * 3
        c_start = (col // 3) * 3

        if num in board[r_start:r_start + 3, c_start:c_start + 3]:
            return False

        return True

    def solve(self, board):
        """Risolve il sudoku con backtracking."""
        empty = self.find_empty(board)

        if not empty:
            return True

        row, col = empty

        for num in np.random.permutation(range(1, 10)):

            if self.is_valid(board, row, col, num):

                board[row, col] = num

                if self.solve(board):
                    return True

                board[row, col] = 0

        return False

    def generate_puzzle(self, difficulty):
        """Genera un puzzle Sudoku."""
        board = np.zeros((9, 9), dtype="int8")

        self.solve(board)

        full_board = board.copy()

        diff_map = {
            "FACILE": 30,
            "MEDIO": 45,
            "DIFFICILE": 60,
        }

        attempts = diff_map.get(difficulty, 45)

        while attempts > 0:

            i = random.randint(0, 8)
            j = random.randint(0, 8)

            if board[i, j] != 0:
                board[i, j] = 0
                attempts -= 1

        return full_board, board


class SudokuGame:
    """Gestisce UI e logica del gioco."""

    def __init__(self):

        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("SUDOKU")

        self.font_big = pygame.font.SysFont("Verdana", 40, bold=True)
        self.font_med = pygame.font.SysFont("Verdana", 30, bold=True)
        self.font_small = pygame.font.SysFont("Verdana", 18)
        self.font_note = pygame.font.SysFont("Verdana", 14)

        self.engine = SudokuEngine()

        self.state = "MENU"

        self.menu_options = ["FACILE", "MEDIO", "DIFFICILE"]
        self.menu_sel = 1

        # stato gioco
        self.solution = None
        self.grid = None
        self.notes = None
        self.is_fixed = None
        self.selected = [4, 4]

        self.won = False
        self.game_over = False
        self.lives = 3
        self.note_mode = False
        self.difficulty_label = ""

    def setup_game(self, difficulty):
        """Inizializza una partita."""

        self.difficulty_label = difficulty

        self.solution, self.grid = self.engine.generate_puzzle(difficulty)

        self.notes = [[set() for _ in range(9)] for _ in range(9)]

        self.is_fixed = self.grid != 0
        self.selected = [4, 4]

        self.won = False
        self.game_over = False
        self.lives = 3
        self.note_mode = False

        self.state = "PLAYING"

    def draw_menu(self):
        """Disegna il menu principale."""

        self.screen.fill(THEME["bg"])

        title = self.font_big.render("SUDOKU", True, THEME["accent"])

        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, 150)))

        for i, opt in enumerate(self.menu_options):

            selected = i == self.menu_sel

            color = THEME["select"] if selected else THEME["text"]

            text = self.font_med.render(opt, True, color)

            rect = text.get_rect(center=(WIDTH // 2, 350 + i * 80))

            if selected:
                bg_rect = rect.inflate(40, 20)

                pygame.draw.rect(
                    self.screen,
                    THEME["panel"],
                    bg_rect,
                    border_radius=10,
                )

            self.screen.blit(text, rect)

    def draw_grid(self):
        """Disegna la griglia."""

        for i in range(10):

            thick = 4 if i % 3 == 0 else 1

            pygame.draw.line(
                self.screen,
                THEME["grid"],
                (0, i * CELL_SIZE),
                (WIDTH, i * CELL_SIZE),
                thick,
            )

            pygame.draw.line(
                self.screen,
                THEME["grid"],
                (i * CELL_SIZE, 0),
                (i * CELL_SIZE, WIDTH),
                thick,
            )

    def draw_numbers(self):
        """Disegna numeri e annotazioni."""

        for r in range(9):
            for c in range(9):

                val = self.grid[r, c]

                rect = pygame.Rect(
                    c * CELL_SIZE,
                    r * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE,
                )

                if val != 0:

                    if self.is_fixed[r, c]:
                        color = THEME["fixed"]

                    elif val == self.solution[r, c]:
                        color = THEME["accent"]

                    else:
                        color = THEME["error"]

                    if self.won:
                        color = THEME["win"]

                    img = self.font_med.render(str(val), True, color)

                    self.screen.blit(img, img.get_rect(center=rect.center))

                elif self.notes[r][c]:

                    for n in self.notes[r][c]:

                        idx = n - 1

                        nx = c * CELL_SIZE + (idx % 3) * (CELL_SIZE // 3) + 8
                        ny = r * CELL_SIZE + (idx // 3) * (CELL_SIZE // 3) + 4

                        img = self.font_note.render(str(n), True, THEME["note"])

                        self.screen.blit(img, (nx, ny))

    def draw_footer(self):
        """Disegna UI inferiore (vite e annotazione)."""

        lives_img = self.font_small.render(
            f"VITE: {'I ' * self.lives}",
            True,
            THEME["error"] if self.lives == 1 else THEME["text"],
        )

        self.screen.blit(lives_img, (20, WIDTH + 10))

        diff_img = self.font_small.render(
            f"MODALITÀ: {self.difficulty_label}",
            True,
            (150, 150, 150),
        )

        self.screen.blit(
            diff_img,
            (WIDTH - diff_img.get_width() - 20, WIDTH + 10),
        )

        footer_y = WIDTH + 55

        note_label = "[A] ANNOTAZIONE: "

        status = "ATTIVA" if self.note_mode else "DISATTIVATA"

        status_color = THEME["note"] if self.note_mode else (120, 120, 120)

        label_surf = self.font_small.render(note_label, True, THEME["text"])
        status_surf = self.font_small.render(status, True, status_color)

        total_w = label_surf.get_width() + status_surf.get_width()

        start_x = (WIDTH - total_w) // 2

        self.screen.blit(label_surf, (start_x, footer_y - 10))
        self.screen.blit(status_surf, (start_x + label_surf.get_width(), footer_y - 10))

        if self.won or self.game_over:

            msg = "VITTORIA! ESC per Menu" if self.won else "GAME OVER! ESC per Menu"

            color = THEME["win"] if self.won else THEME["error"]

            img = self.font_small.render(msg, True, color)

            self.screen.blit(
                img,
                img.get_rect(center=(WIDTH // 2, footer_y + 25)),
            )

    def draw_game(self):
        """Disegna l'interfaccia di gioco."""

        self.screen.fill(THEME["bg"])

        self.draw_grid()
        self.draw_numbers()
        self.draw_footer()

        if not self.won and not self.game_over:

            color = THEME["note"] if self.note_mode else THEME["select"]

            pygame.draw.rect(
                self.screen,
                color,
                (
                    self.selected[1] * CELL_SIZE,
                    self.selected[0] * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE,
                ),
                3,
            )

    def handle_input(self, value):
        """Gestisce input numerico."""

        r, c = self.selected

        if self.is_fixed[r, c]:
            return

        if self.grid[r, c] == value:
            return

        if self.note_mode:

            if value in self.notes[r][c]:
                self.notes[r][c].remove(value)

            else:
                self.notes[r][c].add(value)

        else:

            self.grid[r, c] = value
            self.notes[r][c].clear()

            if value != self.solution[r, c]:

                self.lives -= 1

                if self.lives <= 0:
                    self.game_over = True

            elif np.array_equal(self.grid, self.solution):

                self.won = True

    def handle_menu_events(self, event):
        """Gestisce input nel menu."""

        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_UP:
            self.menu_sel = (self.menu_sel - 1) % 3

        elif event.key == pygame.K_DOWN:
            self.menu_sel = (self.menu_sel + 1) % 3

        elif event.key == pygame.K_RETURN:
            self.setup_game(self.menu_options[self.menu_sel])

    def handle_game_events(self, event):
        """Gestisce input durante la partita."""

        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_a:
            self.note_mode = not self.note_mode

        elif event.key == pygame.K_UP:
            self.selected[0] = (self.selected[0] - 1) % 9

        elif event.key == pygame.K_DOWN:
            self.selected[0] = (self.selected[0] + 1) % 9

        elif event.key == pygame.K_LEFT:
            self.selected[1] = (self.selected[1] - 1) % 9

        elif event.key == pygame.K_RIGHT:
            self.selected[1] = (self.selected[1] + 1) % 9

        elif pygame.K_1 <= event.key <= pygame.K_9:
            self.handle_input(int(event.unicode))

        elif event.key in (pygame.K_BACKSPACE, pygame.K_0):

            r, c = self.selected

            if not self.is_fixed[r, c]:
                self.grid[r, c] = 0
                self.notes[r][c].clear()

    def run(self):
        """Loop principale."""

        while True:

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:

                    if self.state == "PLAYING":
                        self.state = "MENU"

                    else:
                        subprocess.Popen([sys.executable, "main_menu.py"])
                        pygame.quit()
                        sys.exit()

                if self.state == "MENU":
                    self.handle_menu_events(event)

                elif self.state == "PLAYING" and not self.won and not self.game_over:
                    self.handle_game_events(event)

            if self.state == "MENU":
                self.draw_menu()
            else:
                self.draw_game()

            pygame.display.flip()


if __name__ == "__main__":
    SudokuGame().run()