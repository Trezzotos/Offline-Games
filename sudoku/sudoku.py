# pylint: disable=no-member, invalid-name
"""
Sudoku Game - Versione ottimizzata e conforme agli standard Pylint.
Include generazione puzzle, tre difficoltà, note e sistema vite.
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

# 

class SudokuEngine:
    """Motore logico per generare e risolvere Sudoku."""

    @staticmethod
    def find_empty(board):
        """Trova la prima cella vuota (0) nella griglia."""
        for i in range(9):
            for j in range(9):
                if board[i, j] == 0:
                    return i, j
        return None

    @staticmethod
    def is_valid(board, row, col, num):
        """Verifica se un numero può essere inserito in una posizione."""
        if num in board[row, :] or num in board[:, col]:
            return False
        r_start, c_start = (row // 3) * 3, (col // 3) * 3
        if num in board[r_start:r_start+3, c_start:c_start+3]:
            return False
        return True

    def solve(self, board):
        """Risolve la griglia usando backtracking."""
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
        """Genera una nuova partita basata sulla difficoltà."""
        board = np.zeros((9, 9), dtype="int8")
        self.solve(board)
        full_board = board.copy()
        diff_map = {"FACILE": 30, "MEDIO": 45, "DIFFICILE": 60}
        attempts = diff_map.get(difficulty, 45)
        while attempts > 0:
            i, j = random.randint(0, 8), random.randint(0, 8)
            if board[i, j] != 0:
                board[i, j] = 0
                attempts -= 1
        return full_board, board


class GameState:
    """Contiene lo stato della partita corrente."""
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


class Renderer:
    """Gestisce la visualizzazione grafica del gioco."""
    def __init__(self, screen, fonts):
        self.screen = screen
        self.f_big, self.f_med, self.f_small, self.f_note = fonts

    def draw_menu(self, options, current_sel):
        """Disegna il menu principale."""
        self.screen.fill(THEME["bg"])
        title = self.f_big.render("SUDOKU", True, THEME["accent"])
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, 150)))
        for i, opt in enumerate(options):
            sel = i == current_sel
            color = THEME["select"] if sel else THEME["text"]
            text = self.f_med.render(opt, True, color)
            rect = text.get_rect(center=(WIDTH // 2, 350 + i * 80))
            if sel:
                pygame.draw.rect(self.screen, THEME["panel"], rect.inflate(40, 20), border_radius=10)
            self.screen.blit(text, rect)

    def draw_grid(self):
        """Disegna le linee della griglia."""
        for i in range(10):
            thick = 4 if i % 3 == 0 else 1
            pygame.draw.line(self.screen, THEME["grid"], (0, i*CELL_SIZE), (WIDTH, i*CELL_SIZE), thick)
            pygame.draw.line(self.screen, THEME["grid"], (i*CELL_SIZE, 0), (i*CELL_SIZE, WIDTH), thick)

    def _draw_cell_content(self, r, c, state):
        val = state.grid[r, c]
        rect = pygame.Rect(c*CELL_SIZE, r*CELL_SIZE, CELL_SIZE, CELL_SIZE)
        if val != 0:
            color = THEME["fixed"] if state.is_fixed[r, c] else THEME["accent"]
            if val != state.solution[r, c]:
                color = THEME["error"]
            if state.won:
                color = THEME["win"]
            img = self.f_med.render(str(val), True, color)
            self.screen.blit(img, img.get_rect(center=rect.center))
        elif state.notes[r][c]:
            for n in state.notes[r][c]:
                idx = n-1
                nx = c*CELL_SIZE + (idx % 3)*(CELL_SIZE//3) + 8
                ny = r*CELL_SIZE + (idx // 3)*(CELL_SIZE//3) + 4
                img = self.f_note.render(str(n), True, THEME["note"])
                self.screen.blit(img, (nx, ny))

    def draw_game(self, game_state):
        """Renderizza l'intera schermata di gioco."""
        self.screen.fill(THEME["bg"])
        self.draw_grid()
        for r in range(9):
            for c in range(9):
                self._draw_cell_content(r, c, game_state)
        self._draw_footer(game_state)
        if not game_state.won and not game_state.game_over:
            color = THEME["note"] if game_state.note_mode else THEME["select"]
            pygame.draw.rect(self.screen, color, (game_state.selected[1]*CELL_SIZE,
                             game_state.selected[0]*CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)

    def _draw_footer(self, state):
        """Disegna la barra di stato inferiore con vite, modalità e note."""
        footer_y = WIDTH + 10
        
        # 1. Sinistra: Vite
        lives_txt = f"VITE: {'I ' * state.lives}"
        lives_color = THEME["error"] if state.lives == 1 else THEME["text"]
        lives_img = self.f_small.render(lives_txt, True, lives_color)
        self.screen.blit(lives_img, (20, footer_y))

        # 2. Destra: Difficoltà (Modalità)
        diff_txt = f"MODALITÀ: {state.difficulty_label}"
        diff_img = self.f_small.render(diff_txt, True, (150, 150, 150))
        self.screen.blit(diff_img, (WIDTH - diff_img.get_width() - 20, footer_y))

        # 3. Centro: Stato Annotazione
        status_y = footer_y + 45
        status_text = "ATTIVA" if state.note_mode else "DISATTIVATA"
        status_color = THEME["note"] if state.note_mode else (120, 120, 120)
        
        label_surf = self.f_small.render("[A] ANNOTAZIONE:", True, THEME["text"])
        val_surf = self.f_small.render(status_text, True, status_color)
        
        # Calcolo per centrare perfettamente l'insieme dei due testi
        total_w = label_surf.get_width() + val_surf.get_width()
        start_x = (WIDTH - total_w) // 2
        
        self.screen.blit(label_surf, (start_x, status_y))
        self.screen.blit(val_surf, (start_x + label_surf.get_width(), status_y))

        # 4. Messaggi di fine partita (se presenti)
        if state.won or state.game_over:
            msg = "VITTORIA!" if state.won else "GAME OVER!"
            color = THEME["win"] if state.won else THEME["error"]
            end_img = self.f_small.render(f"{msg} ESC per Menu", True, color)
            self.screen.blit(end_img, end_img.get_rect(center=(WIDTH // 2, HEIGHT - 35)))


class SudokuGame:
    """Controller principale del gioco."""
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("SUDOKU")
        fonts = (
            pygame.font.SysFont("Verdana", 40, bold=True),
            pygame.font.SysFont("Verdana", 30, bold=True),
            pygame.font.SysFont("Verdana", 18),
            pygame.font.SysFont("Verdana", 14)
        )
        self.engine = SudokuEngine()
        self.state = GameState()
        self.renderer = Renderer(self.screen, fonts)
        self.state_mode = "MENU"
        self.menu_options = ["FACILE", "MEDIO", "DIFFICILE"]
        self.menu_sel = 1

    def setup_game(self, difficulty):
        """Inizializza una nuova partita."""
        self.state.difficulty_label = difficulty
        self.state.solution, self.state.grid = self.engine.generate_puzzle(difficulty)
        self.state.notes = [[set() for _ in range(9)] for _ in range(9)]
        self.state.is_fixed = self.state.grid != 0
        self.state.lives = 3
        self.state.won = False
        self.state.game_over = False
        self.state_mode = "PLAYING"

    def _handle_menu_events(self, event):
        if event.key == pygame.K_UP:
            self.menu_sel = (self.menu_sel - 1) % 3
        elif event.key == pygame.K_DOWN:
            self.menu_sel = (self.menu_sel + 1) % 3
        elif event.key == pygame.K_RETURN:
            self.setup_game(self.menu_options[self.menu_sel])

    def _handle_play_events(self, event):
        st = self.state
        if event.key == pygame.K_a:
            st.note_mode = not st.note_mode
        elif event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
            self._move_selection(event.key)
        elif pygame.K_1 <= event.key <= pygame.K_9:
            self._input_number(int(event.unicode))
        elif event.key in (pygame.K_BACKSPACE, pygame.K_0):
            r, c = st.selected
            if not st.is_fixed[r, c]:
                st.grid[r, c] = 0
                st.notes[r][c].clear()

    def _move_selection(self, key):
        if key == pygame.K_UP:
            self.state.selected[0] = (self.state.selected[0] - 1) % 9
        elif key == pygame.K_DOWN:
            self.state.selected[0] = (self.state.selected[0] + 1) % 9
        elif key == pygame.K_LEFT:
            self.state.selected[1] = (self.state.selected[1] - 1) % 9
        elif key == pygame.K_RIGHT:
            self.state.selected[1] = (self.state.selected[1] + 1) % 9

    def _input_number(self, val):
        st = self.state
        r, c = st.selected
        if st.is_fixed[r, c] or st.grid[r, c] == val:
            return
        if st.note_mode:
            if val in st.notes[r][c]:
                st.notes[r][c].remove(val)
            else:
                st.notes[r][c].add(val)
        else:
            st.grid[r, c] = val
            st.notes[r][c].clear()
            if val != st.solution[r, c]:
                st.lives -= 1
                if st.lives <= 0:
                    st.game_over = True
            elif np.array_equal(st.grid, st.solution):
                st.won = True

    def run(self):
        """Loop principale del gioco."""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state_mode == "PLAYING":
                            self.state_mode = "MENU"
                        else:
                            # pylint: disable=consider-using-with
                            subprocess.Popen([sys.executable, "main_menu.py"])
                            pygame.quit()
                            sys.exit()
                    elif self.state_mode == "MENU":
                        self._handle_menu_events(event)
                    elif self.state_mode == "PLAYING" and not self.state.game_over:
                        self._handle_play_events(event)
            if self.state_mode == "MENU":
                self.renderer.draw_menu(self.menu_options, self.menu_sel)
            else:
                self.renderer.draw_game(self.state)
            pygame.display.flip()

if __name__ == "__main__":
    SudokuGame().run()