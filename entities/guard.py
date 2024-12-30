import pygame
import random
import math
from ai.agents import GuardAgent

class GuardManager:
    def __init__(self, tile_size, guard_speed):
        self.tile_size = tile_size
        self.guard_speed = guard_speed
        self.guards = []
        self.guard_agents = []
        self.load_images()

    def load_images(self):
        self.guard_idle = pygame.transform.scale(
            pygame.image.load("assets/images/copidle.png"), 
            (self.tile_size, self.tile_size)
        )
        self.guard_run1 = pygame.transform.scale(
            pygame.image.load("assets/images/coprun1.png"), 
            (self.tile_size, self.tile_size)
        )
        self.guard_run2 = pygame.transform.scale(
            pygame.image.load("assets/images/coprun2.png"), 
            (self.tile_size, self.tile_size)
        )

    def place_guards(self, empty_cells, maze, num_guards):
        self.guards = []
        self.guard_agents = []
        maze_size = (len(maze[0]), len(maze))
        
        # Define minimum distance from start (top-left)
        min_distance = 10  # Minimum 10 tiles away from start
        start_pos = (1, 1)  # Player starting position
        
        # Filter cells that are far enough from start
        safe_cells = [
            (x, y) for x, y in empty_cells 
            if abs(x - start_pos[0]) + abs(y - start_pos[1]) >= min_distance
        ]
        
        # If we don't have enough safe cells, use cells that are as far as possible
        if len(safe_cells) < num_guards:
            # Sort cells by distance from start
            empty_cells.sort(
                key=lambda pos: -(abs(pos[0] - start_pos[0]) + abs(pos[1] - start_pos[1]))
            )
            safe_cells = empty_cells[:num_guards]
        
        for _ in range(num_guards):
            if safe_cells:
                x, y = random.choice(safe_cells)
                guard = {
                    "pos": (x, y),
                    "facing_left": False,
                    "current_path": [],
                    "target_pos": None
                }
                self.guards.append(guard)
                self.guard_agents.append(GuardAgent((x, y), maze_size))
                safe_cells.remove((x, y))
                empty_cells.remove((x, y))
                print(f"Placed guard at ({x}, {y})")
        
        return empty_cells

    def update(self, maze, player_pos, obstacles, doors):
        walls = [(x, y) for y, row in enumerate(maze) 
                for x, cell in enumerate(row) if cell == 1]

        for guard, agent in zip(self.guards, self.guard_agents):
            curr_x, curr_y = guard["pos"]
            
            # Get path to player if needed
            if not guard["current_path"]:
                guard["current_path"] = agent.find_path_to_player(
                    (int(curr_x), int(curr_y)),
                    player_pos,
                    walls
                )

            # Move along path
            if guard["current_path"]:
                next_x, next_y = guard["current_path"][0]
                
                # Calculate movement direction
                dx = next_x - curr_x
                dy = next_y - curr_y
                
                # Update facing direction
                if dx != 0:
                    guard["facing_left"] = dx < 0

                # Move if not blocked by wall
                new_x = curr_x + (self.guard_speed if dx > 0 else -self.guard_speed if dx < 0 else 0)
                new_y = curr_y + (self.guard_speed if dy > 0 else -self.guard_speed if dy < 0 else 0)
                
                # Check if reached next path point
                if abs(new_x - next_x) < self.guard_speed and abs(new_y - next_y) < self.guard_speed:
                    guard["pos"] = (next_x, next_y)
                    guard["current_path"].pop(0)
                else:
                    # Check wall collision before moving
                    new_tile_x = int(new_x)
                    new_tile_y = int(new_y)
                    if (new_tile_x, new_tile_y) not in walls:
                        guard["pos"] = (new_x, new_y)
                    else:
                        # Path is blocked, recalculate
                        guard["current_path"] = []

    def draw(self, screen):
        for guard in self.guards:
            x, y = guard["pos"]
            guard_img = self.guard_idle if guard["facing_left"] else \
                       pygame.transform.flip(self.guard_idle, True, False)
            screen.blit(guard_img, (int(x * self.tile_size), int(y * self.tile_size)))
