"""Costanti di configurazione del Sudoku."""

from __future__ import annotations

WIDTH = 600
HEIGHT = 780
GRID_SIZE = 9
BOX_SIZE = 3
CELL_SIZE = WIDTH // GRID_SIZE
INITIAL_LIVES = 3

DIFFICULTIES: dict[str, int] = {"EASY": 30, "MEDIUM": 45, "HARD": 60}
DEFAULT_REMOVED_CELLS = 45

Color = tuple[int, int, int]

THEME: dict[str, Color] = {
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
