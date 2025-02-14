import pygame
import sys
from constants import *
from bounding_star import BoundingStar

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
bounding_star = BoundingStar(screen)
pygame.display.set_caption("Da Star")
clock = pygame.time.Clock()
FPS = 30

def draw():
    screen.fill(BLACK)
    bounding_star.draw()
    pygame.display.flip()

def main():
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        draw()
        clock.tick(FPS)

    # Clean up
    pygame.quit()
    sys.exit()

#himom


if __name__ == "__main__":
    main()