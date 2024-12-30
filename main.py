import pygame
import random
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE
from interface.menu import Menu
from entities.obstacles import ObstacleManager
from entities.items import ItemManager
from entities.guard import GuardManager
from utils.metrics import Metrics
from ai.agents import DQN
from ai.reinforcement import QLearning

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
win_img = pygame.image.load("assets/images/win.png")

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

door_locked_img = pygame.image.load("assets/images/celldoor.png")
door_locked_img = pygame.transform.scale(door_locked_img, (TILE_SIZE, TILE_SIZE))
door_unlocked_img = pygame.image.load("assets/images/doorholder.png")
door_unlocked_img = pygame.transform.scale(door_unlocked_img, (TILE_SIZE, TILE_SIZE))

key_img = pygame.image.load("assets/images/keyblue.png")
key_img = pygame.transform.scale(key_img, (TILE_SIZE, TILE_SIZE))

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
fonts = {
    "title": title_font,
    "tagline": tagline_font,
    "button": button_font
}

# Player Position and Facing Direction
player_x, player_y = TILE_SIZE, TILE_SIZE
player_img = player_idle
facing_right = True
player_frame = 0
player_frozen = False
freeze_start_time = 0
freeze_cooldown = 0

# Maze, Guards, Obstacles, Doors, Keys, and Exit
maze = []
guards = []
obstacles = []
doors = []
keys = []
player_keys = 0
# exit_tile = (COLS - 2, ROWS - 2)

# Difficulty Settings
difficulty = "Medium"
guard_counts = {"Easy": 2, "Medium": 4, "Hard": 8}

from heapq import heappop, heappush

def astar_pathfinding(start, end, custom_maze=None):
    """Modified A* to accept custom maze for alternative path finding"""
    maze_to_use = custom_maze if custom_maze is not None else maze
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
            if 0 <= current[0] + dx < COLS and 0 <= current[1] + dy < ROWS and maze_to_use[current[1] + dy][current[0] + dx] == 0
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
item_manager = ItemManager(TILE_SIZE)

# Initialize managers
obstacle_manager = ObstacleManager(TILE_SIZE)
item_manager = ItemManager(TILE_SIZE)
guard_manager = GuardManager(TILE_SIZE, GUARD_SPEED)
menu = Menu(screen, fonts, floor_img)

def generate_maze():
    global maze, doors, keys
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

    # Place doors and keys using the ItemManager instance
    empty_cells = [(x, y) for y in range(ROWS) for x in range(COLS) 
                  if maze[y][x] == 0]
    
    empty_cells = item_manager.place_doors_and_keys(
        maze, 
        (1, 1), 
        exit_tile, 
        guard_counts[difficulty], 
        empty_cells,
        astar_pathfinding
    )
    
    # Update global doors and keys from item_manager
    global doors, keys
    doors = item_manager.doors
    keys = item_manager.keys

# Function to Place Guards and Obstacles
def place_entities():
    global guards, obstacles
    guards = []
    obstacles = []

    empty_cells = [(x, y) for y in range(ROWS) for x in range(COLS) if maze[y][x] == 0 and (x, y) not in keys and (x, y) not in [door[:2] for door in doors]]

    # Place guards based on difficulty
    empty_cells = guard_manager.place_guards(empty_cells, maze, guard_counts[difficulty])

    # Place obstacles
    empty_cells = obstacle_manager.place_obstacles(empty_cells)

def draw_maze():
    for y in range(ROWS):
        for x in range(COLS):
            if maze[y][x] == 1:  # Wall
                screen.blit(wall_img, (x * TILE_SIZE, y * TILE_SIZE))
            # Remove checkpoint drawing
            # elif maze[y][x] == 2:  # Checkpoint
            #     pygame.draw.rect(screen, DARK_GREEN, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

    for ox, oy, img in obstacles:
        screen.blit(img, (ox * TILE_SIZE, oy * TILE_SIZE))

    for dx, dy, locked in doors:
        door_img = door_locked_img if locked else door_unlocked_img
        screen.blit(door_img, (dx * TILE_SIZE, dy * TILE_SIZE))

    for kx, ky in keys:
        screen.blit(key_img, (kx * TILE_SIZE, ky * TILE_SIZE))

    # Draw the Exit Tile
    ex, ey = exit_tile
    screen.blit(exit_img, (ex * TILE_SIZE, ey * TILE_SIZE))  # Use panel.png for exit

# Collision Checking
def is_collision(x, y):
    # Only walls and locked doors block movement
    if maze[y][x] == 1:
        return True
    for dx, dy, locked in doors:
        if (x, y) == (dx, dy) and locked:  # Only locked doors block movement
            if player_keys > 0:  # If player has keys, unlock the door
                unlock_door(x, y)
                return False  # Allow movement after unlocking
            return True  # Block movement if no key
    return False

def is_obstacle_collision(x, y):
    for ox, oy, _ in obstacles:
        if int((x + TILE_SIZE // 2) // TILE_SIZE) == ox and int((y + TILE_SIZE // 2) // TILE_SIZE) == oy:
            return True
    return False

def collect_key(x, y):
    global player_keys
    for kx, ky in keys:
        if (x, y) == (kx, ky):
            keys.remove((kx, ky))
            player_keys += 1
            break

def unlock_door(x, y):
    global player_keys
    for i, (dx, dy, locked) in enumerate(doors):
        if locked and (x, y) == (dx, dy) and player_keys > 0:
            print(f"Unlocking door at ({dx}, {dy}) with key {player_keys}")
            doors[i] = (dx, dy, False)  # Unlock the door
            player_keys -= 1
            break

def update_guards():
    player_pos = (int(player_x // TILE_SIZE), int(player_y // TILE_SIZE))
    guard_manager.update(maze, player_pos, obstacles, doors)

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
    global difficulty, player_x, player_y, player_img, facing_right, player_frame, player_frozen, freeze_start_time, freeze_cooldown, player_keys
    
    # Load and play menu music
    menu_music = pygame.mixer.Sound("assets/sounds/menu.mp3")
    menu_music.play(-1)  # Loop indefinitely
    
    menu_running = True
    dropdown_open = False
    while menu_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menu_music.stop()
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if SCREEN_WIDTH // 2 - 300 <= mouse_x <= SCREEN_WIDTH // 2 - 100:
                    if SCREEN_HEIGHT // 2 + 150 <= mouse_y <= SCREEN_HEIGHT // 2 + 200:
                        # Reset game state
                        player_x, player_y = TILE_SIZE, TILE_SIZE
                        player_img = player_idle
                        facing_right = True
                        player_frame = 0
                        player_frozen = False
                        freeze_start_time = 0
                        freeze_cooldown = 0
                        player_keys = 0
                        menu_music.stop()  # Stop menu music before starting game
                        generate_maze()
                        place_entities()
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
                        menu_music.stop()
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

    # Draw the restart button
    restart_text = button_font.render("Restart", True, WHITE)
    restart_button_rect = pygame.Rect(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 160, 100, 50)
    pygame.draw.rect(screen, DARK_GREEN, restart_button_rect)
    screen.blit(restart_text, (restart_button_rect.x + (restart_button_rect.width - restart_text.get_width()) // 2, 
                             restart_button_rect.y + (restart_button_rect.height - restart_text.get_height()) // 2))

    # Draw the exit button
    exit_text = button_font.render("Exit", True, WHITE)
    exit_button_rect = pygame.Rect(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 100, 100, 50)
    pygame.draw.rect(screen, DARK_RED, exit_button_rect)
    screen.blit(exit_text, (exit_button_rect.x + (exit_button_rect.width - exit_text.get_width()) // 2,
                           exit_button_rect.y + (exit_button_rect.height - exit_text.get_height()) // 2))

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
                # Check for restart button click
                if SCREEN_WIDTH - 150 <= mouse_x <= SCREEN_WIDTH - 50 and SCREEN_HEIGHT - 160 <= mouse_y <= SCREEN_HEIGHT - 110:
                    return "RESTART"
                # Check for exit button click
                elif SCREEN_WIDTH - 150 <= mouse_x <= SCREEN_WIDTH - 50 and SCREEN_HEIGHT - 100 <= mouse_y <= SCREEN_HEIGHT - 50:
                    return "MENU"

        draw_pause_menu()
    return "CONTINUE"

def draw_win_screen():
    """Draw the winning screen with image, text and looping sound"""
    global player_x, player_y, player_img, facing_right, player_frame, player_frozen, freeze_start_time, freeze_cooldown, player_keys

    # Load and play win sound on loop
    win_sound = pygame.mixer.Sound("assets/sounds/win.mp3")
    win_sound.play(-1)  # -1 means loop indefinitely

    # Load and scale win image
    win_img = pygame.image.load("assets/images/win.png")
    img_width = SCREEN_WIDTH // 2
    img_height = int(img_width * win_img.get_height() / win_img.get_width())
    win_img = pygame.transform.scale(win_img, (img_width, img_height))

    # Load font and create text
    win_font = pygame.font.Font("assets/fonts/Early GameBoy.ttf", 30)
    win_text = win_font.render("Haqeeqi Azaadi Arhi Hai", True, WHITE)
    menu_text = button_font.render("Back to Menu", True, WHITE)

    # Create semi-transparent overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.fill(DARK_GREY)
    overlay.set_alpha(200)  # Set transparency (0-255)

    # Create menu button
    button_width = 200
    button_height = 50
    button_x = (SCREEN_WIDTH - button_width) // 2
    button_y = SCREEN_HEIGHT - 100

    waiting = True
    while waiting:
        # Draw current game state in background
        screen.fill(DARK_GREY)
        draw_floor()
        draw_maze()
        screen.blit(player_img, (player_x, player_y))
        guard_manager.draw(screen)

        # Draw semi-transparent overlay
        screen.blit(overlay, (0, 0))

        # Draw win image centered
        img_x = (SCREEN_WIDTH - img_width) // 2
        img_y = (SCREEN_HEIGHT - img_height - 150) // 2
        screen.blit(win_img, (img_x, img_y))

        # Draw win text centered below image
        text_x = (SCREEN_WIDTH - win_text.get_width()) // 2
        text_y = img_y + img_height + 30
        screen.blit(win_text, (text_x, text_y))

        # Draw menu button
        pygame.draw.rect(screen, DARK_RED, (button_x, button_y, button_width, button_height))
        menu_text_x = button_x + (button_width - menu_text.get_width()) // 2
        menu_text_y = button_y + (button_height - menu_text.get_height()) // 2
        screen.blit(menu_text, (menu_text_x, menu_text_y))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                win_sound.stop()
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if (button_x <= mouse_x <= button_x + button_width and 
                    button_y <= mouse_y <= button_y + button_height):
                    # Reset game state
                    player_x, player_y = TILE_SIZE, TILE_SIZE
                    player_img = player_idle
                    facing_right = True
                    player_frame = 0
                    player_frozen = False
                    freeze_start_time = 0
                    freeze_cooldown = 0
                    player_keys = 0
                    win_sound.stop()
                    waiting = False
                    main_menu()

def draw_lose_screen():
    """Draw the losing screen with image, text and looping sound"""
    global player_x, player_y, player_img, facing_right, player_frame, player_frozen, freeze_start_time, freeze_cooldown, player_keys

    # Load and play lose sound on loop
    lose_sound = pygame.mixer.Sound("assets/sounds/lose.mp3")
    lose_sound.play(-1)  # -1 means loop indefinitely

    # Load and scale lose image
    lose_img = pygame.image.load("assets/images/lose.png")
    img_width = SCREEN_WIDTH // 2
    img_height = int(img_width * win_img.get_height() / win_img.get_width()) + 100
    lose_img = pygame.transform.scale(lose_img, (img_width, img_height))

    # Load font and create text
    lose_font = pygame.font.Font("assets/fonts/Early GameBoy.ttf", 30)
    lose_text = lose_font.render("Mujh Se Jo Ho Sakta Tha,", True, WHITE)
    lose_text2 = lose_font.render("Mein ne Kiya", True, WHITE)
    menu_text = button_font.render("Back to Menu", True, WHITE)

    # Create semi-transparent overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.fill(DARK_GREY)
    overlay.set_alpha(200)  # Set transparency (0-255)

    # Create restart button
    button_width = 200
    button_height = 50
    restart_button_x = (SCREEN_WIDTH - button_width) // 2 - 120
    restart_button_y = SCREEN_HEIGHT - 100

    # Create menu button (adjusted position)
    menu_button_x = (SCREEN_WIDTH - button_width) // 2 + 120
    menu_button_y = SCREEN_HEIGHT - 100

    waiting = True
    while waiting:
        # Draw current game state in background
        screen.fill(DARK_GREY)
        draw_floor()
        draw_maze()
        screen.blit(player_img, (player_x, player_y))
        guard_manager.draw(screen)

        # Draw semi-transparent overlay
        screen.blit(overlay, (0, 0))

        # Draw lose image centered
        img_x = (SCREEN_WIDTH - img_width) // 2
        img_y = (SCREEN_HEIGHT - img_height - 150) // 2
        screen.blit(lose_img, (img_x, img_y))

        # Draw lose text centered below image
        text_x = (SCREEN_WIDTH - lose_text.get_width()) // 2
        text_y = img_y + img_height + 30
        screen.blit(lose_text, (text_x, text_y))
        screen.blit(lose_text2, (text_x + 140, text_y + 30))

        # Draw restart button
        pygame.draw.rect(screen, DARK_GREEN, (restart_button_x, restart_button_y, button_width, button_height))
        restart_text = button_font.render("Restart", True, WHITE)
        restart_text_x = restart_button_x + (button_width - restart_text.get_width()) // 2
        restart_text_y = restart_button_y + (button_height - restart_text.get_height()) // 2
        screen.blit(restart_text, (restart_text_x, restart_text_y))

        # Draw menu button
        pygame.draw.rect(screen, DARK_RED, (menu_button_x, menu_button_y, button_width, button_height))
        menu_text_x = menu_button_x + (button_width - menu_text.get_width()) // 2
        menu_text_y = menu_button_y + (button_height - menu_text.get_height()) // 2
        screen.blit(menu_text, (menu_text_x, menu_text_y))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                lose_sound.stop()
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if (restart_button_x <= mouse_x <= restart_button_x + button_width and 
                    restart_button_y <= mouse_y <= restart_button_y + button_height):
                    lose_sound.stop()
                    return "RESTART"
                elif (menu_button_x <= mouse_x <= menu_button_x + button_width and 
                    menu_button_y <= mouse_y <= menu_button_y + button_height):
                    lose_sound.stop()
                    return "MENU"

def check_guard_collision():
    # Get player hitbox (use a slightly smaller box than the tile size)
    player_rect = pygame.Rect(
        player_x + 5, 
        player_y + 5, 
        TILE_SIZE - 10, 
        TILE_SIZE - 10
    )
    
    # Check collision with each guard
    for guard in guard_manager.guards:
        guard_x = guard["pos"][0] * TILE_SIZE
        guard_y = guard["pos"][1] * TILE_SIZE
        guard_rect = pygame.Rect(
            guard_x + 5,
            guard_y + 5,
            TILE_SIZE - 10,
            TILE_SIZE - 10
        )
        
        if player_rect.colliderect(guard_rect):
            return True
    
    return False

def reset_game_state():
    """Reset all game state variables"""
    global player_x, player_y, player_img, facing_right, player_frame
    global player_frozen, freeze_start_time, freeze_cooldown, player_keys
    global maze, doors, keys, guards, obstacles
    
    # Reset player state
    player_x, player_y = TILE_SIZE, TILE_SIZE
    player_img = player_idle
    facing_right = True
    player_frame = 0
    player_frozen = False
    freeze_start_time = 0
    freeze_cooldown = 0
    player_keys = 0
    
    # Reset game entities
    maze = []
    doors = []
    keys = []
    guards = []
    obstacles = []
    
    # Regenerate game state
    generate_maze()
    place_entities()

# Initialize metrics
metrics = Metrics()

# Initialize DQN agent
dqn_agent = DQN(input_dim=10, output_dim=4)  # Example dimensions

# Initialize QLearning agent
qlearning_agent = QLearning()

def game_loop():
    """Separate game loop function that can be reset and restarted"""
    global player_x, player_y, player_img, facing_right, player_frame
    global player_frozen, freeze_start_time, freeze_cooldown

    # Initial setup
    reset_game_state()
    metrics.start_timer()  # Start the timer

    # Start game music
    game_music = pygame.mixer.Sound("assets/sounds/game.mp3")
    game_music.play(-1)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_music.stop()
                return "QUIT"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    game_music.stop()
                    result = pause_menu()
                    if result == "MENU":
                        return "MENU"
                    elif result == "RESTART":
                        reset_game_state()
                    game_music.play(-1)

        # Check for guard collision
        if check_guard_collision():
            metrics.record_interception()  # Record interception
            metrics.stop_timer()  # Stop the timer
            game_music.stop()
            result = draw_lose_screen()
            if result == "MENU":
                metrics.print_metrics()  # Print metrics
                dqn_agent.print_efficiency_metrics()  # Print DQN efficiency metrics
                qlearning_agent.print_efficiency_metrics()  # Print QLearning efficiency metrics
                return "MENU"
            elif result == "RESTART":
                reset_game_state()  # Use the new reset function
                metrics.start_timer()  # Restart the timer
                game_music.play(-1)
                continue

        # Handle player movement and game logic
        keys = pygame.key.get_pressed()
        next_x, next_y = player_x, player_y

        if not player_frozen:
            # Handle movement
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

            # Collect keys and unlock doors
            collect_key(int(player_x // TILE_SIZE), int(player_y // TILE_SIZE))
            unlock_door(int(player_x // TILE_SIZE), int(player_y // TILE_SIZE))

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
            metrics.stop_timer()  # Stop the timer
            game_music.stop()
            print("You Escaped!")
            draw_win_screen()
            metrics.print_metrics()  # Print metrics
            dqn_agent.print_efficiency_metrics()  # Print DQN efficiency metrics
            qlearning_agent.print_efficiency_metrics()  # Print QLearning efficiency metrics
            return "MENU"

        # Update everything else
        update_guards()
        
        # Draw everything
        screen.fill(DARK_GREY)
        draw_floor()
        draw_maze()
        screen.blit(player_img, (player_x, player_y))
        guard_manager.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

        # Check if freeze time is over
        if player_frozen and pygame.time.get_ticks() - freeze_start_time >= 3000:
            player_frozen = False

        # Record average distance to player
        player_pos = (int(player_x // TILE_SIZE), int(player_y // TILE_SIZE))
        for guard in guard_manager.guards:
            guard_pos = guard["pos"]
            distance = abs(guard_pos[0] - player_pos[0]) + abs(guard_pos[1] - player_pos[1])
            metrics.record_distance(distance)

    return "QUIT"

def main():
    """Main game loop that handles the high-level game flow"""
    running = True
    while running:
        main_menu()  # Show the main menu
        
        # Start a new game
        result = game_loop()
        
        if result == "QUIT":
            running = False
        # If result is "MENU", the loop continues and shows the menu again

    pygame.quit()

if __name__ == "__main__":
    main()
