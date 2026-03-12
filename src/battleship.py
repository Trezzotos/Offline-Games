"""Simple Battleship game built with Pygame."""

# pylint: disable=no-member,global-statement,too-few-public-methods,\
# pylint: disable=too-many-branches,too-many-locals,too-many-statements,\
# pylint: disable=redefined-outer-name,invalid-name,consider-using-enumerate,\
# pylint: disable=line-too-long, missing-final-newline
import random

import pygame

pygame.init()

WIDTH = 800
HEIGHT = WIDTH + 100

BACKGROUND_COLOR = (0, 20, 50)
BLUE = (0, 75, 150)
BLUE_GIRD_MARGIN = (0, 40, 100)
SHIPS_COLOR = (125, 125, 125)

PREVIEW_VALID_COLOR = (0, 255, 100, 120)
PREVIEW_INVALID_COLOR = (255, 60, 60, 120)
PREVIEW_VALID_BORDER = (0, 255, 120)
PREVIEW_INVALID_BORDER = (255, 80, 80)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (200, 200, 200)
RED = (255, 0, 0)
DARK_PANEL = (25, 35, 55)
BUTTON_BLUE = (40, 90, 170)
BUTTON_RED = (170, 40, 40)

game_over = False
winner_text = ""
show_instructions = False

font_ship = pygame.font.SysFont(None, 30)
font_title = pygame.font.SysFont(None, 80)
font_big = pygame.font.SysFont(None, 60)
font_button = pygame.font.SysFont(None, 40)
font_small = pygame.font.SysFont(None, 26)

restart_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 60)
help_button = pygame.Rect(WIDTH - 160, HEIGHT // 2 - 30, 130, 60)
close_instructions_button = pygame.Rect(WIDTH - 60, 20, 40, 40)

display = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Battleship")
clock = pygame.time.Clock()

num_rows, num_columns = 10, 10
cell_dimension = 40

enemy_grid_x = WIDTH // 4
enemy_grid_y = 10
player_grid_x = WIDTH // 4
player_grid_y = HEIGHT // 2 + 40

player_lives = 16
enemy_lives = 16
ship_count = 0
PLAYER_TURN = True

direction = 1
way = 1
enemy_attack_mode = 1

ATTACK_DELAY = 1000
enemy_attack_pending = False
enemy_attack_start = 0


class Cell:
    """Represent a single cell of the game grid."""

    def __init__(self, contains_ship, hitted, sunk):
        """Initialize the state stored in the cell."""
        self.contains_ship = contains_ship
        self.hitted = hitted
        self.sunk = sunk
        self.checked_neighbors = False
        self.ship_id = -1

    def set_ship_id(self, ship_id):
        """Store the identifier of the ship occupying the cell."""
        self.ship_id = ship_id


class Ship:
    """Represent a ship with position, size, and remaining health."""

    def __init__(self, dimension):
        """Create a ship with the given size."""
        global ship_count
        self.ship_id = ship_count
        ship_count += 1
        self.dimension = dimension
        self.remaining_cells = dimension
        self.x = None
        self.y = None
        self.direction = None

        if dimension == 2:
            self.name = "Destroyer"
        elif dimension == 3:
            self.name = "Cruiser"
        elif dimension == 4:
            self.name = "Submarine"
        elif dimension == 5:
            self.name = "Carrier"
        else:
            self.name = "invalid_name"

    def is_sunk(self):
        """Return True when the ship has no remaining cells."""
        return self.remaining_cells <= 0

    def set_coords(self, x, y, user):
        """Save ship coordinates and map its id on the target grid."""
        self.x = x
        self.y = y
        for i in range(self.dimension):
            if self.direction == 1:
                if user == 0:
                    player_grid[y][x + i].set_ship_id(self.ship_id)
                else:
                    enemy_grid[y][x + i].set_ship_id(self.ship_id)
            else:
                if user == 0:
                    player_grid[y + i][x].set_ship_id(self.ship_id)
                else:
                    enemy_grid[y + i][x].set_ship_id(self.ship_id)

    def set_direction(self, direction):
        """Set the ship orientation."""
        self.direction = direction


player_grid = [
    [Cell(False, False, False) for _ in range(num_columns)] for _ in range(num_rows)
]
enemy_grid = [
    [Cell(False, False, False) for _ in range(num_columns)] for _ in range(num_rows)
]

player_ships = [Ship(2), Ship(2), Ship(3), Ship(4), Ship(5)]
enemy_ships = [Ship(2), Ship(2), Ship(3), Ship(4), Ship(5)]
ships_placed = 0
enemy_ships_placed = False
toggle = 1


def can_place_ship(grid, row, col, dim, toggle):
    """Check whether a ship can be placed on the selected cells."""
    if not (0 <= row < num_rows and 0 <= col < num_columns):
        return False

    if toggle == 1:
        if col + dim > num_columns:
            return False
        for i in range(dim):
            if grid[row][col + i].contains_ship:
                return False
    else:
        if row + dim > num_rows:
            return False
        for i in range(dim):
            if grid[row + i][col].contains_ship:
                return False

    return True


def get_preview_cells(mx, my, ship_dim, toggle):
    """Return the preview cells under the mouse and their validity."""
    grid_width = num_columns * cell_dimension
    grid_height = num_rows * cell_dimension

    if not (
        player_grid_x <= mx < player_grid_x + grid_width
        and player_grid_y <= my < player_grid_y + grid_height
    ):
        return [], False

    col = (mx - player_grid_x) // cell_dimension
    row = (my - player_grid_y) // cell_dimension

    if not (0 <= row < num_rows and 0 <= col < num_columns):
        return [], False

    cells = []
    for i in range(ship_dim):
        r = row if toggle == 1 else row + i
        c = col + i if toggle == 1 else col
        if 0 <= r < num_rows and 0 <= c < num_columns:
            cells.append((r, c))

    valid = can_place_ship(player_grid, row, col, ship_dim, toggle)
    return cells, valid


def draw_ship_preview(surface, cells, valid):
    """Draw the placement preview for the current ship."""
    if not cells:
        return

    preview_color = PREVIEW_VALID_COLOR if valid else PREVIEW_INVALID_COLOR
    border_color = PREVIEW_VALID_BORDER if valid else PREVIEW_INVALID_BORDER

    preview_surface = pygame.Surface(
        (cell_dimension - 2, cell_dimension - 2), pygame.SRCALPHA
    )
    preview_surface.fill(preview_color)

    for r, c in cells:
        x = c * cell_dimension + player_grid_x
        y = r * cell_dimension + player_grid_y
        surface.blit(preview_surface, (x + 1, y + 1))
        pygame.draw.rect(
            surface, border_color, (x, y, cell_dimension, cell_dimension), 2
        )


def place_ship(row, col, ship_idx, toggle):
    """Place the selected player ship on the board."""
    ship_obj = player_ships[ship_idx]
    dim_ship = ship_obj.dimension

    if toggle == 1:
        ship_obj.set_direction(1)
        ship_obj.set_coords(col, row, 0)
        for i in range(dim_ship):
            player_grid[row][col + i].contains_ship = True
    else:
        ship_obj.set_direction(0)
        ship_obj.set_coords(col, row, 0)
        for i in range(dim_ship):
            player_grid[row + i][col].contains_ship = True


def place_enemy_ships():
    """Randomly place all enemy ships on the board."""
    global enemy_ships_placed

    for i in range(len(enemy_ships)):
        ship_obj = enemy_ships[i]
        ship_dim = ship_obj.dimension

        attempts = 0
        while attempts < 100:
            ship_direction = random.randint(0, 1)

            if ship_direction == 1:
                x_e = random.randint(0, num_columns - ship_dim)
                y_e = random.randint(0, num_rows - 1)
                coords_ok = True

                for j in range(ship_dim):
                    if (
                        enemy_grid[y_e][x_e + j].contains_ship
                        or (j > 0 and enemy_grid[y_e][x_e + j - 1].contains_ship)
                        or (
                            j < ship_dim - 1
                            and enemy_grid[y_e][x_e + j + 1].contains_ship
                        )
                    ):
                        coords_ok = False
                        break
            else:
                x_e = random.randint(0, num_columns - 1)
                y_e = random.randint(0, num_rows - ship_dim)
                coords_ok = True

                for j in range(ship_dim):
                    if (
                        enemy_grid[y_e + j][x_e].contains_ship
                        or (j > 0 and enemy_grid[y_e + j - 1][x_e].contains_ship)
                        or (
                            j < ship_dim - 1
                            and enemy_grid[y_e + j + 1][x_e].contains_ship
                        )
                    ):
                        coords_ok = False
                        break

            if coords_ok:
                ship_obj.set_direction(ship_direction)

                if ship_direction == 1:
                    for j in range(ship_dim):
                        enemy_grid[y_e][x_e + j].contains_ship = True
                    ship_obj.set_coords(x_e, y_e, 1)
                else:
                    for j in range(ship_dim):
                        enemy_grid[y_e + j][x_e].contains_ship = True
                    ship_obj.set_coords(x_e, y_e, 1)
                break

            attempts += 1

    enemy_ships_placed = True


def enemy_attack():
    """Execute the enemy attack logic and update the game state."""
    global PLAYER_TURN, player_lives, winner_text, game_over
    global enemy_attack_mode, direction, way

    if not hasattr(enemy_attack, "target_ship_id"):
        enemy_attack.target_ship_id = None
        enemy_attack.hits = []
        enemy_attack.orientation = None

    def in_bounds(r, c):
        return 0 <= r < num_rows and 0 <= c < num_columns

    def reset_target():
        enemy_attack.target_ship_id = None
        enemy_attack.hits = []
        enemy_attack.orientation = None

    if enemy_attack.target_ship_id is not None:
        sid = enemy_attack.target_ship_id
        if 0 <= sid < len(player_ships):
            if player_ships[sid].remaining_cells <= 0:
                reset_target()

    shot = None

    if enemy_attack.target_ship_id is not None and enemy_attack.hits:
        hits = list(dict.fromkeys(enemy_attack.hits))
        enemy_attack.hits = hits

        if len(hits) >= 2:
            same_row = all(r == hits[0][0] for r, c in hits)
            same_col = all(c == hits[0][1] for r, c in hits)

            if same_row:
                enemy_attack.orientation = "H"
            elif same_col:
                enemy_attack.orientation = "V"

        candidates = []

        if enemy_attack.orientation == "H":
            row = hits[0][0]
            cols = sorted(c for r, c in hits)
            candidates = [(row, cols[0] - 1), (row, cols[-1] + 1)]
            enemy_attack_mode = 3
            direction = 1
        elif enemy_attack.orientation == "V":
            col = hits[0][1]
            rows = sorted(r for r, c in hits)
            candidates = [(rows[0] - 1, col), (rows[-1] + 1, col)]
            enemy_attack_mode = 3
            direction = -1
        else:
            r, c = hits[0]
            candidates = [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]
            random.shuffle(candidates)
            enemy_attack_mode = 2
            direction = 0

        for rr, cc in candidates:
            if in_bounds(rr, cc) and not player_grid[rr][cc].hitted:
                shot = (rr, cc)
                break

        if shot is None:
            reset_target()
            enemy_attack_mode = 1

    if shot is None:
        parity_cells = [
            (r, c)
            for r in range(num_rows)
            for c in range(num_columns)
            if not player_grid[r][c].hitted and (r + c) % 2 == 0
        ]

        available_cells = (
            parity_cells
            if parity_cells
            else [
                (r, c)
                for r in range(num_rows)
                for c in range(num_columns)
                if not player_grid[r][c].hitted
            ]
        )

        if not available_cells:
            PLAYER_TURN = True
            return True

        shot = random.choice(available_cells)
        enemy_attack_mode = 1

    row, col = shot
    cell = player_grid[row][col]
    cell.hitted = True

    if cell.contains_ship:
        cell.contains_ship = False
        cell.sunk = True
        player_lives -= 1

        if player_lives <= 0:
            winner_text = "YOU LOSE!"
            game_over = True
            PLAYER_TURN = True

        ship_id = cell.ship_id

        if 0 <= ship_id < len(player_ships):
            player_ships[ship_id].remaining_cells -= 1

        if enemy_attack.target_ship_id != ship_id:
            enemy_attack.target_ship_id = ship_id
            enemy_attack.hits = [(row, col)]
            enemy_attack.orientation = None
        else:
            if (row, col) not in enemy_attack.hits:
                enemy_attack.hits.append((row, col))

        if len(enemy_attack.hits) >= 2:
            same_row = all(r == enemy_attack.hits[0][0] for r, c in enemy_attack.hits)
            same_col = all(c == enemy_attack.hits[0][1] for r, c in enemy_attack.hits)

            if same_row:
                enemy_attack.orientation = "H"
                direction = 1
            elif same_col:
                enemy_attack.orientation = "V"
                direction = -1

        if player_ships[ship_id].remaining_cells <= 0:
            reset_target()
            enemy_attack_mode = 1
            direction = 0
            way = 0
        else:
            enemy_attack_mode = 3 if enemy_attack.orientation else 2
            way = 1

        PLAYER_TURN = False
        return True

    PLAYER_TURN = True
    return True


def reset_game():
    """Restore the game to its initial state."""
    global player_grid, enemy_grid
    global player_lives, enemy_lives, ship_count
    global PLAYER_TURN, ships_placed, enemy_ships_placed
    global toggle, game_over, winner_text
    global enemy_attack_mode, direction, way
    global player_ships, enemy_ships
    global enemy_attack_pending, enemy_attack_start
    global show_instructions

    ship_count = 0

    player_lives = 16
    enemy_lives = 16
    PLAYER_TURN = True

    ships_placed = 0
    enemy_ships_placed = False
    toggle = 1

    game_over = False
    winner_text = ""
    show_instructions = False

    enemy_attack_mode = 1
    direction = 1
    way = 1

    enemy_attack_pending = False
    enemy_attack_start = 0

    player_grid = [
        [Cell(False, False, False) for _ in range(num_columns)] for _ in range(num_rows)
    ]
    enemy_grid = [
        [Cell(False, False, False) for _ in range(num_columns)] for _ in range(num_rows)
    ]

    player_ships = [Ship(2), Ship(2), Ship(3), Ship(4), Ship(5)]
    enemy_ships = [Ship(2), Ship(2), Ship(3), Ship(4), Ship(5)]

    if hasattr(enemy_attack, "target_ship_id"):
        enemy_attack.target_ship_id = None
        enemy_attack.hits = []
        enemy_attack.orientation = None


def draw_help_button():
    """Draw the help button shown during gameplay."""
    pygame.draw.rect(display, BUTTON_BLUE, help_button, border_radius=10)
    pygame.draw.rect(display, WHITE, help_button, 2, border_radius=10)

    text_help = font_button.render("Help", True, WHITE)
    text_help_rect = text_help.get_rect(center=help_button.center)
    display.blit(text_help, text_help_rect)


def draw_instructions_overlay():
    """Draw the instruction overlay panel."""
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    display.blit(overlay, (0, 0))

    panel_width = 580
    panel_height = 470
    panel_x = WIDTH // 2 - panel_width // 2
    panel_y = HEIGHT // 2 - panel_height // 2
    panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)

    pygame.draw.rect(display, DARK_PANEL, panel_rect, border_radius=16)
    pygame.draw.rect(display, WHITE, panel_rect, 2, border_radius=16)

    pygame.draw.rect(display, BUTTON_RED, close_instructions_button, border_radius=8)
    pygame.draw.rect(display, WHITE, close_instructions_button, 2, border_radius=8)

    margin = 10
    x1 = close_instructions_button.x + margin
    y1 = close_instructions_button.y + margin
    x2 = close_instructions_button.right - margin
    y2 = close_instructions_button.bottom - margin
    pygame.draw.line(display, WHITE, (x1, y1), (x2, y2), 3)
    pygame.draw.line(display, WHITE, (x2, y1), (x1, y2), 3)

    title = font_big.render("Instructions", True, WHITE)
    title_rect = title.get_rect(center=(WIDTH // 2, panel_y + 45))
    display.blit(title, title_rect)

    lines = [
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
    ]

    start_y = panel_y + 95
    for line in lines:
        text = font_small.render(line, True, (240, 240, 240))
        display.blit(text, (panel_x + 28, start_y))
        start_y += 26


def main():
    """Run the main Battleship loop."""
    global show_instructions, enemy_attack_pending, enemy_attack_start
    global ships_placed, toggle, PLAYER_TURN, game_over, winner_text, enemy_lives

    running = True

    while running:
        display.fill(BACKGROUND_COLOR)

        if not enemy_ships_placed:
            place_enemy_ships()

        mouse_x, mouse_y = pygame.mouse.get_pos()

        preview_cells = []
        preview_valid = False
        current_ship = None

        if 0 <= ships_placed < len(player_ships):
            current_ship = player_ships[ships_placed]
            preview_cells, preview_valid = get_preview_cells(
                mouse_x, mouse_y, current_ship.dimension, toggle
            )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if (
                    game_over
                    and event.button == 1
                    and restart_button.collidepoint(event.pos)
                ):
                    reset_game()
                    continue

                if show_instructions:
                    if event.button == 1 and close_instructions_button.collidepoint(
                        event.pos
                    ):
                        show_instructions = False
                        if enemy_attack_pending:
                            enemy_attack_start = pygame.time.get_ticks()
                    continue

                if (
                    not game_over
                    and event.button == 1
                    and help_button.collidepoint(event.pos)
                ):
                    show_instructions = True
                    continue

                if (
                    ships_placed < len(player_ships)
                    and current_ship is not None
                    and not game_over
                ):
                    if event.button == 1:
                        mx, my = event.pos
                        col = (mx - player_grid_x) // cell_dimension
                        row = (my - player_grid_y) // cell_dimension

                        if 0 <= row < num_rows and 0 <= col < num_columns:
                            dim = current_ship.dimension
                            if can_place_ship(player_grid, row, col, dim, toggle):
                                place_ship(row, col, ships_placed, toggle)
                                ships_placed += 1

                    elif event.button == 3:
                        toggle *= -1

                elif (
                    ships_placed >= len(player_ships)
                    and event.button == 1
                    and PLAYER_TURN
                    and not game_over
                ):
                    mx, my = event.pos

                    if (
                        enemy_grid_x <= mx < enemy_grid_x + num_columns * cell_dimension
                        and enemy_grid_y <= my < enemy_grid_y + num_rows * cell_dimension
                    ):
                        col = (mx - enemy_grid_x) // cell_dimension
                        row = (my - enemy_grid_y) // cell_dimension

                        if (
                            0 <= row < num_rows
                            and 0 <= col < num_columns
                            and not enemy_grid[row][col].hitted
                        ):
                            enemy_grid[row][col].hitted = True

                            if enemy_grid[row][col].contains_ship:
                                enemy_grid[row][col].contains_ship = False
                                enemy_grid[row][col].sunk = True
                                enemy_lives -= 1

                                if enemy_lives <= 0:
                                    winner_text = "YOU WIN!"
                                    game_over = True
                                    PLAYER_TURN = True
                                    enemy_attack_pending = False
                                else:
                                    PLAYER_TURN = True
                                    enemy_attack_pending = False
                            else:
                                PLAYER_TURN = False
                                enemy_attack_pending = True
                                enemy_attack_start = pygame.time.get_ticks()


        placement_phase = (
            ships_placed < len(player_ships)
            and current_ship is not None
            and not game_over
        )

        if placement_phase:
            text_place_your_ships = font_title.render("Place your ships", True, WHITE)
            text_place_your_ships_rect = text_place_your_ships.get_rect(
                center=(WIDTH / 2, HEIGHT / 9)
            )
            display.blit(text_place_your_ships, text_place_your_ships_rect)

            text_ship = font_ship.render(current_ship.name, True, WHITE)
            text_ship_rect = text_ship.get_rect(center=(WIDTH / 2, HEIGHT / 5))
            display.blit(text_ship, text_ship_rect)

            if toggle == 1:
                ship_width = current_ship.dimension * cell_dimension
            else:
                ship_width = cell_dimension

            start_x = WIDTH / 2 - ship_width / 2
            start_y = HEIGHT / 4
            for i in range(current_ship.dimension):
                if toggle == 1:
                    cell_x = start_x + i * cell_dimension
                    cell_y = start_y
                else:
                    cell_x = start_x
                    cell_y = start_y + i * cell_dimension

                pygame.draw.rect(
                    display, SHIPS_COLOR, (cell_x, cell_y, cell_dimension, cell_dimension)
                )
                pygame.draw.rect(
                    display, BLACK, (cell_x, cell_y, cell_dimension, cell_dimension), 1
                )

            for r in range(num_rows):
                for c in range(num_columns):
                    x = c * cell_dimension + player_grid_x
                    y = r * cell_dimension + player_grid_y
                    color = SHIPS_COLOR if player_grid[r][c].contains_ship else BLUE
                    pygame.draw.rect(
                        display,
                        color,
                        (x + 1, y + 1, cell_dimension - 2, cell_dimension - 2),
                    )
                    pygame.draw.rect(
                        display, BLUE_GIRD_MARGIN, (x, y, cell_dimension, cell_dimension), 1
                    )

            if not show_instructions:
                draw_ship_preview(display, preview_cells, preview_valid)

        else:
            pygame.draw.line(display, BLACK, (0, HEIGHT // 2), (WIDTH, HEIGHT // 2), 3)

            if enemy_attack_pending and not game_over and not show_instructions:
                if pygame.time.get_ticks() - enemy_attack_start >= ATTACK_DELAY:
                    enemy_attack()

                    if not PLAYER_TURN and not game_over:
                        enemy_attack_start = pygame.time.get_ticks()
                    else:
                        enemy_attack_pending = False


            for r in range(num_rows):
                for c in range(num_columns):
                    x = c * cell_dimension + player_grid_x
                    y = r * cell_dimension + player_grid_y
                    rect = pygame.Rect(x, y, cell_dimension, cell_dimension)

                    if player_grid[r][c].contains_ship and not player_grid[r][c].hitted:
                        color = SHIPS_COLOR
                    elif not player_grid[r][c].hitted:
                        color = BLUE
                    else:
                        color = LIGHT_GRAY

                    pygame.draw.rect(
                        display,
                        color,
                        (x + 1, y + 1, cell_dimension - 2, cell_dimension - 2),
                    )
                    pygame.draw.rect(display, BLUE_GIRD_MARGIN, rect, 1)

                    if player_grid[r][c].hitted:
                        center_x = x + cell_dimension // 2
                        center_y = y + cell_dimension // 2

                        if player_grid[r][c].sunk:
                            margin = 8
                            pygame.draw.line(
                                display,
                                RED,
                                (x + margin, y + margin),
                                (x + cell_dimension - margin, y + cell_dimension - margin),
                                3,
                            )
                            pygame.draw.line(
                                display,
                                RED,
                                (x + cell_dimension - margin, y + margin),
                                (x + margin, y + cell_dimension - margin),
                                3,
                            )
                        else:
                            radius = cell_dimension // 4
                            pygame.draw.circle(display, WHITE, (center_x, center_y), radius, 3)

            for r in range(num_rows):
                for c in range(num_columns):
                    x = c * cell_dimension + enemy_grid_x
                    y = r * cell_dimension + enemy_grid_y
                    rect = pygame.Rect(x, y, cell_dimension, cell_dimension)

                    if not enemy_grid[r][c].hitted:
                        color = BLUE
                    else:
                        color = LIGHT_GRAY

                    pygame.draw.rect(
                        display,
                        color,
                        (x + 1, y + 1, cell_dimension - 2, cell_dimension - 2),
                    )
                    pygame.draw.rect(display, BLUE_GIRD_MARGIN, rect, 1)

                    if enemy_grid[r][c].hitted:
                        center_x = x + cell_dimension // 2
                        center_y = y + cell_dimension // 2

                        if enemy_grid[r][c].sunk:
                            margin = 8
                            pygame.draw.line(
                                display,
                                RED,
                                (x + margin, y + margin),
                                (x + cell_dimension - margin, y + cell_dimension - margin),
                                3,
                            )
                            pygame.draw.line(
                                display,
                                RED,
                                (x + cell_dimension - margin, y + margin),
                                (x + margin, y + cell_dimension - margin),
                                3,
                            )
                        else:
                            radius = cell_dimension // 4
                            pygame.draw.circle(display, WHITE, (center_x, center_y), radius, 3)

            if PLAYER_TURN:
                overlay = pygame.Surface(
                    (num_columns * cell_dimension, num_rows * cell_dimension),
                    pygame.SRCALPHA,
                )
                overlay.fill((0, 0, 0, 120))
                display.blit(overlay, (player_grid_x, player_grid_y))
            else:
                overlay = pygame.Surface(
                    (num_columns * cell_dimension, num_rows * cell_dimension),
                    pygame.SRCALPHA,
                )
                overlay.fill((0, 0, 0, 120))
                display.blit(overlay, (enemy_grid_x, enemy_grid_y))

            if not game_over:
                draw_help_button()

            if show_instructions and not game_over:
                draw_instructions_overlay()

            if game_over:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 120))
                display.blit(overlay, (0, 0))

                text_surface = font_big.render(winner_text, True, WHITE)
                text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
                display.blit(text_surface, text_rect)

                pygame.draw.rect(display, (0, 180, 0), restart_button)
                pygame.draw.rect(display, BLACK, restart_button, 2)

                button_text = font_button.render("Ricomincia", True, WHITE)
                button_rect = button_text.get_rect(center=restart_button.center)
                display.blit(button_text, button_rect)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
