import pygame
import random
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE

# Initialize Pygame
pygame.init()

# Set up the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(TITLE)

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GREY = (100, 100, 100)
DARK_RED = (139, 0, 0)
DARK_GREEN = (0, 100, 0)
DARK_BLUE = (0, 0, 139)

# Adjust Game Settings
TILE_SIZE = 40  # Increased block size for coarser grid
ROWS, COLS = SCREEN_HEIGHT // TILE_SIZE, SCREEN_WIDTH // TILE_SIZE
exit_tile = (COLS - 2, ROWS - 2)  
PLAYER_SPEED = 0.25  # Slowed down player speed
GUARD_SPEED = 0.05  # Slowed down guard speed
FPS = 30  # Reduced frame rate

# Load Assets
player_idle = pygame.image.load("assets/images/playeridle.png")
player_run1 = pygame.image.load("assets/images/playerrun1.png")
player_run2 = pygame.image.load("assets/images/playerrun2.png")
player_idle = pygame.transform.scale(player_idle, (TILE_SIZE, TILE_SIZE))
player_run1 = pygame.transform.scale(player_run1, (TILE_SIZE, TILE_SIZE))
player_run2 = pygame.transform.scale(player_run2, (TILE_SIZE, TILE_SIZE))

guard_idle = pygame.image.load("assets/images/copidle.png")
guard_run1 = pygame.image.load("assets/images/coprun1.png")
guard_run2 = pygame.image.load("assets/images/coprun2.png")
guard2_run1 = pygame.image.load("assets/images/cop2run1.png")
guard2_run2 = pygame.image.load("assets/images/cop2run2.png")
guard2_idle = pygame.image.load("assets/images/cop2idle.png")
guard_idle = pygame.transform.scale(guard_idle, (TILE_SIZE, TILE_SIZE))
guard_run1 = pygame.transform.scale(guard_run1, (TILE_SIZE, TILE_SIZE))
guard_run2 = pygame.transform.scale(guard_run2, (TILE_SIZE, TILE_SIZE))
guard2_run1 = pygame.transform.scale(guard2_run1, (TILE_SIZE, TILE_SIZE))
guard2_run2 = pygame.transform.scale(guard2_run2, (TILE_SIZE, TILE_SIZE))
guard2_idle = pygame.transform.scale(guard2_idle, (TILE_SIZE, TILE_SIZE))

floor_img = pygame.image.load("assets/images/floor.jpg")
floor_img = pygame.transform.scale(floor_img, (TILE_SIZE, TILE_SIZE))

wall_img = pygame.image.load("assets/images/wallgrey.png")
wall_img = pygame.transform.scale(wall_img, (TILE_SIZE, TILE_SIZE))

exit_img = pygame.image.load("assets/images/doorred.png")
exit_img = pygame.transform.scale(exit_img, (TILE_SIZE, TILE_SIZE))

obstacle_images = [
    pygame.transform.scale(pygame.image.load("assets/images/pipesblue.png"), (TILE_SIZE, TILE_SIZE)),
    pygame.transform.scale(pygame.image.load("assets/images/pipesgreen.png"), (TILE_SIZE, TILE_SIZE)),
    pygame.transform.scale(pygame.image.load("assets/images/pipesred.png"), (TILE_SIZE, TILE_SIZE)),
    pygame.transform.scale(pygame.image.load("assets/images/table1.png"), (TILE_SIZE, TILE_SIZE)),
    pygame.transform.scale(pygame.image.load("assets/images/desk.png"), (TILE_SIZE, TILE_SIZE))
]

# Fonts
gameboy_font_path = "assets/fonts/Early GameBoy.ttf"
title_font = pygame.font.Font(gameboy_font_path, 50)
tagline_font = pygame.font.Font(gameboy_font_path, 25)
button_font = pygame.font.Font(gameboy_font_path, 15)

# Player Position and Facing Direction
player_x, player_y = TILE_SIZE, TILE_SIZE
player_img = player_idle
facing_right = True
player_frame = 0
player_frozen = False
freeze_start_time = 0
freeze_cooldown = 0

# Maze, Guards, Obstacles, and Exit
maze = []
guards = []
obstacles = []
# exit_tile = (COLS - 2, ROWS - 2)

# Difficulty Settings
difficulty = "Medium"
guard_counts = {"Easy": 2, "Medium": 4, "Hard": 8}

from heapq import heappop, heappush

def astar_pathfinding(start, end):
    open_set = []
    heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, end)}

    while open_set:
        _, current = heappop(open_set)

        if current == end:
            return reconstruct_path(came_from, current)

        neighbors = [
            (current[0] + dx, current[1] + dy)
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]
            if 0 <= current[0] + dx < COLS and 0 <= current[1] + dy < ROWS and maze[current[1] + dy][current[0] + dx] == 0
        ]

        for neighbor in neighbors:
            tentative_g_score = g_score[current] + 1  # All moves cost 1

            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, end)
                heappush(open_set, (f_score[neighbor], neighbor))

    return []  # No path found

def heuristic(a, b):
    # Manhattan distance
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def reconstruct_path(came_from, current):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    return path[::-1]


# Function to Draw the Floor
def draw_floor():
    for x in range(0, SCREEN_WIDTH, TILE_SIZE):
        for y in range(0, SCREEN_HEIGHT, TILE_SIZE):
            screen.blit(floor_img, (x, y))

# Enhanced Maze Generation
def generate_maze():
    global maze
    maze = [[1] * COLS for _ in range(ROWS)]

    # Recursive Backtracking Algorithm
    def carve(x, y):
        directions = [(0, -2), (0, 2), (-2, 0), (2, 0)]
        random.shuffle(directions)

        for dx, dy in directions:
            nx, ny = x + dx, y + dy

            if 0 < nx < COLS and 0 < ny < ROWS and maze[ny][nx] == 1:
                maze[y + dy // 2][x + dx // 2] = 0  # Open the path
                maze[ny][nx] = 0
                carve(nx, ny)

    # Start at the top-left corner
    carve(1, 1)
    maze[exit_tile[1]][exit_tile[0]] = 0  # Ensure the exit is clear

    # Add extra connections for multiple paths
    def add_connections():
        for _ in range((ROWS * COLS) // 16):  # Add ~6.25% extra connections
            x, y = random.randint(1, COLS - 2), random.randint(1, ROWS - 2)
            if maze[y][x] == 1:  # If it's a wall
                neighbors = [
                    (x + dx, y + dy) for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]
                    if 0 <= x + dx < COLS and 0 <= y + dy < ROWS and maze[y + dy][x + dx] == 0
                ]
                if len(neighbors) >= 2:  # Only connect if two or more paths exist
                    maze[y][x] = 0

    add_connections()

    # Ensure the bottom row is filled with walls
    for x in range(COLS):
        maze[ROWS - 1][x] = 1

# Function to Place Guards and Obstacles
def place_entities():
    global guards, obstacles
    guards = []
    obstacles = []

    empty_cells = [(x, y) for y in range(ROWS) for x in range(COLS) if maze[y][x] == 0]

    # Place guards based on difficulty
    for _ in range(guard_counts[difficulty]):
        if empty_cells:
            x, y = random.choice(empty_cells)
            route = []
            current_x, current_y = x, y

            # Generate patrol route with valid moves
            for _ in range(5):  # Adjust patrol steps
                neighbors = [
                    (current_x + dx, current_y + dy)
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]
                    if 0 <= current_x + dx < COLS and 0 <= current_y + dy < ROWS and maze[current_y + dy][current_x + dx] == 0
                ]
                if neighbors:
                    next_pos = random.choice(neighbors)
                    route.append(next_pos)
                    current_x, current_y = next_pos
            if route:
                guards.append({"pos": (x, y), "route": route, "route_index": 0, "direction": 1, "progress": 0})
            empty_cells.remove((x, y))

    for _ in range(2):  # Place 2 obstacles
        x, y = random.choice(empty_cells)
        obstacles.append((x, y, random.choice(obstacle_images)))
        empty_cells.remove((x, y))

def draw_maze():
    for y in range(ROWS):
        for x in range(COLS):
            if maze[y][x] == 1:  # Wall
                screen.blit(wall_img, (x * TILE_SIZE, y * TILE_SIZE))
            # Remove checkpoint drawing
            # elif maze[y][x] == 2:  # Checkpoint
            #     pygame.draw.rect(screen, DARK_GREEN, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

    for guard in guards:
        gx, gy = guard["pos"]
        guard_img = guard_idle if guard["progress"] == 0 else (guard_run1 if guard["progress"] < 0.5 else guard_run2)
        if guard.get("facing_left", False):  # Check if guard is facing left
            guard_img = pygame.transform.flip(guard_img, True, False)
        screen.blit(guard_img, (gx * TILE_SIZE, gy * TILE_SIZE))

    for ox, oy, img in obstacles:
        screen.blit(img, (ox * TILE_SIZE, oy * TILE_SIZE))

    # Draw the Exit Tile
    ex, ey = exit_tile
    screen.blit(exit_img, (ex * TILE_SIZE, ey * TILE_SIZE))  # Use panel.png for exit

# Collision Checking
def is_collision(x, y):
    return maze[y][x] == 1

def is_obstacle_collision(x, y):
    for ox, oy, _ in obstacles:
        if int((x + TILE_SIZE // 2) // TILE_SIZE) == ox and int((y + TILE_SIZE // 2) // TILE_SIZE) == oy:
            return True
    return False

def update_guards():
    for guard in guards:
        current_pos = guard["route"][guard["route_index"]]
        next_index = (guard["route_index"] + guard["direction"]) % len(guard["route"])
        next_pos = guard["route"][next_index]

        # A* pathfinding to calculate path to next patrol point
        path = astar_pathfinding(current_pos, next_pos)

        if path:
            guard["progress"] += GUARD_SPEED
            guard["progress"] = min(guard["progress"], 1)  # Clamp progress
            current_step = path[0]
            next_step = path[1] if len(path) > 1 else current_step

            guard["pos"] = (
                current_step[0] + (next_step[0] - current_step[0]) * guard["progress"],
                current_step[1] + (next_step[1] - current_step[1]) * guard["progress"]
            )

            # Flip sprite if direction changes (left/right only)
            if next_step[0] < current_step[0]:  # Moving left
                guard["facing_left"] = True
            elif next_step[0] > current_step[0]:  # Moving right
                guard["facing_left"] = False

            # Update index when reaching the next step
            if guard["progress"] >= 1:
                guard["route_index"] = next_index
                guard["progress"] = 0
        else:
            # Reverse the route if no path found (end of patrol)
            guard["route"].reverse()
            guard["direction"] *= -1  # Reverse direction

# Function to Draw the Menu
def draw_menu(dropdown_open):
    draw_floor()
    player_menu = pygame.image.load('assets/images/menu_player.png')
    screen.blit(player_menu, (SCREEN_WIDTH // 2 - player_menu.get_width() // 2, SCREEN_HEIGHT // 2 - player_menu.get_height() // 2 + 40))

    title_text = title_font.render("Mission 804", True, WHITE)
    tagline_text = tagline_font.render("Tabdeeli aa Nhi Rahi,", True, WHITE)
    tagline_text2 = tagline_font.render("Tabdeeli aa Gayi Hai", True, WHITE)
    start_text = button_font.render("Start", True, WHITE)
    difficulty_text = button_font.render(f"{difficulty}", True, WHITE)
    quit_text = button_font.render("Quit", True, WHITE)

    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 300))
    screen.blit(tagline_text, (SCREEN_WIDTH // 2 - tagline_text.get_width() // 2, SCREEN_HEIGHT // 2 - 200))
    screen.blit(tagline_text2, (SCREEN_WIDTH // 2 - tagline_text2.get_width() // 2, SCREEN_HEIGHT // 2 - 150))

    pygame.draw.rect(screen, DARK_GREEN, (SCREEN_WIDTH // 2 - 350, SCREEN_HEIGHT // 2 + 180, 200, 50))
    pygame.draw.rect(screen, DARK_GREY, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 180, 200, 50))
    pygame.draw.rect(screen, DARK_RED, (SCREEN_WIDTH // 2 + 150, SCREEN_HEIGHT // 2 + 180, 200, 50))

    screen.blit(start_text, (SCREEN_WIDTH // 2 - 300 + 50 - start_text.get_width() // 2, SCREEN_HEIGHT // 2 + 190))
    screen.blit(difficulty_text, (SCREEN_WIDTH // 2 - 100 + 100 - difficulty_text.get_width() // 2, SCREEN_HEIGHT // 2 + 190))
    screen.blit(quit_text, (SCREEN_WIDTH // 2 + 100 + 150 - quit_text.get_width() // 2, SCREEN_HEIGHT // 2 + 190))

    if dropdown_open:
        easy_text = button_font.render("Easy", True, WHITE)
        medium_text = button_font.render("Medium", True, WHITE)
        hard_text = button_font.render("Hard", True, WHITE)

        pygame.draw.rect(screen, DARK_GREY, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 200, 200, 50))
        pygame.draw.rect(screen, DARK_GREY, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 250, 200, 50))
        pygame.draw.rect(screen, DARK_GREY, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 300, 200, 50))

        screen.blit(easy_text, (SCREEN_WIDTH // 2 - easy_text.get_width() // 2, SCREEN_HEIGHT // 2 + 210))
        screen.blit(medium_text, (SCREEN_WIDTH // 2 - medium_text.get_width() // 2, SCREEN_HEIGHT // 2 + 260))
        screen.blit(hard_text, (SCREEN_WIDTH // 2 - hard_text.get_width() // 2, SCREEN_HEIGHT // 2 + 310))

    pygame.display.flip()

# Main Menu Function
def main_menu():
    global difficulty
    menu_running = True
    dropdown_open = False
    while menu_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if SCREEN_WIDTH // 2 - 300 <= mouse_x <= SCREEN_WIDTH // 2 - 100:
                    if SCREEN_HEIGHT // 2 + 150 <= mouse_y <= SCREEN_HEIGHT // 2 + 200:
                        menu_running = False  # Start the game
                elif SCREEN_WIDTH // 2 - 100 <= mouse_x <= SCREEN_WIDTH // 2 + 100:
                    if SCREEN_HEIGHT // 2 + 150 <= mouse_y <= SCREEN_HEIGHT // 2 + 200:
                        dropdown_open = not dropdown_open  # Toggle dropdown
                    elif dropdown_open:
                        if SCREEN_HEIGHT // 2 + 200 <= mouse_y <= SCREEN_HEIGHT // 2 + 250:
                            difficulty = "Easy"
                            dropdown_open = False
                        elif SCREEN_HEIGHT // 2 + 250 <= mouse_y <= SCREEN_HEIGHT // 2 + 300:
                            difficulty = "Medium"
                            dropdown_open = False
                        elif SCREEN_HEIGHT // 2 + 300 <= mouse_y <= SCREEN_HEIGHT // 2 + 350:
                            difficulty = "Hard"
                            dropdown_open = False
                elif SCREEN_WIDTH // 2 + 100 <= mouse_x <= SCREEN_WIDTH // 2 + 300:
                    if SCREEN_HEIGHT // 2 + 150 <= mouse_y <= SCREEN_HEIGHT // 2 + 200:
                        pygame.quit()
                        exit()  # Quit the game

        draw_menu(dropdown_open)

# Function to Draw the Pause Menu
def draw_pause_menu():
    # Draw the pause sign (two rectangles)
    rect_width, rect_height = 20, 60
    rect_x = SCREEN_WIDTH // 2 - rect_width - 10
    rect_y = SCREEN_HEIGHT // 2 - rect_height // 2 - 50
    pygame.draw.rect(screen, WHITE, (rect_x, rect_y, rect_width, rect_height))
    pygame.draw.rect(screen, WHITE, (rect_x + rect_width + 20, rect_y, rect_width, rect_height))

    # Draw the exit button
    exit_text = button_font.render("Exit", True, WHITE)
    exit_button_rect = pygame.Rect(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 100, 100, 50)
    pygame.draw.rect(screen, DARK_RED, exit_button_rect)
    screen.blit(exit_text, (exit_button_rect.x + (exit_button_rect.width - exit_text.get_width()) // 2, exit_button_rect.y + (exit_button_rect.height - exit_text.get_height()) // 2))

    pygame.display.flip()

def pause_menu():
    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = False  # Resume the game
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if SCREEN_WIDTH - 150 <= mouse_x <= SCREEN_WIDTH - 50 and SCREEN_HEIGHT - 100 <= mouse_y <= SCREEN_HEIGHT - 50:
                    main_menu()  # Go back to the main menu
                    return

        draw_pause_menu()

# Main Game Loop
def main():
    global player_x, player_y, player_img, facing_right, player_frame, player_frozen, freeze_start_time, freeze_cooldown

    main_menu()  # Show the main menu

    generate_maze()
    place_entities()

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    pause_menu()  # Pause the game

        if not running:
            break

        # Handle player movement
        keys = pygame.key.get_pressed()
        next_x, next_y = player_x, player_y

        if not player_frozen:
            if keys[pygame.K_UP]:
                next_y -= TILE_SIZE * PLAYER_SPEED
            if keys[pygame.K_DOWN]:
                next_y += TILE_SIZE * PLAYER_SPEED
            if keys[pygame.K_LEFT]:
                next_x -= TILE_SIZE * PLAYER_SPEED
                if facing_right:
                    player_img = pygame.transform.flip(player_idle, True, False)
                    facing_right = False
            if keys[pygame.K_RIGHT]:
                next_x += TILE_SIZE * PLAYER_SPEED
                if not facing_right:
                    player_img = player_idle
                    facing_right = True

            # Check for collisions and update position
            if not is_collision(int(next_x // TILE_SIZE), int(next_y // TILE_SIZE)):
                player_x, player_y = next_x, next_y

            # Check for obstacle collisions
            if is_obstacle_collision(player_x, player_y) and pygame.time.get_ticks() - freeze_cooldown >= 1000:
                player_frozen = True
                freeze_start_time = pygame.time.get_ticks()
                freeze_cooldown = pygame.time.get_ticks()

        # Update player animation
        if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or keys[pygame.K_UP] or keys[pygame.K_DOWN]:
            player_frame = (player_frame + 1) % 20
            if player_frame < 10:
                player_img = player_run1 if facing_right else pygame.transform.flip(player_run1, True, False)
            else:
                player_img = player_run2 if facing_right else pygame.transform.flip(player_run2, True, False)
        else:
            player_img = player_idle if facing_right else pygame.transform.flip(player_idle, True, False)

        # Check for Win Condition (Exit Reached)
        if (int(player_x // TILE_SIZE), int(player_y // TILE_SIZE)) == exit_tile:
            print("You Escaped!")
            running = False

        # Update Guards
        update_guards()

        # Update screen
        screen.fill(DARK_GREY)
        draw_floor()
        draw_maze()
        screen.blit(player_img, (player_x, player_y))

        # Refresh the display
        pygame.display.flip()
        clock.tick(FPS)

        # Check if freeze time is over
        if player_frozen and pygame.time.get_ticks() - freeze_start_time >= 3000:
            player_frozen = False

    pygame.quit()

if __name__ == "__main__":
    main()