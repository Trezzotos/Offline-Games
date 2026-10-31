"""Costanti e parametri di configurazione di Battleship."""

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
WIDTH = 800
HEIGHT = WIDTH + 100
CELL_SIZE = 40
ENEMY_GRID_ORIGIN: Coord = (WIDTH // 4, 10)
PLAYER_GRID_ORIGIN: Coord = (WIDTH // 4, HEIGHT // 2 + 40)

RESTART_BUTTON = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 60)
HELP_BUTTON = pygame.Rect(WIDTH - 160, HEIGHT // 2 - 30, 130, 60)
CLOSE_INSTRUCTIONS_BUTTON = pygame.Rect(WIDTH - 60, 20, 40, 40)

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
    "SHIP PLACEMENT",
    "- Left click: place the ship.",
    "- Right click: rotate the ship.",
    "- Green = valid position.",
    "- Red = invalid position.",
    "",
    "ATTACK",
    "- Click on the enemy grid to shoot.",
    "- Red X = hit.",
    "- White circle = miss.",
    "",
    "PAUSE / HELP",
    "- Press Help to pause the game.",
    "- Press the X in the top-right corner to resume.",
)


@dataclass(frozen=True)
class FontSpec:
    """Dimensioni dei font usati dall'interfaccia."""

    ship: int = 30
    title: int = 80
    big: int = 60
    button: int = 40
    small: int = 26
