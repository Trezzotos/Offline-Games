"""Rendering di una singola plancia e conversione pixel <-> coordinate."""

from __future__ import annotations

import pygame

from battleship_game import config
from battleship_game.config import Coord
from battleship_game.model import Board

MARKER_MARGIN = 6


class BoardView:
    """Disegna una plancia in una posizione dello schermo."""

    def __init__(self, origin: Coord, cell_size: int = config.CELL_SIZE) -> None:
        self.origin = origin
        self.cell_size = cell_size

    def pixel_size(self, board: Board) -> tuple[int, int]:
        """Dimensioni in pixel della plancia."""
        return board.columns * self.cell_size, board.rows * self.cell_size

    def rect(self, board: Board) -> pygame.Rect:
        """Rettangolo occupato dalla plancia sullo schermo."""
        return pygame.Rect(self.origin, self.pixel_size(board))

    def locate(self, board: Board, pos: Coord) -> Coord | None:
        """Converte una posizione in pixel in (riga, colonna), se sulla plancia."""
        if not self.rect(board).collidepoint(pos):
            return None
        col = (pos[0] - self.origin[0]) // self.cell_size
        row = (pos[1] - self.origin[1]) // self.cell_size
        return row, col

    def cell_rect(self, row: int, col: int) -> pygame.Rect:
        """Rettangolo in pixel di una cella."""
        return pygame.Rect(
            self.origin[0] + col * self.cell_size,
            self.origin[1] + row * self.cell_size,
            self.cell_size,
            self.cell_size,
        )

    def draw(self, surface: pygame.Surface, board: Board, reveal_ships: bool) -> None:
        """Disegna celle, navi (se visibili) e segnalini dei colpi."""
        for row in range(board.rows):
            for col in range(board.columns):
                self._draw_cell(surface, board, row, col, reveal_ships)

    def draw_dim_overlay(self, surface: pygame.Surface, board: Board) -> None:
        """Oscura la plancia non attiva."""
        overlay = pygame.Surface(self.pixel_size(board), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        surface.blit(overlay, self.origin)

    def draw_ship_preview(
        self, surface: pygame.Surface, cells: list[Coord], valid: bool
    ) -> None:
        """Disegna l'anteprima di posizionamento della nave."""
        if not cells:
            return
        fill = config.PREVIEW_VALID_COLOR if valid else config.PREVIEW_INVALID_COLOR
        border = config.PREVIEW_VALID_BORDER if valid else config.PREVIEW_INVALID_BORDER
        tile = pygame.Surface((self.cell_size - 2, self.cell_size - 2), pygame.SRCALPHA)
        tile.fill(fill)
        for row, col in cells:
            rect = self.cell_rect(row, col)
            surface.blit(tile, (rect.x + 1, rect.y + 1))
            pygame.draw.rect(surface, border, rect, 2)

    def _draw_cell(
        self,
        surface: pygame.Surface,
        board: Board,
        row: int,
        col: int,
        reveal_ships: bool,
    ) -> None:
        cell = board.cell(row, col)
        rect = self.cell_rect(row, col)
        if cell.is_hit:
            color = config.LIGHT_GRAY
        elif cell.has_ship and reveal_ships:
            color = config.SHIPS_COLOR
        else:
            color = config.BLUE
        inner = pygame.Rect(rect.x + 1, rect.y + 1, rect.w - 2, rect.h - 2)
        pygame.draw.rect(surface, color, inner)
        pygame.draw.rect(surface, config.BLUE_GRID_MARGIN, rect, 1)
        if cell.is_hit:
            self._draw_marker(surface, rect, cell.has_ship)

    @staticmethod
    def _draw_marker(surface: pygame.Surface, rect: pygame.Rect, is_ship: bool) -> None:
        if is_ship:
            m = MARKER_MARGIN
            pygame.draw.line(
                surface,
                config.RED,
                (rect.left + m, rect.top + m),
                (rect.right - m, rect.bottom - m),
                3,
            )
            pygame.draw.line(
                surface,
                config.RED,
                (rect.right - m, rect.top + m),
                (rect.left + m, rect.bottom - m),
                3,
            )
        else:
            pygame.draw.circle(surface, config.WHITE, rect.center, rect.w // 4, 3)
