import pygame
import sys

# Colori coerenti con il tuo Menu
BG_COLOR = (30, 35, 45)
GRID_COLOR = (240, 240, 240)
TEXT_COLOR = (255, 255, 255)
ACCENT_COLOR = (0, 200, 255)
FIXED_NUM_COLOR = (150, 150, 150)

WIDTH, HEIGHT = 600, 650
GRID_SIZE = 9
CELL_SIZE = 600 // GRID_SIZE

class Sudoku:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("SUDOKU - Offline Games")
        self.font = pygame.font.SysFont("Verdana", 35)
        self.small_font = pygame.font.SysFont("Verdana", 18)
        
        # 0 rappresenta cella vuota. I numeri non zero sono "fissi".
        self.grid = [
            [5, 3, 0, 0, 7, 0, 0, 0, 0],
            [6, 0, 0, 1, 9, 5, 0, 0, 0],
            [0, 9, 8, 0, 0, 0, 0, 6, 0],
            [8, 0, 0, 0, 6, 0, 0, 0, 3],
            [4, 0, 0, 8, 0, 3, 0, 0, 1],
            [7, 0, 0, 0, 2, 0, 0, 0, 6],
            [0, 6, 0, 0, 0, 0, 2, 8, 0],
            [0, 0, 0, 4, 1, 9, 0, 0, 5],
            [0, 0, 0, 0, 8, 0, 0, 7, 9]
        ]
        # Teniamo traccia di quali numeri erano originali (non modificabili)
        self.original_grid = [[self.grid[y][x] != 0 for x in range(9)] for y in range(9)]
        self.selected = (0, 0)

    def draw_grid(self):
        self.screen.fill(BG_COLOR)
        for i in range(GRID_SIZE + 1):
            thickness = 4 if i % 3 == 0 else 1
            # Linee orizzontali
            pygame.draw.line(self.screen, GRID_COLOR, (0, i * CELL_SIZE), (600, i * CELL_SIZE), thickness)
            # Linee verticali
            pygame.draw.line(self.screen, GRID_COLOR, (i * CELL_SIZE, 0), (i * CELL_SIZE, 600), thickness)

    def draw_numbers(self):
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                val = self.grid[y][x]
                if val != 0:
                    color = FIXED_NUM_COLOR if self.original_grid[y][x] else ACCENT_COLOR
                    text = self.font.render(str(val), True, color)
                    self.screen.blit(text, (x * CELL_SIZE + 20, y * CELL_SIZE + 10))

    def draw_selection(self):
        x, y = self.selected
        pygame.draw.rect(self.screen, (255, 170, 0), (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    x, y = self.selected
                    if event.key == pygame.K_UP: self.selected = (x, (y - 1) % 9)
                    if event.key == pygame.K_DOWN: self.selected = (x, (y + 1) % 9)
                    if event.key == pygame.K_LEFT: self.selected = ((x - 1) % 9, y)
                    if event.key == pygame.K_RIGHT: self.selected = ((x + 1) % 9, y)
                    
                    # Inserimento numeri (solo se la cella non è originale)
                    if not self.original_grid[y][x]:
                        if pygame.K_1 <= event.key <= pygame.K_9:
                            self.grid[y][x] = int(event.unicode)
                        if event.key == pygame.K_BACKSPACE or event.key == pygame.K_0:
                            self.grid[y][x] = 0

            self.draw_grid()
            self.draw_selection()
            self.draw_numbers()
            
            info = self.small_font.render("Frecce per muoverti • Numeri per inserire • Backspace per cancellare", True, (200, 200, 200))
            self.screen.blit(info, (20, 615))
            
            pygame.display.flip()

if __name__ == "__main__":
    Sudoku().run()