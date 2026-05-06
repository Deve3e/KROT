#!/usr/bin/env python3
"""
Texture generator for KROT game blocks.
Run this script to generate placeholder textures for the game.
"""

import pygame
import os

def create_texture(block_type, color, pattern=None):
    """Create a 32x32 texture for a block type"""
    surface = pygame.Surface((32, 32))

    # Fill with base color
    surface.fill(color)

    # Add pattern if specified
    if pattern == "grass":
        # Add some green dots for grass texture
        for i in range(0, 32, 4):
            for j in range(0, 32, 4):
                if (i + j) % 8 == 0:
                    pygame.draw.circle(surface, (80, 120, 40), (i, j), 1)
    elif pattern == "soil":
        # Add some darker spots for soil texture
        for i in range(0, 32, 6):
            for j in range(0, 32, 6):
                pygame.draw.circle(surface, (100, 60, 20), (i, j), 2)
    elif pattern == "plant":
        # Add some leaf-like patterns
        pygame.draw.ellipse(surface, (150, 80, 30), (8, 8, 16, 20))
        pygame.draw.ellipse(surface, (120, 60, 20), (6, 12, 20, 12))

    return surface

def main():
    pygame.init()

    # Create textures directory if it doesn't exist
    os.makedirs("game/textures", exist_ok=True)

    textures = {
        "soil.png": ((120, 80, 40), "soil"),
        "grass.png": ((100, 150, 60), "grass"),
        "plant.png": ((200, 100, 50), "plant"),
        "sky.png": ((135, 206, 235), None)
    }

    for filename, (color, pattern) in textures.items():
        texture = create_texture(filename.split('.')[0], color, pattern)
        pygame.image.save(texture, f"game/textures/{filename}")
        print(f"Generated texture: {filename}")

    print("\nTexture generation complete!")
    print("You can now replace these placeholder textures with your own images.")
    print("Supported formats: PNG, JPG, BMP")
    print("Recommended size: 32x32 or 64x64 pixels")

if __name__ == "__main__":
    main()