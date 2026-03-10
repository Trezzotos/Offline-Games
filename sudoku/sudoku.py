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


# =========================
# CONFIG
# =========================

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


# =========================
# ENGINE (testabile)
# =========================

class SudokuEngine:
    """Motore logico per generare e risolvere Sudoku."""

    @staticmethod
    def find_empty(board):
        for i in range(9):
            for j in range(9):
                if board[i, j] == 0:
                    return i, j
        return None

    @staticmethod
    def is_valid(board, row, col, num):

        if num in board[row, :] or num in board[:, col]:
            return False

        r_start = (row // 3) * 3
        c_start = (col // 3) * 3

        if num in board[r_start:r_start+3, c_start:c_start+3]:
            return False

        return True

    def solve(self, board):

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


# =========================
# GAME STATE
# =========================

class GameState:
    """Contiene lo stato della partita."""

    def __init__(self):

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


# =========================
# RENDERER (grafica)
# =========================

class Renderer:

    def __init__(self, screen, fonts):

        self.screen = screen
        self.font_big, self.font_med, self.font_small, self.font_note = fonts

    def draw_menu(self, game):

        self.screen.fill(THEME["bg"])

        title = self.font_big.render("SUDOKU", True, THEME["accent"])
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, 150)))

        for i, opt in enumerate(game.menu_options):

            selected = i == game.menu_sel
            color = THEME["select"] if selected else THEME["text"]

            text = self.font_med.render(opt, True, color)
            rect = text.get_rect(center=(WIDTH // 2, 350 + i * 80))

            if selected:
                bg_rect = rect.inflate(40, 20)
                pygame.draw.rect(self.screen, THEME["panel"], bg_rect, border_radius=10)

            self.screen.blit(text, rect)

    def draw_grid(self):

        for i in range(10):

            thick = 4 if i % 3 == 0 else 1

            pygame.draw.line(self.screen, THEME["grid"], (0, i*CELL_SIZE), (WIDTH, i*CELL_SIZE), thick)
            pygame.draw.line(self.screen, THEME["grid"], (i*CELL_SIZE, 0), (i*CELL_SIZE, WIDTH), thick)

    def draw_numbers(self, game):

        state = game.state

        for r in range(9):
            for c in range(9):

                val = state.grid[r, c]

                rect = pygame.Rect(c*CELL_SIZE, r*CELL_SIZE, CELL_SIZE, CELL_SIZE)

                if val != 0:

                    if state.is_fixed[r, c]:
                        color = THEME["fixed"]

                    elif val == state.solution[r, c]:
                        color = THEME["accent"]

                    else:
                        color = THEME["error"]

                    if state.won:
                        color = THEME["win"]

                    img = self.font_med.render(str(val), True, color)
                    self.screen.blit(img, img.get_rect(center=rect.center))

                elif state.notes[r][c]:

                    for n in state.notes[r][c]:

                        idx = n-1
                        nx = c*CELL_SIZE + (idx % 3)*(CELL_SIZE//3) + 8
                        ny = r*CELL_SIZE + (idx // 3)*(CELL_SIZE//3) + 4

                        img = self.font_note.render(str(n), True, THEME["note"])
                        self.screen.blit(img, (nx, ny))

    def draw_footer(self, game):

        state = game.state

        lives_img = self.font_small.render(
            f"VITE: {'I ' * state.lives}",
            True,
            THEME["error"] if state.lives == 1 else THEME["text"],
        )

        self.screen.blit(lives_img, (20, WIDTH + 10))

        diff_img = self.font_small.render(
            f"MODALITÀ: {state.difficulty_label}",
            True,
            (150,150,150)
        )

        self.screen.blit(diff_img, (WIDTH - diff_img.get_width() - 20, WIDTH + 10))

        footer_y = WIDTH + 55

        status = "ATTIVA" if state.note_mode else "DISATTIVATA"
        status_color = THEME["note"] if state.note_mode else (120,120,120)

        label = self.font_small.render("[A] ANNOTAZIONE:", True, THEME["text"])
        status_surf = self.font_small.render(status, True, status_color)

        total = label.get_width() + status_surf.get_width()
        start = (WIDTH - total)//2

        self.screen.blit(label,(start,footer_y-10))
        self.screen.blit(status_surf,(start+label.get_width(),footer_y-10))

        if state.won or state.game_over:

            msg = "VITTORIA! ESC per Menu" if state.won else "GAME OVER! ESC per Menu"
            color = THEME["win"] if state.won else THEME["error"]

            img = self.font_small.render(msg,True,color)

            self.screen.blit(img,img.get_rect(center=(WIDTH//2,footer_y+25)))

    def draw_game(self, game):

        self.screen.fill(THEME["bg"])

        self.draw_grid()
        self.draw_numbers(game)
        self.draw_footer(game)

        state = game.state

        if not state.won and not state.game_over:

            color = THEME["note"] if state.note_mode else THEME["select"]

            pygame.draw.rect(
                self.screen,
                color,
                (
                    state.selected[1]*CELL_SIZE,
                    state.selected[0]*CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE
                ),
                3
            )


# =========================
# INPUT CONTROLLER
# =========================

class InputController:

    def handle_number(self, game, value):

        state = game.state
        r, c = state.selected

        if state.is_fixed[r, c]:
            return

        if state.grid[r, c] == value:
            return

        if state.note_mode:

            if value in state.notes[r][c]:
                state.notes[r][c].remove(value)
            else:
                state.notes[r][c].add(value)

        else:

            state.grid[r, c] = value
            state.notes[r][c].clear()

            if value != state.solution[r, c]:

                state.lives -= 1

                if state.lives <= 0:
                    state.game_over = True

            elif np.array_equal(state.grid, state.solution):

                state.won = True


# =========================
# GAME CONTROLLER
# =========================

class SudokuGame:

    def __init__(self):

        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("SUDOKU")

        self.font_big = pygame.font.SysFont("Verdana", 40, bold=True)
        self.font_med = pygame.font.SysFont("Verdana", 30, bold=True)
        self.font_small = pygame.font.SysFont("Verdana", 18)
        self.font_note = pygame.font.SysFont("Verdana", 14)

        fonts = (self.font_big, self.font_med, self.font_small, self.font_note)

        self.engine = SudokuEngine()
        self.state = GameState()

        self.renderer = Renderer(self.screen, fonts)
        self.input = InputController()

        self.state_mode = "MENU"

        self.menu_options = ["FACILE", "MEDIO", "DIFFICILE"]
        self.menu_sel = 1

    def setup_game(self, difficulty):

        state = self.state

        state.difficulty_label = difficulty

        state.solution, state.grid = self.engine.generate_puzzle(difficulty)

        state.notes = [[set() for _ in range(9)] for _ in range(9)]

        state.is_fixed = state.grid != 0
        state.selected = [4,4]

        state.won = False
        state.game_over = False
        state.lives = 3
        state.note_mode = False

        self.state_mode = "PLAYING"

    def run(self):

        while True:

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:

                    if self.state_mode == "PLAYING":
                        self.state_mode = "MENU"

                    else:
                        subprocess.Popen([sys.executable,"main_menu.py"])
                        pygame.quit()
                        sys.exit()

                if self.state_mode == "MENU":

                    if event.type == pygame.KEYDOWN:

                        if event.key == pygame.K_UP:
                            self.menu_sel = (self.menu_sel-1)%3

                        elif event.key == pygame.K_DOWN:
                            self.menu_sel = (self.menu_sel+1)%3

                        elif event.key == pygame.K_RETURN:
                            self.setup_game(self.menu_options[self.menu_sel])

                elif self.state_mode == "PLAYING":

                    if event.type == pygame.KEYDOWN:

                        state = self.state

                        if event.key == pygame.K_a:
                            state.note_mode = not state.note_mode

                        elif event.key == pygame.K_UP:
                            state.selected[0] = (state.selected[0]-1)%9

                        elif event.key == pygame.K_DOWN:
                            state.selected[0] = (state.selected[0]+1)%9

                        elif event.key == pygame.K_LEFT:
                            state.selected[1] = (state.selected[1]-1)%9

                        elif event.key == pygame.K_RIGHT:
                            state.selected[1] = (state.selected[1]+1)%9

                        elif pygame.K_1 <= event.key <= pygame.K_9:
                            self.input.handle_number(self, int(event.unicode))

                        elif event.key in (pygame.K_BACKSPACE, pygame.K_0):

                            r, c = state.selected

                            if not state.is_fixed[r,c]:
                                state.grid[r,c] = 0
                                state.notes[r][c].clear()

            if self.state_mode == "MENU":
                self.renderer.draw_menu(self)
            else:
                self.renderer.draw_game(self)

            pygame.display.flip()


# =========================
# MAIN
# =========================

if __name__ == "__main__":
    SudokuGame().run()