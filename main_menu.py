# pylint: disable=no-member
"""
Main menu grafico per avviare giochi offline.
Dashboard sviluppata con pygame che permette di
selezionare e avviare diversi giochi Python.
"""

import os
import subprocess
import sys
from typing import List, Dict

import pygame

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
    """Dashboard grafica per selezionare e avviare giochi offline."""

    def __init__(self) -> None:
        pygame.init()

        self.window = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption("MULTIGAME DASHBOARD")

        self.font_header = pygame.font.SysFont("Segoe UI", 55, bold=True)
        self.font_button = pygame.font.SysFont("Segoe UI", 32, bold=True)
        self.font_help = pygame.font.SysFont("Segoe UI", 18, italic=True)

        # catalogo giochi
        self.catalog: List[Dict[str, str]] = [
            {"label": "SUDOKU", "file": "sudoku/Sudoku.py"},
            {
                "label": "BATTAGLIA NAVALE",
                "file": "battaglia_navale/BattagliaNavale.py",
            },
        ]

        # directory del progetto
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.pointer = 0

    def _render_frame(self) -> None:
        """Disegna il pannello centrale e il titolo."""
        margin = 60
        rect_width = SCREEN_SIZE[0] - margin * 2
        rect_height = SCREEN_SIZE[1] - margin * 2

        pygame.draw.rect(
            self.window,
            THEME["panel"],
            (margin, margin, rect_width, rect_height),
            border_radius=30,
        )

        title_img = self.font_header.render(
            "Offline Games Menu", True, THEME["text_main"]
        )
        title_pos = title_img.get_rect(center=(SCREEN_SIZE[0] // 2, 160))

        pygame.draw.line(
            self.window,
            THEME["accent"],
            (250, 200),
            (450, 200),
            3,
        )
        self.window.blit(title_img, title_pos)

    def refresh_ui(self) -> None:
        """Aggiorna la UI."""
        self.window.fill(THEME["background"])
        self._render_frame()

        for idx, item in enumerate(self.catalog):
            is_active = idx == self.pointer
            color = THEME["selection"] if is_active else THEME["text_main"]
            label = self.font_button.render(item["label"], True, color)
            label_rect = label.get_rect(center=(SCREEN_SIZE[0] // 2, 350 + idx * 110))

            if is_active:
                glow_rect = label_rect.inflate(50, 25)
                pygame.draw.rect(
                    self.window,
                    (40, 45, 60),
                    glow_rect,
                    border_radius=15,
                )
                arrow_l = self.font_button.render("> ", True, THEME["selection"])
                arrow_r = self.font_button.render(" <", True, THEME["selection"])
                l_pos = arrow_l.get_rect(
                    midright=(glow_rect.left - 15, glow_rect.centery)
                )
                r_pos = arrow_r.get_rect(
                    midleft=(glow_rect.right + 15, glow_rect.centery)
                )
                self.window.blit(arrow_l, l_pos)
                self.window.blit(arrow_r, r_pos)

            self.window.blit(label, label_rect)

        hint = self.font_help.render(
            "Naviga con ↑↓ • Conferma con INVIO", True, THEME["footer"]
        )
        self.window.blit(hint, hint.get_rect(center=(SCREEN_SIZE[0] // 2, 620)))
        pygame.display.flip()

    def boot_selected_game(self) -> None:
        """Avvia il gioco selezionato."""
        target_script = self.catalog[self.pointer]["file"]
        full_path = os.path.join(self.base_dir, target_script)

        try:
            # pylint: disable=consider-using-with
            subprocess.Popen([sys.executable, full_path], start_new_session=True)
            self.shutdown()
        except (OSError, subprocess.SubprocessError) as error:
            print(f"Errore nell'avvio di {full_path}: {error}")

    def shutdown(self) -> None:
        """Chiude l'applicazione."""
        pygame.quit()
        sys.exit()

    def start_engine(self) -> None:
        """Loop principale."""
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.shutdown()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.pointer = (self.pointer - 1) % len(self.catalog)
                    elif event.key == pygame.K_DOWN:
                        self.pointer = (self.pointer + 1) % len(self.catalog)
                    elif event.key == pygame.K_RETURN:
                        self.boot_selected_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.shutdown()

            self.refresh_ui()
            clock.tick(60)


if __name__ == "__main__":
    app = OfflineGames()
    app.start_engine()
