import pygame
import random

class GuardManager:
    def __init__(self, tile_size, guard_speed):
        self.tile_size = tile_size
        self.guard_speed = guard_speed
        self.guards = []
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
        for _ in range(num_guards):
            if empty_cells:
                x, y = random.choice(empty_cells)
                route = self.generate_patrol_route(x, y, maze)
                if route:
                    self.guards.append({
                        "pos": (x, y),
                        "route": route,
                        "route_index": 0,
                        "direction": 1,
                        "progress": 0,
                        "facing_left": False
                    })
                empty_cells.remove((x, y))
        return empty_cells

    def generate_patrol_route(self, x, y, maze):
        # ... patrol route generation code ...
        pass

    def update(self, astar_pathfinding):
        # ... guard update code ...
        pass

    def draw(self, screen):
        for guard in self.guards:
            gx, gy = guard["pos"]
            guard_img = self.guard_idle if guard["progress"] == 0 else \
                       (self.guard_run1 if guard["progress"] < 0.5 else self.guard_run2)
            
            if guard.get("facing_left", False):
                guard_img = pygame.transform.flip(guard_img, True, False)
            
            screen.blit(guard_img, (gx * self.tile_size, gy * self.tile_size))
