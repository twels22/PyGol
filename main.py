#python
import pygame
import sys
import math
import tkinter as tk
from tkinter import simpledialog

pygame.init()

#constants

WIDTH, HEIGHT = 800, 600
CELL_SIZE = 10
FPS = 30

# cls
WHITE = (240, 240, 240)
BLACK = (20, 20, 20)
GRAY = (180, 180, 180)
DIMMED_WHITE = (200, 200, 200)
HIGHLIGHT = (100, 100, 255)
RED = (255, 100, 100)
LIGHT_BLUE = (150, 200, 255)
GRID_BG_COLOR = (138, 127, 142)

#gradietn
START_COLOR = (235, 235, 0)
END_COLOR = (102, 102, 255)


screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("pyGOL")

clock = pygame.time.Clock()

#vars
cols, rows = WIDTH // CELL_SIZE, HEIGHT // CELL_SIZE
grid = [[0 for _ in range(cols)] for _ in range(rows)]
age_grid = [[0 for _ in range(cols)] for _ in range(rows)]
is_running = False
scroll_offset = [0, 0]
mousedown = False
remove_mode = False

#rules
birth = {3}
survive = {2, 3}

def draw_grid():
    global grid, age_grid

    for y in range(rows):
        for x in range(cols):
            rect = pygame.Rect(
                x * CELL_SIZE + scroll_offset[0],
                y * CELL_SIZE + scroll_offset[1],
                CELL_SIZE,
                CELL_SIZE,
            )
            pygame.draw.rect(screen, GRID_BG_COLOR, rect)

            if grid[y][x]:
                age = age_grid[y][x]

                if age < 10:
                    color = (
                        max(0, 240 - age * 24),
                        max(0, 240 - age * 12),
                        max(0, min(255, age * 25))
                    )
                else:
                    color = HIGHLIGHT
                pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, GRAY, rect, 1)

def highlight_cell(mx, my):
    global grid, age_grid
    x = (mx - scroll_offset[0]) // CELL_SIZE
    y = (my - scroll_offset[1]) // CELL_SIZE
    if 0 <= x < cols and 0 <= y < rows:
        rect = pygame.Rect(
            x * CELL_SIZE + scroll_offset[0],
            y * CELL_SIZE + scroll_offset[1],
            CELL_SIZE,
            CELL_SIZE,
        )
        pygame.draw.rect(screen, RED, rect, 2)

def get_neighbors(x, y):
    global grid, age_grid
    neighbors = 0
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < cols and 0 <= ny < rows:
                neighbors += grid[ny][nx]
    return neighbors

def update_grid():
    global grid, age_grid
    new_grid = [[0 for _ in range(cols)] for _ in range(rows)]
    new_age_grid = [[0 for _ in range(cols)] for _ in range(rows)]
    for y in range(rows):
        for x in range(cols):
            neighbors = get_neighbors(x, y)
            if grid[y][x]:
                if neighbors in survive:
                    new_grid[y][x] = 1
                    new_age_grid[y][x] = min(age_grid[y][x] + 1, 10)
            else:
                if neighbors in birth:
                    new_grid[y][x] = 1
                    new_age_grid[y][x] = 0
    grid = new_grid
    age_grid = new_age_grid

def parse_rules(birth_input, survive_input):
    global birth, survive
    try:
        birth = set(map(int, birth_input))
        survive = set(map(int, survive_input))
    except ValueError:
        pass

def input_rules_window():
    root = tk.Tk()
    root.withdraw()

    birth_input = simpledialog.askstring("rules", "new birth rule: (e.g., 3 for B3):")
    survive_input = simpledialog.askstring("rules", "new survive rule: (e.g., 23 for S23):")

    if birth_input and survive_input:
        parse_rules(birth_input, survive_input)

    root.destroy()

def resize_grid(new_cell_size):
    global CELL_SIZE, cols, rows, grid, age_grid
    CELL_SIZE = new_cell_size
    cols, rows = WIDTH // CELL_SIZE, HEIGHT // CELL_SIZE
    grid = [[0 for _ in range(cols)] for _ in range(rows)]
    age_grid = [[0 for _ in range(cols)] for _ in range(rows)]

def draw_gradient_background():
    """yellow->blue gradient background"""
    for y in range(HEIGHT):

        r = int(START_COLOR[0] + (END_COLOR[0] - START_COLOR[0]) * y / HEIGHT)
        g = int(START_COLOR[1] + (END_COLOR[1] - START_COLOR[1]) * y / HEIGHT)
        b = int(START_COLOR[2] + (END_COLOR[2] - START_COLOR[2]) * y / HEIGHT)
        color = (r, g, b)
        pygame.draw.line(screen, color, (0, y), (WIDTH, y))

def main():
    global is_running, scroll_offset, mousedown, remove_mode, grid, age_grid

    font = pygame.font.Font(None, 36)
    paused_font = pygame.font.Font(None, 48)
    rule_text = "B3/S23"
    dim_alpha = 128

    while True:

        draw_gradient_background()


        draw_grid()

        if not is_running:
            dim_surface = pygame.Surface((WIDTH, HEIGHT))
            dim_surface.set_alpha(dim_alpha)
            dim_surface.fill(DIMMED_WHITE)
            screen.blit(dim_surface, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    is_running = not is_running
                if event.key == pygame.K_e:
                    remove_mode = not remove_mode
                if event.key == pygame.K_q and pygame.key.get_pressed()[pygame.K_LCTRL]:#ctrl+q - clr screen
                    grid = [[0 for _ in range(cols)] for _ in range(rows)]
                    age_grid = [[0 for _ in range(cols)] for _ in range(rows)]

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  #lmb
                    mousedown = True
                elif event.button == 2:  # mmb
                    scroll_offset = [0, 0]
                elif event.button == 3:  # rmb
                    input_rules_window()

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    mousedown = False

            if event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[1]:  #if mmb is pressed
                    scroll_offset[0] += event.rel[0]
                    scroll_offset[1] += event.rel[1]

        #mouse
        mx, my = pygame.mouse.get_pos()
        if mousedown:
            x = (mx - scroll_offset[0]) // CELL_SIZE
            y = (my - scroll_offset[1]) // CELL_SIZE
            if 0 <= x < cols and 0 <= y < rows:
                if remove_mode:

                    grid[y][x] = 0
                    age_grid[y][x] = 1
                else:
                    grid[y][x] = 1
                    age_grid[y][x] = 0

        #highliht remove cells
        if remove_mode:
            highlight_cell(mx, my)

        #update
        if is_running:
            update_grid()

        #rules text
        text_surface = font.render(f"rules: B{''.join(map(str, birth))}/S{''.join(map(str, survive))}", True, BLACK)
        screen.blit(text_surface, (10, 10))

        #pause text
        if not is_running:
            paused_text = paused_font.render("pause", True, BLACK)
            screen.blit(paused_text, (WIDTH - 220, HEIGHT - 60))

        #
        pygame.display.flip()
        clock.tick(FPS)

#main
if __name__ == "__main__":
    main()
