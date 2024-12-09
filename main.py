import pygame
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

# Player Settings
PLAYER_SPEED = 5

# Load the player sprite
player_img_original = pygame.image.load("assets/images/player.png")
player_img_original = pygame.transform.scale(player_img_original, (40, 40))

# Player Position and Facing Direction
player_x, player_y = 100, 100
player_img = player_img_original
facing_right = True  # Tracks current facing direction

# Main Game Loop
def main():
    global player_x, player_y, player_img, facing_right  # Declare globals

    running = True

    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Handle player movement
        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP]:
            player_y -= PLAYER_SPEED

        if keys[pygame.K_DOWN]:
            player_y += PLAYER_SPEED

        if keys[pygame.K_LEFT]:
            player_x -= PLAYER_SPEED
            if facing_right:  # Flip if previously facing right
                player_img = pygame.transform.flip(player_img_original, True, False)
                facing_right = False

        if keys[pygame.K_RIGHT]:
            player_x += PLAYER_SPEED
            if not facing_right:  # Flip if previously facing left
                player_img = player_img_original
                facing_right = True

        # Prevent the player from moving off-screen
        player_x = max(0, min(SCREEN_WIDTH - 40, player_x))
        player_y = max(0, min(SCREEN_HEIGHT - 40, player_y))

        # Update screen
        screen.fill(GREY)

        # Draw the player sprite
        screen.blit(player_img, (player_x, player_y))

        # Refresh the display
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
