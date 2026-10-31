"""Rendering del menu principale."""

from __future__ import annotations

import pygame

from menu.catalog import GameEntry

SCREEN_SIZE = (700, 700)

THEME = {
    "background": (25, 25, 35),
    "panel": (15, 15, 20),
    "text_main": (235, 235, 235),
    "accent": (0, 180, 255),
    "selection": (255, 160, 0),
    "footer": (120, 120, 130),
    "highlight": (40, 45, 60),
}

PANEL_MARGIN = 60
CENTER_X = SCREEN_SIZE[0] // 2


class MenuView:
    """Disegna il pannello del menu."""

    def __init__(self, window: pygame.Surface) -> None:
        self.window = window
        self.font_header = pygame.font.SysFont("Segoe UI", 55, bold=True)
        self.font_button = pygame.font.SysFont("Segoe UI", 32, bold=True)
        self.font_help = pygame.font.SysFont("Segoe UI", 18, italic=True)

    def draw(self, catalog: tuple[GameEntry, ...], pointer: int) -> None:
        """Disegna un frame completo e lo mostra a schermo."""
        self.window.fill(THEME["background"])
        self._draw_frame()
        for idx, entry in enumerate(catalog):
            self._draw_entry(entry.label, idx, idx == pointer)
        hint = self.font_help.render(
            "UP/DOWN to select - ENTER to confirm", True, THEME["footer"]
        )
        self.window.blit(hint, hint.get_rect(center=(CENTER_X, 620)))
        pygame.display.flip()

    def _draw_frame(self) -> None:
        size = (SCREEN_SIZE[0] - PANEL_MARGIN * 2, SCREEN_SIZE[1] - PANEL_MARGIN * 2)
        pygame.draw.rect(
            self.window,
            THEME["panel"],
            (PANEL_MARGIN, PANEL_MARGIN, *size),
            border_radius=30,
        )
        title = self.font_header.render("Offline Games Menu", True, THEME["text_main"])
        pygame.draw.line(self.window, THEME["accent"], (250, 200), (450, 200), 3)
        self.window.blit(title, title.get_rect(center=(CENTER_X, 160)))

    def _draw_entry(self, text: str, idx: int, active: bool) -> None:
        color = THEME["selection"] if active else THEME["text_main"]
        label = self.font_button.render(text, True, color)
        label_rect = label.get_rect(center=(CENTER_X, 350 + idx * 110))
        if active:
            self._draw_highlight(label_rect)
        self.window.blit(label, label_rect)

    def _draw_highlight(self, label_rect: pygame.Rect) -> None:
        glow = label_rect.inflate(50, 25)
        pygame.draw.rect(self.window, THEME["highlight"], glow, border_radius=15)
        arrow_l = self.font_button.render("> ", True, THEME["selection"])
        arrow_r = self.font_button.render(" <", True, THEME["selection"])
        self.window.blit(
            arrow_l, arrow_l.get_rect(midright=(glow.left - 15, glow.centery))
        )
        self.window.blit(
            arrow_r, arrow_r.get_rect(midleft=(glow.right + 15, glow.centery))
        )
