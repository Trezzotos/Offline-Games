import os
import subprocess
import sys

import pygame
from pygame.locals import *

# --- CONFIGURAZIONE ESTETICA ---
SCREEN_SIZE = (700, 700)
THEME = {
    "background": (25, 25, 35),
    "panel": (15, 15, 20),
    "text_main": (235, 235, 235),
    "accent": (0, 180, 255),
    "selection": (255, 160, 0),
    "footer": (120, 120, 130),
}


class OfflineGames:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption("MULTIGAME DASHBOARD")

        # Inizializzazione Font
        self.font_header = pygame.font.SysFont("Segoe UI", 55, bold=True)
        self.font_button = pygame.font.SysFont("Segoe UI", 32, bold=True)
        self.font_help = pygame.font.SysFont("Segoe UI", 18, italic=True)

        # Mappatura Giochi: Nome visualizzato -> Nome File
        self.catalog = [
            {"label": "SUDOKU", "file": "Sudoku.py"},
            {"label": "BATTAGLIA NAVALE", "file": "BattagliaNavale.py"},
        ]
        self.pointer = 0

    def _render_frame(self):
        # Pannello centrale decorativo
        margin = 60
        rect_width = SCREEN_SIZE[0] - (margin * 2)
        rect_height = SCREEN_SIZE[1] - (margin * 2)
        pygame.draw.rect(
            self.window,
            THEME["panel"],
            (margin, margin, rect_width, rect_height),
            border_radius=30,
        )

        # Header
        title_img = self.font_header.render(
            "Offline Games Menu", True, THEME["text_main"]
        )
        title_pos = title_img.get_rect(center=(SCREEN_SIZE[0] // 2, 160))

        # Sottolineatura stilizzata
        line_y = 200
        pygame.draw.line(self.window, THEME["accent"], (250, line_y), (450, line_y), 3)
        self.window.blit(title_img, title_pos)

    def refresh_ui(self):
        """Aggiorna l'intero contenuto della finestra con il fix del testo centrato."""
        self.window.fill(THEME["background"])
        self._render_frame()

        for idx, item in enumerate(self.catalog):
            is_active = idx == self.pointer
            label_color = THEME["selection"] if is_active else THEME["text_main"]

            # 1. Renderizziamo solo il testo del gioco (es. "SUDOKU")
            # In questo modo il centro del testo è il centro dello schermo
            label_surf = self.font_button.render(item["label"], True, label_color)
            label_rect = label_surf.get_rect(
                center=(SCREEN_SIZE[0] // 2, 350 + idx * 110)
            )

            if is_active:
                # 2. Creiamo il rettangolo di evidenziazione basato solo sul testo
                glow_rect = label_rect.inflate(50, 25)
                pygame.draw.rect(self.window, (40, 45, 60), glow_rect, border_radius=15)

                # 3. Disegniamo le frecce esternamente al rettangolo "glow"
                arrow_l = self.font_button.render("> ", True, THEME["selection"])
                arrow_r = self.font_button.render(" <", True, THEME["selection"])

                # Posizioniamo le frecce a sinistra e destra del rettangolo grigio
                l_pos = arrow_l.get_rect(
                    midright=(glow_rect.left - 15, glow_rect.centery)
                )
                r_pos = arrow_r.get_rect(
                    midleft=(glow_rect.right + 15, glow_rect.centery)
                )

                self.window.blit(arrow_l, l_pos)
                self.window.blit(arrow_r, r_pos)

            # 4. Infine scriviamo il testo (rimarrà sempre perfettamente al centro)
            self.window.blit(label_surf, label_rect)

        # Footer informativo
        hint = self.font_help.render(
            "Naviga con ↑↓ • Conferma con INVIO", True, THEME["footer"]
        )
        self.window.blit(hint, hint.get_rect(center=(SCREEN_SIZE[0] // 2, 620)))

        pygame.display.flip()

    def boot_selected_game(self):
        """Esegue il file associato alla selezione attuale."""
        target_script = self.catalog[self.pointer]["file"]
        try:
            subprocess.Popen([sys.executable, target_script])
            self.shutdown()
        except Exception as e:
            print(f"Errore nell'avvio di {target_script}: {e}")

    def shutdown(self):
        """Chiusura pulita dell'applicazione."""
        pygame.quit()
        sys.exit()

    def start_engine(self):
        """Ciclo principale dell'applicazione."""
        clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.shutdown()

                if event.type == KEYDOWN:
                    if event.key == K_UP:
                        self.pointer = (self.pointer - 1) % len(self.catalog)
                    elif event.key == K_DOWN:
                        self.pointer = (self.pointer + 1) % len(self.catalog)
                    elif event.key == K_RETURN:
                        self.boot_selected_game()
                    elif event.key == K_ESCAPE:
                        self.shutdown()

            self.refresh_ui()
            clock.tick(60)


if __name__ == "__main__":
    app = OfflineGames()
    app.start_engine()
