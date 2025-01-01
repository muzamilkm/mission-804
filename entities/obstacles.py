import pygame
import random
import math

class ObstacleManager:
    def __init__(self, tile_size):
        self.tile_size = tile_size
        self.obstacles = []
        self.load_images()

    def load_images(self):
        self.obstacle_images = []
        image_files = ['pipesblue.png', 'pipesgreen.png', 'pipesred.png', 'table1.png', 'desk.png']
        for img in image_files:
            try:
                loaded_img = pygame.image.load(f"assets/images/{img}")
                scaled_img = pygame.transform.scale(loaded_img, (self.tile_size, self.tile_size))
                self.obstacle_images.append(scaled_img)
            except pygame.error as e:
                print(f"Error loading obstacle image {img}: {e}")

    def place_obstacles(self, empty_cells, min_count=2, max_count=4):
        """
        Place obstacles strategically in the maze with improved placement logic
        """
        self.obstacles = []  # Clear existing obstacles
        if not empty_cells or not self.obstacle_images:
            print("No empty cells or obstacle images available")
            return empty_cells

        # Calculate number of obstacles based on available space
        available_space = len(empty_cells)
        target_count = min(max_count, max(min_count, available_space // 20))
        
        # Create a copy of empty cells to work with
        available_cells = empty_cells.copy()
        
        # Place obstacles with minimum spacing
        min_spacing = 2  # Reduced spacing to allow more placement options
        placed_positions = set()

        for _ in range(target_count):
            if not available_cells:
                break

            # Try to place an obstacle
            for attempt in range(10):  # Limit attempts per obstacle
                if not available_cells:
                    break
                    
                pos = random.choice(available_cells)
                x, y = pos
                
                # Check if position is suitable
                is_valid = all(abs(x - px) + abs(y - py) >= min_spacing 
                             for px, py, _ in self.obstacles)
                
                if is_valid:
                    # Place obstacle
                    img = random.choice(self.obstacle_images)
                    self.obstacles.append((x, y, img))
                    placed_positions.add(pos)
                    
                    # Remove nearby cells from available cells
                    available_cells = [
                        cell for cell in available_cells
                        if abs(cell[0] - x) + abs(cell[1] - y) >= min_spacing
                    ]
                    break
                else:
                    available_cells.remove(pos)

        print(f"Placed {len(self.obstacles)} obstacles")
        
        # Return updated empty cells
        return [cell for cell in empty_cells if cell not in placed_positions]

    def is_collision(self, x, y):
        for ox, oy, _ in self.obstacles:
            if int((x + self.tile_size // 2) // self.tile_size) == ox and \
               int((y + self.tile_size // 2) // self.tile_size) == oy:
                return True
        return False

    def draw(self, screen):
        for ox, oy, img in self.obstacles:
            screen.blit(img, (ox * self.tile_size, oy * self.tile_size))
