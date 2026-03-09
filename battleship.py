import pygame
import random

pygame.init()

WIDTH, HEIGHT = 800, 800
WHITE = (255,255,255)

display = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Battleship")
clock = pygame.time.Clock()

num_rows, num_columns = 10, 10
cell_dimension = 30

x_pos, y_pos = 0, 400 # coordinate navi da posizionare

player_grid = []
enemy_grid = []

for i in range(num_rows):
    rows = [False] * num_columns # ogni row è composta da 10 colonne impostate a false
    player_grid.append(rows)

for i in range(num_rows):
    rows = [False] * num_columns # ogni row è composta da 10 colonne impostate a false
    enemy_grid.append(rows)

class ship:
    def __init__(self, dimension):
        self.dimension = dimension
        if dimension == 2: self.name = "Destroyer"
        elif dimension == 3: self.name = "Cruiser"
        elif dimension == 4: self.name = "Submarine"
        elif dimension == 5: self.name = "Carrier"
        else: self.name = "invalid_name"

    def set_coords(self, x, y):
        self.x = x
        self.y = y
    
    def set_direction(self, direction):
        self.direction = direction

player_ships = [ship(2), ship(2), ship(3), ship(4), ship(5)]
enemy_ships = [ship(2), ship(2), ship(3), ship(4), ship(5)]
ships_placed = 0
enemy_ships_placed = False
toggle = 1 # cambia la direzione della nave

def place_ship(row, col, ship):
    dim_ship = player_ships[ship].dimension
    if(toggle == 1):
        for i in range(dim_ship):
            player_grid[row][col+i] = not player_grid[row][col+i]
    else:
        for i in range(dim_ship):
            player_grid[row+i][col] = not player_grid[row+i][col]

def place_enemy_ships():
    ship_direction = 0 # 0 -> orizzontale | 1 -> verticale
    global enemy_ships_placed

    for i in range(5):
        ship_direction = random.randint(0,1)
        print(enemy_ships[i].name, enemy_ships[i].dimension)
        ship_dim = enemy_ships[i].dimension

        if ship_direction == 0:
            coords_accepted = False
            while coords_accepted == False:
                coords_accepted = False
                x_e = random.randint(0, 10 - ship_dim)
                y_e = random.randint(0, 10 - ship_dim)
                print("Horizontal:", x_e, y_e)
                for j in range(ship_dim):
                    if enemy_grid[y_e][x_e + j] == True:
                        print("Ritento...")
                        break
                    if j == ship_dim - 1: coords_accepted = True

            if coords_accepted == True:
                for j in range(ship_dim):
                    enemy_grid[y_e][x_e + j] = True

        else:
            coords_accepted = False
            while coords_accepted == False:
                coords_accepted = False
                x_e = random.randint(0, 10 - ship_dim)
                y_e = random.randint(0, 10 - ship_dim)
                print("Vertical:", x_e, y_e)
                for j in range(ship_dim):
                    if enemy_grid[y_e + j][x_e] == True:
                        print("Ritento...")
                        break
                    if j == ship_dim - 1: coords_accepted = True

            if coords_accepted == True:
                for j in range(ship_dim):
                    enemy_grid[y_e + j][x_e] = True

        enemy_ships[i].set_coords(x_e, y_e)
        enemy_ships[i].set_direction(ship_direction)
        print("EHIEHI", enemy_ships[i].x, enemy_ships[i].y, "Direction: ", enemy_ships[i].direction)

    enemy_ships_placed = True

running = True

while running:

    display.fill(WHITE)

    if ships_placed < 5:
        if toggle == 1: pygame.draw.rect(display, (0,0,0), (x_pos, y_pos, cell_dimension * player_ships[ships_placed].dimension, cell_dimension))
        else: pygame.draw.rect(display, (0,0,0), (x_pos, y_pos, cell_dimension, cell_dimension * player_ships[ships_placed].dimension))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Click Sinistro
                    mx, my = event.pos
                    print(mx, my)
                    col = mx // cell_dimension
                    row = my // cell_dimension
                    if 0 <= row < num_rows and 0 <= col < num_columns and ships_placed < len(player_ships):
                        if toggle == 1 and col + player_ships[ships_placed].dimension > 10: print("You can't place player_ships here!")
                        elif toggle == -1 and row + player_ships[ships_placed].dimension > 10: print("You can't place player_ships here!")
                        else:
                            trovato = False
                            if toggle == 1:
                                for i in range(player_ships[ships_placed].dimension):
                                    if player_grid[row][col+i] == True:
                                        trovato = True
                                        break
                            else:
                                for i in range(player_ships[ships_placed].dimension):
                                    if player_grid[row+i][col] == True:
                                        trovato = True
                                        break

                            if trovato == False:
                                place_ship(row, col, ships_placed)
                                ships_placed += 1

                elif event.button == 3: #Click Destro
                    toggle *= -1

        # Disegna player_grid
        for r in range(num_rows):
            for c in range(num_columns):
                x = c * cell_dimension
                y = r * cell_dimension

                if player_grid[r][c]:
                    colour = (0, 255, 0)
                else:
                    colour = (128,128,128)

                pygame.draw.rect(display, colour, (x + 1, y + 1, cell_dimension - 2, cell_dimension - 2))
                pygame.draw.rect(display, (0, 0, 0), (x, y, cell_dimension, cell_dimension), 1)  # Bordo



    # Navi posizionate, inizia il gioco
    else:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Click Sinistro
                    mx, my = event.pos
                    print(mx, my)
                    col = mx // cell_dimension
                    row = my // cell_dimension

        for r in range(num_rows):
            for c in range(num_columns):
                x = c * cell_dimension
                y = r * cell_dimension

                if player_grid[r][c]:
                    colour = (0, 255, 0)
                else:
                    colour = (128,128,128)

                pygame.draw.rect(display, colour, (x + 1, y + 1, cell_dimension - 2, cell_dimension - 2))
                pygame.draw.rect(display, (0, 0, 0), (x, y, cell_dimension, cell_dimension), 1)  # Bordo

                if enemy_ships_placed == False: place_enemy_ships()

        # Disegna enemy_grid
        for r in range(num_rows):
            for c in range(num_columns):
                x = c * cell_dimension + 400
                y = r * cell_dimension

                if enemy_grid[r][c]:
                    colour = (0, 255, 0)
                else:
                    colour = (128,128,128)

                pygame.draw.rect(display, colour, (x + 1, y + 1, cell_dimension - 2, cell_dimension - 2))
                pygame.draw.rect(display, (0, 0, 0), (x, y, cell_dimension, cell_dimension), 1)  # Bordo

        

#  # Disegna Navi Fuori
#  prev_ship_dim = 0
#  gap = 0
#  c = 0
#
#  for i in range(len(player_ships)):
#    x_pos = (prev_ship_dim * cell_dimension) + gap
#    pygame.draw.rect(display, (c,0,0), (x_pos, 400, cell_dimension * player_ships[i].dimension, cell_dimension))
#    prev_ship_dim += player_ships[i].dimension
#    gap += 10+prev_ship_dim
#    c += 50
  
    pygame.display.flip()

    clock.tick(60)

pygame.quit()