import pygame
import random

class ObstacleManager:
    def __init__(self, tile_size):
        self.tile_size = tile_size
        self.obstacles = []
        self.load_images()

    def load_images(self):
        self.obstacle_images = [
            pygame.transform.scale(pygame.image.load(f"assets/images/{img}"), (self.tile_size, self.tile_size))
            for img in ['pipesblue.png', 'pipesgreen.png', 'pipesred.png', 'table1.png', 'desk.png']
        ]

    def place_obstacles(self, empty_cells, count=2):
        self.obstacles = []
        for _ in range(count):
            if empty_cells:
                x, y = random.choice(empty_cells)
                self.obstacles.append((x, y, random.choice(self.obstacle_images)))
                empty_cells.remove((x, y))
        return empty_cells

    def is_collision(self, x, y):
        for ox, oy, _ in self.obstacles:
            if int((x + self.tile_size // 2) // self.tile_size) == ox and \
               int((y + self.tile_size // 2) // self.tile_size) == oy:
                return True
        return False

    def draw(self, screen):
        for ox, oy, img in self.obstacles:
            screen.blit(img, (ox * self.tile_size, oy * self.tile_size))
