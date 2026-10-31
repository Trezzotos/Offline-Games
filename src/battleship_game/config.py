"""Costanti e parametri di configurazione di Battleship."""

from __future__ import annotations

from dataclasses import dataclass

import pygame

Color = tuple[int, int, int]
Coord = tuple[int, int]

# --- Regole di gioco ---------------------------------------------------------
GRID_ROWS = 10
GRID_COLUMNS = 10
FLEET_SIZES: tuple[int, ...] = (2, 2, 3, 4, 5)
SHIP_NAMES: dict[int, str] = {
    2: "Destroyer",
    3: "Cruiser",
    4: "Submarine",
    5: "Carrier",
}
INVALID_SHIP_NAME = "invalid_name"
MAX_PLACEMENT_ATTEMPTS = 100
ENEMY_ATTACK_DELAY_MS = 1000
FPS = 60

# --- Geometria ---------------------------------------------------------------
WIDTH = 550
HEIGHT = 600
CELL_SIZE = 24
_GRID_W = GRID_COLUMNS * CELL_SIZE
_GRID_X = (WIDTH - _GRID_W) // 2

ENEMY_GRID_ORIGIN: Coord = (_GRID_X, 20)
PLAYER_GRID_ORIGIN: Coord = (_GRID_X, 335)

STATUS_BAR_Y = 275
DIVIDER_Y = 300

RESTART_BUTTON = pygame.Rect(WIDTH // 2 - 80, HEIGHT // 2 + 20, 160, 50)
HELP_BUTTON = pygame.Rect(WIDTH - 120, STATUS_BAR_Y - 18, 100, 36)
CLOSE_INSTRUCTIONS_BUTTON = pygame.Rect(WIDTH - 55, 15, 36, 36)

# --- Testi di turno ----------------------------------------------------------
TURN_YOUR_TEXT = "Your turn"
TURN_AI_TEXT = "Waiting for AI..."
TURN_YOUR_COLOR: Color = (0, 230, 100)
TURN_AI_COLOR: Color = (255, 200, 50)

ESC_HINT_TEXT = "ESC for Main Menu"
ESC_HINT_COLOR: Color = (120, 120, 130)
ESC_HINT_Y = HEIGHT - 12

# --- Colori ------------------------------------------------------------------
BACKGROUND_COLOR: Color = (0, 20, 50)
BLUE: Color = (0, 75, 150)
BLUE_GRID_MARGIN: Color = (0, 40, 100)
SHIPS_COLOR: Color = (125, 125, 125)
PREVIEW_VALID_COLOR = (0, 255, 100, 120)
PREVIEW_INVALID_COLOR = (255, 60, 60, 120)
PREVIEW_VALID_BORDER: Color = (0, 255, 120)
PREVIEW_INVALID_BORDER: Color = (255, 80, 80)
WHITE: Color = (255, 255, 255)
BLACK: Color = (0, 0, 0)
LIGHT_GRAY: Color = (200, 200, 200)
RED: Color = (255, 0, 0)
DARK_PANEL: Color = (25, 35, 55)
BUTTON_BLUE: Color = (40, 90, 170)
BUTTON_RED: Color = (170, 40, 40)
BUTTON_GREEN: Color = (0, 180, 0)

INSTRUCTION_LINES: tuple[str, ...] = (
    "PLACEMENT",
    "  Left click: place  |  Right click: rotate",
    "  Green = valid  |  Red = invalid",
    "",
    "ATTACK",
    "  Click the enemy grid to shoot",
    "  Red X = hit  |  White circle = miss",
    "",
    "OTHER",
    "  Help = pause  |  ESC = back to menu",
)


@dataclass(frozen=True)
class FontSpec:
    """Dimensioni dei font usati dall'interfaccia."""

    ship: int = 26
    title: int = 48
    big: int = 40
    button: int = 28
    small: int = 20
