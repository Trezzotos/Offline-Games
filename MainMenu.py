import pygame
from pygame.locals import *
import sys
import subprocess

# ----------------------------
# Costanti grafiche (Colori più sobri ed eleganti)
# ----------------------------
WINDOW_WIDTH, WINDOW_HEIGHT = 700, 700
BG_COLOR = (30, 35, 45)       # Blu notte scuro
PRIMARY_COLOR = (240, 240, 240)  # Bianco avorio
ACCENT_COLOR = (0, 200, 255)     # Azzurro brillante
HIGHLIGHT_COLOR = (255, 170, 0)  # Arancio (per la selezione)
DARK_GRAY = (20, 20, 20)

class OfflineGamesMenu:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("OFFLINE GAMES HUB")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()

        # Font (Utilizzo font di sistema standard per pulizia, o caricali se li hai)
        self.title_font = pygame.font.SysFont("Verdana", 50, bold=True)
        self.menu_font = pygame.font.SysFont("Verdana", 30, bold=True)
        self.info_font = pygame.font.SysFont("Verdana", 18)

        # Nuove Opzioni
        self.options = ["SUDOKU", "BATTAGLIA NAVALE"]
        self.selected = 0

    # ------------------------
    # Interfaccia grafica moderna
    # ------------------------
    def draw_interface(self):
        s = self.screen
        w, h = WINDOW_WIDTH, WINDOW_HEIGHT

        # Sfondo con sfumatura semplice (rettangolo decorativo)
        pygame.draw.rect(s, DARK_GRAY, (50, 50, w-100, h-100), border_radius=20)
        
        # Titolo "Offline Games"
        title_surf = self.title_font.render("Offline Games", True, PRIMARY_COLOR)
        title_rect = title_surf.get_rect(center=(w // 2, 150))
        
        # Linea decorativa sotto il titolo
        pygame.draw.line(s, ACCENT_COLOR, (200, 190), (500, 190), 4)
        s.blit(title_surf, title_rect)

    # ------------------------
    # Disegna il menu
    # ------------------------
    def draw_menu(self):
        self.screen.fill(BG_COLOR)
        self.draw_interface()

        for i, option in enumerate(self.options):
            # Cambia colore e aggiunge un indicatore se selezionato
            if i == self.selected:
                color = HIGHLIGHT_COLOR
                prefix = "> "
            else:
                color = PRIMARY_COLOR
                prefix = "  "
            
            text = self.menu_font.render(f"{prefix}{option}", True, color)
            rect = text.get_rect(center=(WINDOW_WIDTH // 2, 320 + i * 100))
            
            # Effetto hover (opzionale: rettangolo dietro la selezione)
            if i == self.selected:
                bg_rect = rect.inflate(40, 20)
                pygame.draw.rect(self.screen, (50, 50, 60), bg_rect, border_radius=10)
            
            self.screen.blit(text, rect)

        # Istruzioni in basso
        info = self.info_font.render(
            "Usa le frecce per scegliere • INVIO per giocare", True, (150, 150, 150)
        )
        self.screen.blit(info, info.get_rect(center=(WINDOW_WIDTH // 2, 600)))

        pygame.display.flip()

    def launch_game(self):
        # Assicurati che i nomi dei file siano corretti
        if self.selected == 0:
            # Lancia Sudoku
            subprocess.Popen([sys.executable, "Sudoku.py"])
        elif self.selected == 1:
            # Lancia Battaglia Navale
            subprocess.Popen([sys.executable, "BattagliaNavale.py"])
        
        pygame.quit()
        sys.exit()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == KEYDOWN:
                    if event.key == K_UP:
                        self.selected = (self.selected - 1) % len(self.options)
                    elif event.key == K_DOWN:
                        self.selected = (self.selected + 1) % len(self.options)
                    elif event.key == K_RETURN:
                        self.launch_game()

            self.draw_menu()
            self.clock.tick(30)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    OfflineGamesMenu().run()