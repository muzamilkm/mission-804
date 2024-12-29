import pygame
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT

# Colors
WHITE = (255, 255, 255)
DARK_GREY = (100, 100, 100)
DARK_RED = (139, 0, 0)
DARK_GREEN = (0, 100, 0)

class Menu:
    def __init__(self, screen, fonts, floor_img):
        self.screen = screen
        self.title_font = fonts['title']
        self.tagline_font = fonts['tagline']
        self.button_font = fonts['button']
        self.floor_img = floor_img
        self.difficulty = "Medium"

    def draw_floor(self):
        for x in range(0, SCREEN_WIDTH, 40):
            for y in range(0, SCREEN_HEIGHT, 40):
                self.screen.blit(self.floor_img, (x, y))

    def draw_menu(self, dropdown_open):
        self.draw_floor()
        player_menu = pygame.image.load('assets/images/menu_player.png')
        # ... rest of draw_menu code ...

    def main_menu(self):
        menu_running = True
        dropdown_open = False
        while menu_running:
            # ... main_menu code ...
            pass
        return self.difficulty

    def draw_pause_menu(self):
        # ... pause menu drawing code ...
        pass

    def pause_menu(self):
        # ... pause menu logic code ...
        pass
