import pygame
import time

pygame.init()
screen = pygame.Surface((800, 600))
clock = pygame.time.Clock()

start = time.time()
frames = 0
while frames < 60:
    screen.fill((0, 0, 0))
    for i in range(20000):
        pygame.draw.polygon(screen, (255, 0, 0), [(10, 10), (20, 10), (20, 20), (10, 20)])
    frames += 1

print("FPS:", 60 / (time.time() - start))
