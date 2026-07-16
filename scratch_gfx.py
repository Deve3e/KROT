import pygame
import pygame.gfxdraw
import sys

pygame.init()
screen = pygame.display.set_mode((400, 400))
pygame.display.set_caption("Texture Test")

# Create a sample texture
tex = pygame.Surface((100, 100))
tex.fill((200, 0, 0))
pygame.draw.line(tex, (0, 255, 0), (0, 0), (100, 100), 5)
pygame.draw.line(tex, (0, 0, 255), (0, 100), (100, 0), 5)

points = [(150, 150), (300, 100), (250, 300), (100, 250)]
min_x = min(p[0] for p in points)
min_y = min(p[1] for p in points)
max_x = max(p[0] for p in points)
max_y = max(p[1] for p in points)
w = int(max_x - min_x)
h = int(max_y - min_y)

scaled_tex = pygame.transform.scale(tex, (w, h))

screen.fill((0, 0, 0))
# textured_polygon signature: surface, points, texture, tx, ty
pygame.gfxdraw.textured_polygon(screen, points, scaled_tex, int(-min_x), int(-min_y))
pygame.display.flip()

import time
time.sleep(1)
pygame.quit()
sys.exit()
