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
GREY = (140, 140, 140)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Adjust Game Settings
TILE_SIZE = 20  # Reduced block size for finer grid
ROWS, COLS = SCREEN_HEIGHT // TILE_SIZE, SCREEN_WIDTH // TILE_SIZE
exit_tile = (COLS - 2, ROWS - 2)  
PLAYER_SPEED = 0.25  # Further slowed down player speed
GUARD_SPEED = 0.05  # Further slowed down guard speed
FPS = 30  # Reduced frame rate

# Load Assets
player_img_original = pygame.image.load("assets/images/player.png")
player_img_original = pygame.transform.scale(player_img_original, (TILE_SIZE, TILE_SIZE))

floor_img = pygame.image.load("assets/images/floor.jpg")
floor_img = pygame.transform.scale(floor_img, (TILE_SIZE, TILE_SIZE))

wall_img = pygame.image.load("assets/images/wall.png")
wall_img = pygame.transform.scale(wall_img, (TILE_SIZE, TILE_SIZE))

# Player Position and Facing Direction
player_x, player_y = TILE_SIZE, TILE_SIZE
player_img = player_img_original
facing_right = True

# Maze, Guards, Obstacles, and Exit
maze = []
guards = []
obstacles = []
# exit_tile = (COLS - 2, ROWS - 2)


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
        for _ in range((ROWS * COLS) // 8):  # Add ~12.5% extra connections
            x, y = random.randint(1, COLS - 2), random.randint(1, ROWS - 2)
            if maze[y][x] == 1:  # If it's a wall
                neighbors = [
                    (x + dx, y + dy) for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]
                    if 0 <= x + dx < COLS and 0 <= y + dy < ROWS and maze[y + dy][x + dx] == 0
                ]
                if len(neighbors) >= 2:  # Only connect if two or more paths exist
                    maze[y][x] = 0

    add_connections()

    # Add Checkpoints for Longer Gameplay
    for _ in range(3):  # Place 3 checkpoints
        x, y = random.randint(1, COLS - 2), random.randint(1, ROWS - 2)
        if maze[y][x] == 0:
            maze[y][x] = 2  # Mark checkpoint with a 2

    # Ensure the bottom row is filled with walls
    for x in range(COLS):
        maze[ROWS - 1][x] = 1


# Function to Place Guards and Obstacles
def place_entities():
    global guards, obstacles
    guards = []
    obstacles = []

    empty_cells = [(x, y) for y in range(ROWS) for x in range(COLS) if maze[y][x] == 0]

    # Divide the map into regions and place guards in each region
    region_size = (ROWS * COLS) // 20
    regions = [empty_cells[i:i + region_size] for i in range(0, len(empty_cells), region_size)]

    for region in regions:
        if region:
            x, y = random.choice(region)
            route = []
            current_x, current_y = x, y

            # Generate patrol route with valid moves
            for _ in range(15):  # Increase patrol steps to 10
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

    for _ in range(5):  # Place 5 obstacles
        x, y = random.choice(empty_cells)
        obstacles.append((x, y))
        empty_cells.remove((x, y))


def draw_maze():
    for y in range(ROWS):
        for x in range(COLS):
            if maze[y][x] == 1:  # Wall
                screen.blit(wall_img, (x * TILE_SIZE, y * TILE_SIZE))
            elif maze[y][x] == 2:  # Checkpoint
                pygame.draw.rect(screen, GREEN, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

    for guard in guards:
        gx, gy = guard["pos"]
        pygame.draw.rect(screen, RED, (gx * TILE_SIZE, gy * TILE_SIZE, TILE_SIZE, TILE_SIZE))

    for ox, oy in obstacles:
        pygame.draw.rect(screen, BLACK, (ox * TILE_SIZE, oy * TILE_SIZE, TILE_SIZE, TILE_SIZE))

    # Draw the Exit Tile
    ex, ey = exit_tile
    pygame.draw.rect(screen, (0, 128, 255), (ex * TILE_SIZE, ey * TILE_SIZE, TILE_SIZE, TILE_SIZE))  # Blue Exit

# Collision Checking
def is_collision(x, y):
    return maze[y][x] == 1


def update_guards():
    for guard in guards:
        current_pos = guard["route"][guard["route_index"]]
        next_index = (guard["route_index"] + guard["direction"]) % len(guard["route"])
        next_pos = guard["route"][next_index]

        if not is_collision(next_pos[0], next_pos[1]):
            guard["progress"] += GUARD_SPEED
            guard["progress"] = min(guard["progress"], 1)  # Clamp progress to 1
            guard["pos"] = (
                current_pos[0] + (next_pos[0] - current_pos[0]) * guard["progress"],
                current_pos[1] + (next_pos[1] - current_pos[1]) * guard["progress"]
            )

            # Update index when guard reaches next position
            if guard["progress"] >= 1:
                guard["route_index"] = next_index
                guard["progress"] = 0
        else:
            guard["direction"] *= -1  # Reverse direction if next position is blocked
            guard["route_index"] = (guard["route_index"] + guard["direction"]) % len(guard["route"])
            guard["progress"] = 0


# Main Game Loop
def main():
    global player_x, player_y, player_img, facing_right

    generate_maze()
    place_entities()

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Handle player movement
        keys = pygame.key.get_pressed()
        next_x, next_y = player_x, player_y

        if keys[pygame.K_UP]:
            next_y -= TILE_SIZE * PLAYER_SPEED
        if keys[pygame.K_DOWN]:
            next_y += TILE_SIZE * PLAYER_SPEED
        if keys[pygame.K_LEFT]:
            next_x -= TILE_SIZE * PLAYER_SPEED
            if facing_right:
                player_img = pygame.transform.flip(player_img_original, True, False)
                facing_right = False
        if keys[pygame.K_RIGHT]:
            next_x += TILE_SIZE * PLAYER_SPEED
            if not facing_right:
                player_img = player_img_original
                facing_right = True

        # Check for collisions
        if not is_collision(int(next_x // TILE_SIZE), int(next_y // TILE_SIZE)):
            player_x, player_y = next_x, next_y

        # Check for Win Condition (Exit Reached)
        if (int(player_x // TILE_SIZE), int(player_y // TILE_SIZE)) == exit_tile:
            print("You Escaped!")
            running = False

        # Update Guards
        update_guards()

        # Update screen
        screen.fill(GREY)
        draw_floor()
        draw_maze()
        screen.blit(player_img, (player_x, player_y))

        # Refresh the display
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()