import pygame
import time

try:
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("Test")
    print("Window opened successfully.")
    time.sleep(2)
except Exception as e:
    import traceback
    traceback.print_exc()
