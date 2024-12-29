import pygame
import random

class ItemManager:
    def __init__(self, tile_size):
        self.tile_size = tile_size
        self.doors = []
        self.keys = []
        self.player_keys = 0
        self.load_images()

    def load_images(self):
        self.door_locked_img = pygame.transform.scale(
            pygame.image.load("assets/images/celldoor.png"), 
            (self.tile_size, self.tile_size)
        )
        self.door_unlocked_img = pygame.transform.scale(
            pygame.image.load("assets/images/doorholder.png"), 
            (self.tile_size, self.tile_size)
        )
        self.key_img = pygame.transform.scale(
            pygame.image.load("assets/images/keyblue.png"), 
            (self.tile_size, self.tile_size)
        )

    def find_all_paths_to_exit(self, maze, start, end, astar_fn):
        """Find multiple paths to the exit using variations of A*"""
        paths = []
        # Get initial optimal path
        main_path = astar_fn(start, end)
        if main_path:
            paths.append(main_path)

        # Find alternative paths by temporarily blocking some cells from the main path
        for _ in range(3):  # Try to find 3 alternative paths
            if not main_path:
                break
            # Make a copy of the maze
            temp_maze = [row[:] for row in maze]
            # Block some random cells from the main path
            block_points = random.sample(main_path[1:-1], min(3, len(main_path) - 2))
            for x, y in block_points:
                temp_maze[y][x] = 1
            # Find alternative path with blocked cells
            alt_path = astar_fn(start, end, temp_maze)
            if alt_path and alt_path not in paths:
                paths.append(alt_path)
        
        return paths

    def place_doors_and_keys(self, maze, start, end, num_doors, empty_cells, astar_fn):
        """Place doors along multiple paths and keys in accessible locations"""
        paths = self.find_all_paths_to_exit(maze, start, end, astar_fn)
        
        # Collect all potential door positions from all paths
        all_path_cells = set()
        for path in paths:
            all_path_cells.update(path[1:-1])  # Exclude start and end points
        
        # Select door positions from all available path cells
        door_positions = random.sample(list(all_path_cells), min(num_doors, len(all_path_cells)))
        self.doors = [(x, y, True) for x, y in door_positions]
        
        # Update empty cells and place keys
        empty_cells = [(x, y) for x, y in empty_cells if (x, y) not in door_positions]
        self.keys = random.sample(empty_cells, num_doors)
        
        return empty_cells

    def collect_key(self, x, y):
        for kx, ky in self.keys:
            if (x, y) == (kx, ky):
                self.keys.remove((kx, ky))
                self.player_keys += 1
                return True
        return False

    def unlock_door(self, x, y):
        for i, (dx, dy, locked) in enumerate(self.doors):
            if locked and (x, y) == (dx, dy) and self.player_keys > 0:
                self.doors[i] = (dx, dy, False)
                self.player_keys -= 1
                return True
        return False

    def draw(self, screen):
        for dx, dy, locked in self.doors:
            door_img = self.door_locked_img if locked else self.door_unlocked_img
            screen.blit(door_img, (dx * self.tile_size, dy * self.tile_size))
        
        for kx, ky in self.keys:
            screen.blit(self.key_img, (kx * self.tile_size, ky * self.tile_size))
