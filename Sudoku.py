import pygame
import sys
import numpy as np
import random
import subprocess
from pygame.locals import *

# --- CONFIGURAZIONE ESTETICA ---
THEME = {
    "bg": (30, 35, 45),
    "grid": (240, 240, 240),
    "text": (255, 255, 255),
    "accent": (0, 180, 255),      # Numeri Corretti
    "fixed": (150, 150, 150),     # Numeri Iniziali
    "error": (255, 80, 80),       # Numeri Sbagliati
    "select": (255, 170, 0),      # Cursore Normale
    "note": (255, 255, 100),      # Cursore Annotazione / Note
    "win": (50, 255, 50),
    "panel": (40, 45, 60)
}

WIDTH, HEIGHT = 600, 780 
GRID_SIZE = 9
CELL_SIZE = WIDTH // GRID_SIZE

class SudokuEngine:
    @staticmethod
    def find_empty(board):
        for i in range(9):
            for j in range(9):
                if board[i, j] == 0: return (i, j)
        return None

    @staticmethod
    def is_valid(board, row, col, num):
        if num in board[row, :] or num in board[:, col]: return False
        r_start, c_start = (row // 3) * 3, (col // 3) * 3
        if num in board[r_start:r_start+3, c_start:c_start+3]: return False
        return True

    def solve(self, board):
        empty = self.find_empty(board)
        if not empty: return True
        row, col = empty
        for i in np.random.permutation(range(1, 10)):
            if self.is_valid(board, row, col, i):
                board[row, col] = i
                if self.solve(board): return True
                board[row, col] = 0
        return False

    def generate_puzzle(self, difficulty):
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

class SudokuGame:
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

    def setup_game(self, difficulty):
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
        self.screen.fill(THEME["bg"])
        title = self.font_big.render("SUDOKU", True, THEME["accent"])
        self.screen.blit(title, title.get_rect(center=(WIDTH//2, 150)))
        for i, opt in enumerate(self.menu_options):
            is_selected = (i == self.menu_sel)
            color = THEME["select"] if is_selected else THEME["text"]
            text_surf = self.font_med.render(opt, True, color)
            text_rect = text_surf.get_rect(center=(WIDTH // 2, 350 + i * 80))
            if is_selected:
                bg_rect = text_rect.inflate(40, 20)
                pygame.draw.rect(self.screen, THEME["panel"], bg_rect, border_radius=10)
                self.screen.blit(self.font_med.render("> ", True, color), self.font_med.render("> ", True, color).get_rect(midright=(bg_rect.left - 10, bg_rect.centery)))
                self.screen.blit(self.font_med.render(" <", True, color), self.font_med.render(" <", True, color).get_rect(midleft=(bg_rect.right + 10, bg_rect.centery)))
            self.screen.blit(text_surf, text_rect)

    def draw_game(self):
        self.screen.fill(THEME["bg"])
        
        # UI Superiore (Vite e Difficoltà)
        lives_img = self.font_small.render(f"VITE: {'I ' * self.lives}", True, THEME["error"] if self.lives == 1 else THEME["text"])
        self.screen.blit(lives_img, (20, WIDTH + 10))
        diff_img = self.font_small.render(f"MODALITÀ: {self.difficulty_label}", True, (150, 150, 150))
        self.screen.blit(diff_img, (WIDTH - diff_img.get_width() - 20, WIDTH + 10))
        
        # Griglia
        for i in range(10):
            thick = 4 if i % 3 == 0 else 1
            pygame.draw.line(self.screen, THEME["grid"], (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE), thick)
            pygame.draw.line(self.screen, THEME["grid"], (i * CELL_SIZE, 0), (i * CELL_SIZE, WIDTH), thick)
        
        # Numeri e Note
        for r in range(9):
            for c in range(9):
                val = self.grid[r, c]
                cell_rect = pygame.Rect(c*CELL_SIZE, r*CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if val != 0:
                    if self.is_fixed[r, c]: color = THEME["fixed"]
                    elif val == self.solution[r, c]: color = THEME["accent"]
                    else: color = THEME["error"]
                    if self.won: color = THEME["win"]
                    img = self.font_med.render(str(val), True, color)
                    self.screen.blit(img, img.get_rect(center=cell_rect.center))
                elif self.notes[r][c]:
                    for n in self.notes[r][c]:
                        idx = n - 1
                        nx = c * CELL_SIZE + (idx % 3) * (CELL_SIZE // 3) + 8
                        ny = r * CELL_SIZE + (idx // 3) * (CELL_SIZE // 3) + 4
                        self.screen.blit(self.font_note.render(str(n), True, THEME["note"]), (nx, ny))

        # --- FOOTER CENTRALE ---
        footer_y = WIDTH + 55
        note_label = "[A] ANNOTAZIONE: "
        status_str = "ATTIVA" if self.note_mode else "DISATTIVATA"
        status_color = THEME["note"] if self.note_mode else (120, 120, 120)
        
        label_surf = self.font_small.render(note_label, True, THEME["text"])
        status_surf = self.font_small.render(status_str, True, status_color)
        
        total_w = label_surf.get_width() + status_surf.get_width()
        start_x = (WIDTH - total_w) // 2
        self.screen.blit(label_surf, (start_x, footer_y - 10))
        self.screen.blit(status_surf, (start_x + label_surf.get_width(), footer_y - 10))

        if self.won or self.game_over:
            end_msg = "VITTORIA! ESC per Menu" if self.won else "GAME OVER! ESC per Menu"
            end_img = self.font_small.render(end_msg, True, THEME["win"] if self.won else THEME["error"])
            self.screen.blit(end_img, end_img.get_rect(center=(WIDTH//2, footer_y + 25)))

        if not self.won and not self.game_over:
            sel_color = THEME["note"] if self.note_mode else THEME["select"]
            pygame.draw.rect(self.screen, sel_color, (self.selected[1]*CELL_SIZE, self.selected[0]*CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)

    def handle_input(self, val):
        r, c = self.selected
        if self.is_fixed[r, c]: return
        
        # --- FIX: Se il numero inserito è già quello nella cella, non fare nulla ---
        if self.grid[r, c] == val:
            return

        if self.note_mode:
            if val in self.notes[r][c]: self.notes[r][c].remove(val)
            else: self.notes[r][c].add(val)
        else:
            self.grid[r, c] = val
            self.notes[r][c].clear()
            if val != self.solution[r, c]:
                self.lives -= 1
                if self.lives <= 0: self.game_over = True
            elif np.array_equal(self.grid, self.solution):
                self.won = True

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == QUIT: pygame.quit(); sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        if self.state == "PLAYING": self.state = "MENU"
                        else: subprocess.Popen([sys.executable, "MainMenu.py"]); pygame.quit(); sys.exit()
                    if self.state == "MENU":
                        if event.key == K_UP: self.menu_sel = (self.menu_sel - 1) % 3
                        if event.key == K_DOWN: self.menu_sel = (self.menu_sel + 1) % 3
                        if event.key == K_RETURN: self.setup_game(self.menu_options[self.menu_sel])
                    elif self.state == "PLAYING" and not self.won and not self.game_over:
                        if event.key == K_a: self.note_mode = not self.note_mode
                        if event.key == K_UP: self.selected[0] = (self.selected[0] - 1) % 9
                        if event.key == K_DOWN: self.selected[0] = (self.selected[0] + 1) % 9
                        if event.key == K_LEFT: self.selected[1] = (self.selected[1] - 1) % 9
                        if event.key == K_RIGHT: self.selected[1] = (self.selected[1] + 1) % 9
                        if K_1 <= event.key <= K_9: self.handle_input(int(event.unicode))
                        if event.key in [K_BACKSPACE, K_0]:
                            if not self.is_fixed[self.selected[0], self.selected[1]]:
                                self.grid[self.selected[0], self.selected[1]] = 0
                                self.notes[self.selected[0]][self.selected[1]].clear()
            self.draw_menu() if self.state == "MENU" else self.draw_game()
            pygame.display.flip()

if __name__ == "__main__":
    SudokuGame().run()