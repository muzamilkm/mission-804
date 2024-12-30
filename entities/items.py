import pygame
import random
from collections import deque

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

    def find_player_region(self, maze, start_pos, distance=5):
        """Find cells within player's initial region using BFS"""
        rows, cols = len(maze), len(maze[0])
        visited = set()
        queue = deque([(start_pos)])
        player_region = set()

        while queue:
            x, y = queue.popleft()
            if (x, y) not in visited:
                visited.add((x, y))
                if self.manhattan_distance(start_pos, (x, y)) <= distance:
                    player_region.add((x, y))
                    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                        nx, ny = x + dx, y + dy
                        if (0 <= nx < cols and 0 <= ny < rows and 
                            maze[ny][nx] == 0 and 
                            (nx, ny) not in visited):
                            queue.append((nx, ny))
        return player_region

    def find_optimal_paths(self, maze, start, end, pathfinding_func):
        """Find multiple optimal and near-optimal paths using the provided pathfinding function"""
        base_path = pathfinding_func(start, end, maze)
        paths = [base_path]
        
        # Create temporary maze copies to find alternative paths
        temp_maze = [row[:] for row in maze]
        for _ in range(2):  # Find 2 alternative paths
            if not base_path:
                break
            # Block a random point in the previous path to force an alternative
            if len(base_path) > 2:  # Avoid blocking start/end points
                block_point = random.choice(base_path[1:-1])
                temp_maze[block_point[1]][block_point[0]] = 1
                alt_path = pathfinding_func(start, end, temp_maze)
                if alt_path:
                    paths.append(alt_path)
        
        return paths

    def find_door_locations(self, paths, player_region, num_doors=3):
        """Find strategic door locations along paths outside player region"""
        door_locations = []
        all_path_points = set()
        for path in paths:
            all_path_points.update(path)

        # Filter points that are outside player region and on paths
        candidate_points = [p for p in all_path_points if p not in player_region]
        
        # Sort by distance from player region for better distribution
        candidate_points.sort(key=lambda p: min(self.manhattan_distance(p, pr) for pr in player_region))
        
        # Select door locations ensuring minimum spacing
        min_spacing = 4  # Minimum tiles between doors
        for point in candidate_points:
            if len(door_locations) >= num_doors:
                break
            if all(self.manhattan_distance(point, d) >= min_spacing for d in door_locations):
                door_locations.append(point)
        
        return door_locations

    def find_key_locations(self, maze, player_region, door_locations, num_keys):
        """Place keys strategically - at least one somewhat close to player"""
        key_locations = []
        empty_cells = [(x, y) for y in range(len(maze)) for x in range(len(maze[0])) 
                      if maze[y][x] == 0 and (x, y) not in door_locations]
        
        # Find cells just outside player region for first key
        border_cells = [cell for cell in empty_cells if
                       cell not in player_region and
                       any(self.manhattan_distance(cell, pr) <= 3 for pr in player_region)]
        
        if border_cells:
            # Place first key in accessible location near player region
            first_key = random.choice(border_cells)
            key_locations.append(first_key)
            empty_cells.remove(first_key)
        
        # Place remaining keys
        cells_by_distance = sorted(empty_cells, 
                                 key=lambda c: min(self.manhattan_distance(c, d) for d in door_locations))
        
        for _ in range(num_keys - 1):
            if cells_by_distance:
                # Select from middle portion of sorted cells for balanced distribution
                mid_start = len(cells_by_distance) // 3
                mid_end = 2 * len(cells_by_distance) // 3
                key_pos = random.choice(cells_by_distance[mid_start:mid_end])
                key_locations.append(key_pos)
                cells_by_distance.remove(key_pos)
        
        return key_locations

    def manhattan_distance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def place_doors_and_keys(self, maze, start, exit_tile, num_guards, empty_cells, pathfinding_func):
        """Enhanced door and key placement with improved distribution"""
        # Find player's initial region
        player_region = self.find_player_region(maze, start)
        
        # Find optimal paths
        optimal_paths = self.find_optimal_paths(maze, start, exit_tile, pathfinding_func)
        
        # Place doors strategically
        num_doors = min(3, len(empty_cells) // 10)  # Scale doors with maze size
        door_locations = self.find_door_locations(optimal_paths, player_region, num_doors)
        self.doors = [(x, y, True) for x, y in door_locations]  # All doors start locked
        
        # Place keys strategically
        key_locations = self.find_key_locations(maze, player_region, door_locations, num_doors)
        self.keys = key_locations
        
        # Update empty cells
        used_cells = set(door_locations + key_locations)
        empty_cells = [cell for cell in empty_cells if cell not in used_cells]
        
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
