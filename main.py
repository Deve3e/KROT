# pyrefly: ignore [missing-import]
import pygame
import sys
import math
import os
import random
from enum import Enum
from typing import Optional

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# Colors
BG_COLOR = (34, 34, 34)  # Dark gray
GRASS_GREEN = (76, 175, 80)  # Green for grass theme
SOIL_BROWN = (139, 69, 19)  # Brown for soil
TEXT_WHITE = (255, 255, 255)
ACCENT_ORANGE = (255, 165, 0)  # Orange for accents
BUTTON_HOVER = (255, 154, 66)  # Bright gold on hover

# Playful button color themes: (base_color, shadow_color, outline_color, text_color)
BUTTON_THEMES = {
    "play":         ((60, 200, 80),   (20, 100, 30),  (20, 160, 50),   (255, 255, 255)),
    "instructions": ((60, 140, 230),  (20, 60, 140),  (30, 100, 200),  (255, 255, 255)),
    "settings":     ((160, 80, 220),  (80, 30, 130),  (130, 50, 190),  (255, 255, 255)),
    "resume":       ((60, 200, 80),   (20, 100, 30),  (20, 160, 50),   (255, 255, 255)),
    "play_again":   ((255, 180, 0),   (140, 80, 0),   (210, 130, 0),   (60, 30, 0)),
    "exit":         ((220, 60, 60),   (110, 20, 20),  (180, 30, 30),   (255, 255, 255)),
    "back":         ((100, 180, 220), (30, 80, 120),  (60, 140, 190),  (255, 255, 255)),
    "default":      ((255, 190, 80),  (140, 80, 10),  (210, 130, 20),  (50, 20, 0)),
}


class TextureManager:
    """Manages block textures for 2D rendering"""
    def __init__(self, block_size: int = 40):
        self.textures = {}   # block_type -> pygame.Surface  (primary/fallback)
        self.variants = {}   # block_type -> [pygame.Surface, ...]  (all variants incl. primary)
        self.block_size = block_size
        self.load_textures()
    
    def load_textures(self) -> None:
        """Load textures from textures/ folder"""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        texture_files = {
            "soil":       os.path.join(base_dir, "textures", "soil.png"),
            "grass":      os.path.join(base_dir, "textures", "grass.png"),
            "plant":      os.path.join(base_dir, "textures", "plant.png"),
            "sky":        os.path.join(base_dir, "textures", "sky.png"),
            "gardener":   os.path.join(base_dir, "textures", "gardener.png"),
            "stone":      os.path.join(base_dir, "textures", "stone.png"),
            "player":     os.path.join(base_dir, "textures", "player.png"),
            "snake_head": os.path.join(base_dir, "textures", "snake_head.png"),
            "snake_tail": os.path.join(base_dir, "textures", "snake_tail.png"),
        }
        
        for block_type, file_path in texture_files.items():
            try:
                texture = pygame.image.load(file_path)
                texture = texture.convert_alpha()
                texture = pygame.transform.scale(texture, (self.block_size, self.block_size))
                self.textures[block_type] = texture
                self.variants[block_type] = [texture]
                print(f"Loaded texture: {block_type}")
            except Exception as e:
                print(f"Failed to load texture {block_type}: {e}")
                fallback = self._create_fallback_texture(block_type)
                self.textures[block_type] = fallback
                self.variants[block_type] = [fallback]

        textures_dir = os.path.join(base_dir, "textures")

        # Auto-load additional soil variants: soil2.png, soil3.png, ...
        for i in range(2, 100):
            path = os.path.join(textures_dir, f"soil{i}.png")
            if not os.path.exists(path):
                break
            try:
                tex = pygame.image.load(path).convert_alpha()
                tex = pygame.transform.scale(tex, (self.block_size, self.block_size))
                self.variants["soil"].append(tex)
                print(f"Loaded texture: soil variant {i}")
            except Exception as e:
                print(f"Failed to load soil variant {i}: {e}")
                break

        # Auto-load snake body variants: snake_body1.png, snake_body2.png, ...
        # At least one must exist; keep scanning until a file is missing.
        self.variants["snake_body"] = []
        for i in range(1, 100):
            path = os.path.join(textures_dir, f"snake_body{i}.png")
            if not os.path.exists(path):
                break
            try:
                tex = pygame.image.load(path).convert_alpha()
                tex = pygame.transform.scale(tex, (self.block_size, self.block_size))
                self.variants["snake_body"].append(tex)
                print(f"Loaded texture: snake_body variant {i}")
            except Exception as e:
                print(f"Failed to load snake_body variant {i}: {e}")
                break
    
    def _create_fallback_texture(self, block_type: str) -> pygame.Surface:
        """Create a fallback colored texture if image loading fails"""
        surface = pygame.Surface((self.block_size, self.block_size))
        
        if block_type == "soil":
            surface.fill((139, 69, 19))
            pygame.draw.rect(surface, (100, 50, 10), surface.get_rect(), 2)
        elif block_type == "grass":
            surface.fill((139, 69, 19))
            pygame.draw.rect(surface, (76, 175, 80), (0, 0, self.block_size, int(self.block_size * 0.25)))
        elif block_type == "plant":
            surface.fill((200, 100, 50))
        elif block_type == "stone":
            surface.fill((120, 120, 120))  # Stone gray
            pygame.draw.rect(surface, (70, 70, 70), surface.get_rect(), 2)
            pygame.draw.line(surface, (80, 80, 80), (5, 8), (15, 12), 2)
            pygame.draw.line(surface, (80, 80, 80), (15, 12), (32, 10), 2)
            pygame.draw.line(surface, (90, 90, 90), (10, 25), (28, 30), 2)
            pygame.draw.line(surface, (90, 90, 90), (28, 30), (35, 20), 2)
        elif block_type == "gardener":
            surface.fill((220, 20, 60))  # Crimson red
            # Give him some simple eyes
            pygame.draw.rect(surface, (255, 255, 255), (10, 10, 8, 8))
            pygame.draw.rect(surface, (255, 255, 255), (22, 10, 8, 8))
            pygame.draw.rect(surface, (0, 0, 0), (12, 12, 4, 4))
            pygame.draw.rect(surface, (0, 0, 0), (24, 12, 4, 4))
        else:
            surface.fill((100, 100, 100))
        
        return surface
    
    def get_texture(self, block_type: str) -> pygame.Surface:
        """Get the primary texture for a block type."""
        return self.textures.get(block_type, self.textures.get("soil", None))

    def get_texture_variant(self, block_type: str, x: int, y: int) -> pygame.Surface:
        """Pick a texture variant deterministically from (x, y) so the same
        block always shows the same texture without storing extra data."""
        var_list = self.variants.get(block_type)
        if not var_list:
            return self.get_texture(block_type)
        # Simple spatial hash — stable across frames, visually uncorrelated
        idx = (x * 2654435761 ^ y * 2246822519) % len(var_list)
        return var_list[idx]


class ImageBackground:
    """Class to handle image background display"""
    def __init__(self, image_path: str, screen_width: int, screen_height: int):
        self.image_path = image_path
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.image_surface: Optional[pygame.Surface] = None
        self.image_loaded = False
        self.image_width = screen_width
        self.image_height = screen_height
        self.base_x = 0
        
        try:
            image = pygame.image.load(image_path)
            image = image.convert_alpha()
            image_width, image_height = image.get_size()
            if image_height != screen_height:
                scale_factor = screen_height / image_height
                image_width = int(image_width * scale_factor)
                image = pygame.transform.smoothscale(image, (image_width, screen_height))
            self.image_surface = image.convert()
            self.image_width = image_width
            self.image_height = screen_height
            self.base_x = (screen_width - image_width) // 2
            self.image_loaded = True
        except Exception as e:
            print(f"Failed to load background image: {e}")
            self.image_loaded = False


class GameState(Enum):
    """Enum for different game states"""
    HOME = 1
    INSTRUCTIONS = 2
    SETTINGS = 3
    PLAYING = 4
    PAUSED = 5
    GAME_OVER = 6
    WIN = 7


class Camera2D:
    """2D Camera that tracks an (x, y) offset"""
    def __init__(self, screen_width: int, screen_height: int, block_size: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.block_size = block_size
        self.x = 0.0
        self.y = 0.0
        
    def set_position(self, target_x: float, target_y: float) -> None:
        """Center the camera on the target (world coordinates)"""
        self.x = (target_x * self.block_size) - (self.screen_width / 2)
        self.y = (target_y * self.block_size) - (self.screen_height / 2)
        
    def world_to_screen(self, world_x: float, world_y: float) -> tuple:
        """Convert world coordinates (blocks) to screen coordinates (pixels)"""
        screen_x = (world_x * self.block_size) - self.x
        screen_y = (world_y * self.block_size) - self.y
        return (screen_x, screen_y)

    def screen_to_world(self, screen_x: float, screen_y: float) -> tuple:
        """Convert screen coordinates (pixels) to world coordinates (blocks)"""
        world_x = (screen_x + self.x) / self.block_size
        world_y = (screen_y + self.y) / self.block_size
        return (world_x, world_y)


class Terrain2D:
    """2D tile-based terrain system"""
    def __init__(self, texture_manager: TextureManager, block_size: int):
        self.texture_manager = texture_manager
        self.block_size = block_size
        self.blocks = {}  # (x, y) -> block_type
        self.particle_system: Optional['ParticleSystem'] = None
        
    def add_block(self, x: int, y: int, block_type: str = "soil") -> None:
        self.blocks[(x, y)] = block_type
    
    def remove_block(self, x: int, y: int) -> Optional[str]:
        if (x, y) in self.blocks:
            block_type = self.blocks.pop((x, y))
            if self.particle_system is not None:
                self.particle_system.spawn_break(x + 0.5, y + 0.5, block_type)
            return block_type
        return None
    
    def is_block_at(self, x: int, y: int) -> bool:
        return (x, y) in self.blocks
    
    def generate_terrain(self) -> None:
        self.blocks.clear()
        
        # Surface grass at y = 0, soil/stone below
        for x in range(-50, 51):
            for y in range(0, 16):
                if y == 0:
                    self.add_block(x, y, "grass")
                elif y == 15:
                    self.add_block(x, y, "stone")
                else:
                    # Make 3x3 area around player spawn empty
                    if -50 <= x <= -48 and 12 <= y <= 14:
                        continue
                    elif random.random() < 0.15:
                        self.add_block(x, y, "stone")
                    else:
                        self.add_block(x, y, "soil")
                    
        # Remove center area where player starts (underground cave)
        for x in range(-3, 4):
            for y in range(25, 29):
                self.remove_block(x, y)
                
        # Add some surface plants
        self.add_block(-10, -1, "plant")
        self.add_block(10, -1, "plant")
        self.add_block(-20, -1, "plant")
        self.add_block(25, -1, "plant")
    
    def draw(self, surface: pygame.Surface, camera: Camera2D) -> None:
        start_x = int(camera.x / self.block_size) - 1
        end_x = int((camera.x + camera.screen_width) / self.block_size) + 1
        start_y = int(camera.y / self.block_size) - 1
        end_y = int((camera.y + camera.screen_height) / self.block_size) + 1
        
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                if (x, y) in self.blocks:
                    block_type = self.blocks[(x, y)]
                    # Use variant lookup so different soil blocks can look distinct
                    texture = self.texture_manager.get_texture_variant(block_type, x, y)
                    screen_x, screen_y = camera.world_to_screen(x, y)
                    if texture:
                        surface.blit(texture, (screen_x, screen_y))


class Minimap:
    """Minimap to show zoomed-out 2D view"""
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
    def draw(self, surface: pygame.Surface, player: 'Player', terrain: 'Terrain2D', gardener: 'Gardener' = None, snakes: list = None) -> None:
        pygame.draw.rect(surface, (50, 25, 0), (self.x, self.y, self.width, self.height))
        pygame.draw.rect(surface, (150, 100, 50), (self.x, self.y, self.width, self.height), 2)
        
        font_small = pygame.font.Font(None, 16)
        title = font_small.render("Map", True, TEXT_WHITE)
        surface.blit(title, (self.x + 5, self.y + 2))
        
        blocks_w, blocks_h = 60, 60
        map_block_w = self.width / blocks_w
        map_block_h = self.height / blocks_h
        
        start_bx = int(player.x) - blocks_w // 2
        end_bx = int(player.x) + blocks_w // 2
        start_by = int(player.y) - blocks_h // 2
        end_by = int(player.y) + blocks_h // 2
        
        for by in range(start_by, end_by):
            for bx in range(start_bx, end_bx):
                if terrain.is_block_at(bx, by):
                    block_type = terrain.blocks[(bx, by)]
                    if block_type == "grass":
                        color = (76, 175, 80)
                    elif block_type == "stone":
                        color = (120, 120, 120)
                    else:
                        color = (100, 50, 10)
                    mx = self.x + (bx - start_bx) * map_block_w
                    my = self.y + (by - start_by) * map_block_h
                    pygame.draw.rect(surface, color, (mx, my, max(1, map_block_w), max(1, map_block_h)))
        
        player_mx = self.x + (player.x - start_bx) * map_block_w
        player_my = self.y + (player.y - start_by) * map_block_h
        pygame.draw.circle(surface, ACCENT_ORANGE, (int(player_mx), int(player_my)), 3)
        
        if gardener:
            gardener_mx = self.x + (gardener.x - start_bx) * map_block_w
            gardener_my = self.y + (gardener.y - start_by) * map_block_h
            pygame.draw.circle(surface, (255, 0, 0), (int(gardener_mx), int(gardener_my)), 3)
            
        if snakes:
            for snake in snakes:
                snake_mx = self.x + (snake.x - start_bx) * map_block_w
                snake_my = self.y + (snake.y - start_by) * map_block_h
                pygame.draw.circle(surface, (0, 255, 0), (int(snake_mx), int(snake_my)), 2)


class Player:
    """Player (Mole) class with 2D platformer movement"""
    def __init__(self, start_x: float, start_y: float, size: float = 0.8):
        self.x = start_x
        self.y = start_y
        self.width = size
        self.height = size
        
        self.speed = 0.15
        self.dig_cooldown = 0
        self.dig_timer = 0
        self.dig_target: Optional[tuple[int, int]] = None
        
        self.vy = 0.0
        self.is_on_ground = False
        
    def handle_input(self, keys, camera: Camera2D, terrain: Terrain2D, mouse_buttons, mouse_pos,
                     key_left: int = 97, key_right: int = 100,
                     key_jump: int = 119) -> bool:
        destroyed_seed = False
        dx = 0
        if keys[key_left]:
            dx -= self.speed
        if keys[key_right]:
            dx += self.speed
            
        if dx != 0:
            new_x = self.x + dx
            if not self._check_collision(new_x, self.y, terrain):
                self.x = new_x
                
        if (keys[pygame.K_SPACE] or keys[key_jump]) and self.is_on_ground:
            self.vy = -0.4
            self.is_on_ground = False
            
        if self.dig_cooldown > 0:
            self.dig_cooldown -= 1
            
        if self.dig_timer > 0:
            return False
        
        if mouse_buttons[0] and self.dig_cooldown <= 0:
            world_x, world_y = camera.screen_to_world(mouse_pos[0], mouse_pos[1])
            bx, by = int(math.floor(world_x)), int(math.floor(world_y))
            
            dist = math.hypot(self.x + self.width/2 - bx - 0.5, self.y + self.height/2 - by - 0.5)
            if terrain.is_block_at(bx, by) and terrain.blocks.get((bx, by)) == "plant":
                if dist <= 1.0:
                    self.dig_timer = 30
                    self.dig_target = (bx, by)
                    self.dig_cooldown = 30
            elif dist <= 4.0:
                if terrain.is_block_at(bx, by) and terrain.blocks.get((bx, by)) != "stone":
                    removed_block = terrain.remove_block(bx, by)
                    if removed_block == "plant":
                        return True
                    self.dig_cooldown = 15
        return False
    
    def _check_collision(self, x: float, y: float, terrain: Terrain2D) -> bool:
        margin = 0.05
        corners = [
            (x + margin, y + margin),
            (x + self.width - margin, y + margin),
            (x + margin, y + self.height - margin),
            (x + self.width - margin, y + self.height - margin)
        ]
        for cx, cy in corners:
            bx, by = int(math.floor(cx)), int(math.floor(cy))
            if terrain.is_block_at(bx, by) and terrain.blocks.get((bx, by)) != "plant":
                return True
        return False
        
    def update(self, terrain: Terrain2D) -> bool:
        destroyed_seed = False
        if self.dig_timer > 0:
            self.dig_timer -= 1
            if self.dig_timer == 0 and self.dig_target:
                bx, by = self.dig_target
                dist = math.hypot(self.x + self.width/2 - bx - 0.5, self.y + self.height/2 - by - 0.5)
                if dist <= 1.0 and terrain.is_block_at(bx, by) and terrain.blocks.get((bx, by)) == "plant":
                    terrain.remove_block(bx, by)
                    destroyed_seed = True
                self.dig_target = None
        
        GRAVITY = 0.02
        TERMINAL_VELOCITY = 0.5
        
        self.vy += GRAVITY
        if self.vy > TERMINAL_VELOCITY:
            self.vy = TERMINAL_VELOCITY
            
        new_y = self.y + self.vy
        
        if self.vy > 0:
            if self._check_collision(self.x, new_y, terrain):
                self.y = math.floor(new_y + self.height) - self.height
                self.vy = 0.0
                self.is_on_ground = True
            else:
                self.y = new_y
                self.is_on_ground = False
        elif self.vy < 0:
            if self._check_collision(self.x, new_y, terrain):
                self.y = math.ceil(new_y)
                self.vy = 0.0
            else:
                self.y = new_y
                self.is_on_ground = False
        return destroyed_seed
    
    def draw(self, surface: pygame.Surface, camera: Camera2D,
             texture_manager: Optional['TextureManager'] = None) -> None:
        screen_x, screen_y = camera.world_to_screen(self.x, self.y)
        pixel_width  = int(self.width  * camera.block_size)
        pixel_height = int(self.height * camera.block_size)

        # Try to use a player skin texture
        skin = texture_manager.get_texture("player") if texture_manager else None
        if skin:
            # Scale to the actual pixel size this frame
            scaled = pygame.transform.scale(skin, (pixel_width, pixel_height))
            # Flip when moving left (reuse last horizontal direction via vx sign)
            surface.blit(scaled, (screen_x, screen_y))
        else:
            # Fallback: orange rounded rectangle + eye
            rect = pygame.Rect(screen_x, screen_y, pixel_width, pixel_height)
            pygame.draw.rect(surface, ACCENT_ORANGE, rect, border_radius=8)
            pygame.draw.circle(surface, (0, 0, 0),
                               (int(screen_x + pixel_width * 0.7),
                                int(screen_y + pixel_height * 0.3)), 3)


class Gardener:
    """Gardener AI that patrols the surface and chases the player"""
    def __init__(self, start_x: float, start_y: float):
        self.x = start_x
        self.y = start_y
        self.width = 1.0
        self.height = 1.0
        
        self.state = "WANDER"
        self.wander_timer = 0
        self.patrol_speed = 0.05
        self.chase_speed = 0.08
        self.direction = 1
        self.vy = 0.0
        self.is_on_ground = False
        self.vision_range = 15.0
        self.climb_target_x: Optional[float] = None
        # Track where the gardener sank underground so it can climb back
        self.prev_y: float = start_y
        self.surface_return_x: Optional[float] = None
        # Timer to avoid spamming grass placement
        self.grass_repair_timer: int = 0
        
    def _check_collision(self, x: float, y: float, terrain: 'Terrain2D') -> bool:
        margin = 0.05
        corners = [
            (x + margin, y + margin),
            (x + self.width - margin, y + margin),
            (x + margin, y + self.height - margin),
            (x + self.width - margin, y + self.height - margin)
        ]
        for cx, cy in corners:
            bx, by = int(math.floor(cx)), int(math.floor(cy))
            if terrain.is_block_at(bx, by) and terrain.blocks.get((bx, by)) != "plant":
                return True
        return False

    def _is_passable_tile(self, x: int, y: int, terrain: 'Terrain2D') -> bool:
        if y < 0:
            return True
        return not terrain.is_block_at(x, y) or terrain.blocks.get((x, y)) == "plant"

    def _column_has_open_path(self, x: int, current_y: int, terrain: 'Terrain2D') -> bool:
        for ty in range(current_y, -1, -1):
            if not self._is_passable_tile(x, ty, terrain):
                return False
        return True

    def _find_surface_column(self, terrain: 'Terrain2D') -> Optional[float]:
        current_y = int(math.floor(self.y))
        start_col = int(math.floor(self.x))
        for offset in range(0, 101):
            for candidate in (start_col + offset, start_col - offset):
                if candidate < -50 or candidate > 50:
                    continue
                if self._column_has_open_path(candidate, current_y, terrain):
                    return float(candidate)
        return None
        
    def can_see(self, player: 'Player', terrain: 'Terrain2D') -> bool:
        """Check if player is on the same vertical level as the gardener"""
        return abs(self.y - player.y) < 1.5

    def _is_breakable_tile(self, x: int, y: int, terrain: 'Terrain2D') -> bool:
        if not terrain.is_block_at(x, y):
            return False
        return terrain.blocks.get((x, y)) != "stone"

    def _break_above_block(self, terrain: 'Terrain2D') -> bool:
        """Break the block directly above the gardener's head (used when blocked horizontally)."""
        above_y = int(math.floor(self.y - 0.01))
        left_x = int(math.floor(self.x + 0.1))
        right_x = int(math.floor(self.x + self.width - 0.1))
        removed = False
        for bx in (left_x, right_x):
            if self._is_breakable_tile(bx, above_y, terrain):
                terrain.remove_block(bx, above_y)
                removed = True
        return removed

    def update(self, terrain: 'Terrain2D', player: 'Player') -> None:
        # --- Track y-level increases (gardener sinking underground) ---
        if self.state != "CHASE" and self.y > self.prev_y + 0.5:
            # Gardener sank deeper; remember where this happened
            self.surface_return_x = self.x
        self.prev_y = self.y

        if self.can_see(player, terrain):
            self.state = "CHASE"
            self.wander_timer = 0
            self.climb_target_x = None
            self.surface_return_x = None
        else:
            if self.state == "CHASE":
                self.state = "WANDER"
                self.climb_target_x = None

        if self.state != "CHASE" and self.y > 2.0:
            self.state = "CLIMB"
            if self.climb_target_x is None:
                # Prefer returning to where we fell if we have that info
                if self.surface_return_x is not None:
                    self.climb_target_x = self.surface_return_x
                else:
                    self.climb_target_x = self._find_surface_column(terrain)
            else:
                current_col = int(round(self.climb_target_x))
                if not self._column_has_open_path(current_col, int(math.floor(self.y)), terrain):
                    self.climb_target_x = self._find_surface_column(terrain)

        if self.state == "WANDER":
            if self.wander_timer <= 0:
                self.direction = random.choice([-1, 1])
                self.wander_timer = random.randint(60, 180)
            else:
                self.wander_timer -= 1
        elif self.state == "CHASE":
            if player.x > self.x:
                self.direction = 1
            else:
                self.direction = -1
        elif self.state == "CLIMB":
            if self.climb_target_x is None:
                if self.wander_timer <= 0:
                    self.direction = random.choice([-1, 1])
                    self.wander_timer = random.randint(60, 180)
                else:
                    self.wander_timer -= 1
            else:
                # Navigate towards the target column
                if abs(self.x - self.climb_target_x) > 0.15:
                    self.direction = 1 if self.climb_target_x > self.x else -1
                else:
                    # Reached the target column — jump left or right to get on surface
                    self.direction = random.choice([-1, 1])
                    self.surface_return_x = None  # Clear the return target
                if self.is_on_ground:
                    above_x = int(math.floor(self.x + self.width / 2))
                    above_y = int(math.floor(self.y - 1))
                    if self._is_passable_tile(above_x, above_y, terrain):
                        self.vy = -0.4
                        self.is_on_ground = False
                    else:
                        if self._break_above_block(terrain):
                            self.vy = -0.4
                            self.is_on_ground = False
                        else:
                            self.climb_target_x = self._find_surface_column(terrain)

        # 1. Horizontal movement
        speed = self.chase_speed if self.state == "CHASE" else self.patrol_speed
        new_x = self.x + speed * self.direction
        
        # Check horizontal collision
        if not self._check_collision(new_x, self.y, terrain):
            self.x = new_x
        else:
            # When blocked horizontally, break the block ABOVE (not in front) to climb up
            if self._break_above_block(terrain):
                # Try to move into the freed space next tick; for now try the move
                if not self._check_collision(new_x, self.y, terrain):
                    self.x = new_x
                elif self.is_on_ground:
                    self.vy = -0.4
                    self.is_on_ground = False
            elif self.is_on_ground:
                self.vy = -0.4
                self.is_on_ground = False
            else:
                # Turn around if wandering and hit a wall while airborne
                if self.state == "WANDER":
                    self.direction *= -1
                    self.wander_timer = random.randint(60, 180)
        
        # Clamp gardener to map boundaries and reverse direction at edges
        if self.x < -50.0:
            self.x = -50.0
            self.direction = 1
            self.wander_timer = random.randint(60, 180)
        elif self.x > 50.0:
            self.x = 50.0
            self.direction = -1
            self.wander_timer = random.randint(60, 180)
                
        # 2. Vertical movement (Gravity)
        GRAVITY = 0.02
        TERMINAL_VELOCITY = 0.5
        
        self.vy += GRAVITY
        if self.vy > TERMINAL_VELOCITY:
            self.vy = TERMINAL_VELOCITY
            
        new_y = self.y + self.vy
        
        if self.vy > 0: # Falling
            if self._check_collision(self.x, new_y, terrain):
                self.y = math.floor(new_y + self.height) - self.height
                self.vy = 0.0
                self.is_on_ground = True
            else:
                self.y = new_y
                self.is_on_ground = False
        elif self.vy < 0: # Jumping up
            if self._check_collision(self.x, new_y, terrain):
                self.y = math.ceil(new_y)
                self.vy = 0.0
            else:
                self.y = new_y
                self.is_on_ground = False
                
        # Seed planting logic while wandering
        if self.state == "WANDER" and self.is_on_ground:
            bx = int(math.floor(self.x + self.width / 2))
            by = int(math.floor(self.y))
            if not terrain.is_block_at(bx, by) and terrain.is_block_at(bx, by + 1):
                if random.random() < 0.005:
                    terrain.add_block(bx, by, "plant")

        # Grass repair logic: when not chasing, check the block diagonally below (same
        # row as the ground the gardener stands on, one tile to the side) and restore it.
        if self.state != "CHASE" and self.is_on_ground:
            if self.grass_repair_timer > 0:
                self.grass_repair_timer -= 1
            else:
                # ground_y = the actual block the gardener is standing ON (one row below feet)
                foot_y = int(math.floor(self.y + self.height - 0.1))
                ground_y = foot_y + 1  # row of the ground block beneath the gardener
                for check_x in (
                    int(math.floor(self.x - 1)),
                    int(math.floor(self.x + self.width))
                ):
                    # "Diagonally below": same depth as the ground the gardener stands on,
                    # but one tile to the side. If that block is missing, replace it with grass.
                    if (not terrain.is_block_at(check_x, ground_y)
                            and terrain.is_block_at(check_x, ground_y + 1)
                            and terrain.blocks.get((check_x, ground_y + 1)) not in ("plant",)):
                        terrain.add_block(check_x, ground_y, "grass")
                        self.grass_repair_timer = 120  # 2-second cooldown
                        break
                
    def draw(self, surface: pygame.Surface, camera: 'Camera2D', texture_manager: 'TextureManager') -> None:
        screen_x, screen_y = camera.world_to_screen(self.x, self.y)
        pixel_width = int(self.width * camera.block_size)
        pixel_height = int(self.height * camera.block_size)
        
        tex = texture_manager.get_texture("gardener")
        if tex:
            # Flip texture based on direction
            if self.direction == -1:
                tex = pygame.transform.flip(tex, True, False)
            surface.blit(tex, (screen_x, screen_y))
        else:
            rect = pygame.Rect(screen_x, screen_y, pixel_width, pixel_height)
            pygame.draw.rect(surface, (255, 0, 0), rect)


class Snake:
    """Snake enemy that slithers randomly underground and can pass through soil but not stone"""
    def __init__(self, start_x: float, start_y: float):
        # 12 segments spaced 0.475 blocks apart (≈19 px) so textures overlap by 5 px
        self.segments = [[start_x - i * 0.475, start_y] for i in range(12)]
        self.width = 0.6
        self.height = 0.6
        self.speed = 0.03
        self.dx = 0.0
        self.dy = 0.0
        self.change_dir_timer = 0
        
    @property
    def x(self) -> float:
        return self.segments[0][0]
        
    @property
    def y(self) -> float:
        return self.segments[0][1]

    def _check_stone_collision(self, x: float, y: float, terrain: 'Terrain2D') -> bool:
        margin = 0.05
        corners = [
            (x + margin, y + margin),
            (x + self.width - margin, y + margin),
            (x + margin, y + self.height - margin),
            (x + self.width - margin, y + self.height - margin)
        ]
        for cx, cy in corners:
            bx, by = int(math.floor(cx)), int(math.floor(cy))
            if terrain.is_block_at(bx, by) and terrain.blocks.get((bx, by)) == "stone":
                return True
        return False

    def update(self, terrain: 'Terrain2D') -> None:
        if self.change_dir_timer <= 0:
            angle = random.uniform(0, 2 * math.pi)
            self.dx = math.cos(angle) * self.speed
            self.dy = math.sin(angle) * self.speed
            self.change_dir_timer = random.randint(60, 180)
        else:
            self.change_dir_timer -= 1
            
        new_hx = self.segments[0][0] + self.dx
        new_hy = self.segments[0][1] + self.dy
        
        # Limit to underground region (y between 1 and 14)
        if new_hy < 1.0 or new_hy > 14.0:
            self.dy *= -1
            new_hy = max(1.0, min(14.0, new_hy))
            self.change_dir_timer = 0
            
        # Constrain to map boundaries
        if new_hx < -50.0 or new_hx > 50.0:
            self.dx *= -1
            new_hx = max(-50.0, min(50.0, new_hx))
            self.change_dir_timer = 0
            
        # Check collision with stone block only
        if self._check_stone_collision(new_hx, new_hy, terrain):
            self.dx *= -1
            self.dy *= -1
            self.change_dir_timer = 0
        else:
            self.segments[0][0] = new_hx
            self.segments[0][1] = new_hy
            
        # Segment follow behavior
        spacing = 0.475  # 19 px at block_size 40 → 5 px overlap between segments
        for i in range(1, len(self.segments)):
            prev = self.segments[i-1]
            curr = self.segments[i]
            dx = prev[0] - curr[0]
            dy = prev[1] - curr[1]
            dist = math.hypot(dx, dy)
            if dist > spacing:
                ratio = spacing / dist
                curr[0] = prev[0] - dx * ratio
                curr[1] = prev[1] - dy * ratio
            
    def draw(self, surface: pygame.Surface, camera: 'Camera2D',
             texture_manager: Optional['TextureManager'] = None) -> None:
        """Draw the snake tail-to-head so the head always renders on top.

        Texture slots (all optional, falls back to gradient circles):
          snake_head.png        – head segment
          snake_body1.png, snake_body2.png, ...  – body segments (cycled)
          snake_tail.png        – tail segment

        All textures are assumed to face RIGHT (0°) in their source image.
        Each segment is rotated to face the direction it is travelling.
        """
        num_segs = len(self.segments)
        pixel_w = int(self.width * camera.block_size)
        pixel_h = int(self.height * camera.block_size)
        seg_size = max(pixel_w, pixel_h)  # square blit size for textures

        # Gather textures once (None if not loaded)
        head_tex  = texture_manager.get_texture("snake_head")  if texture_manager else None
        tail_tex  = texture_manager.get_texture("snake_tail")  if texture_manager else None
        body_vars = (texture_manager.variants.get("snake_body") or []) if texture_manager else []

        def _seg_angle(i: int) -> float:
            """Angle (degrees) each segment faces – toward the head."""
            if i == 0:
                # Head: faces the direction it's moving
                prev = self.segments[1] if num_segs > 1 else self.segments[0]
                dx = self.segments[0][0] - prev[0]
                dy = self.segments[0][1] - prev[1]
            else:
                # Body / tail: faces toward the segment ahead of it
                dx = self.segments[i - 1][0] - self.segments[i][0]
                dy = self.segments[i - 1][1] - self.segments[i][1]
            return math.degrees(math.atan2(dy, dx))  # 0° = right

        def _blit_tex(tex: pygame.Surface, cx: int, cy: int, angle: float) -> None:
            """Scale, rotate and blit a texture centred on (cx, cy)."""
            scaled  = pygame.transform.scale(tex, (seg_size, seg_size))
            rotated = pygame.transform.rotate(scaled, -angle)
            rect    = rotated.get_rect(center=(cx, cy))
            surface.blit(rotated, rect.topleft)

        # Draw tail → head so the head is always on top
        for i in range(num_segs - 1, -1, -1):
            hx, hy     = self.segments[i]
            sx, sy     = camera.world_to_screen(hx, hy)
            cx         = int(sx + pixel_w / 2)
            cy         = int(sy + pixel_h / 2)
            angle      = _seg_angle(i)

            if i == 0 and head_tex:
                _blit_tex(head_tex, cx, cy, angle)

            elif i == num_segs - 1 and tail_tex:
                _blit_tex(tail_tex, cx, cy, angle)

            elif body_vars:
                # Cycle through available body textures
                tex = body_vars[(i - 1) % len(body_vars)]
                _blit_tex(tex, cx, cy, angle)

            else:
                # ── Fallback: gradient circles ──
                factor       = 1.0 - (i / (num_segs - 1)) * 0.6
                radius       = max(2, int((pixel_w / 2) * factor))
                color_factor = 1.0 - (i / (num_segs - 1))
                color        = (0, int(120 + 135 * color_factor), 0)
                pygame.draw.circle(surface, color, (cx, cy), radius)
                if i == 0:  # fallback eyes on head
                    eo = int(radius * 0.4)
                    pygame.draw.circle(surface, (255, 0, 0), (cx - eo, cy - eo), 2)
                    pygame.draw.circle(surface, (255, 0, 0), (cx + eo, cy - eo), 2)


class ParticleSystem:
    """Spawns and updates block-break debris particles"""

    # Palette of debris colours per block type
    _COLORS: dict = {
        'soil':  [(139, 90, 43), (160, 105, 50), (120, 70, 30), (180, 125, 60)],
        'grass': [(76, 175, 80),  (100, 200, 80), (55, 140, 40), (139, 90, 43)],
        'stone': [(120, 120, 120),(150, 150, 150),(90, 90, 90),  (170, 170, 170)],
        'plant': [(76, 175, 80),  (50, 150, 60),  (100, 180, 60)],
    }
    _DEFAULT = [(150, 100, 50)]

    def __init__(self) -> None:
        # Each particle: [x, y, vx, vy, life, max_life, (r,g,b), size]
        self._particles: list = []

    def clear(self) -> None:
        self._particles.clear()

    def spawn_break(self, wx: float, wy: float, block_type: str) -> None:
        """Burst particles at world position (wx, wy) using colours for block_type."""
        palette = self._COLORS.get(block_type, self._DEFAULT)
        count = random.randint(7, 14)
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(0.025, 0.13)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - random.uniform(0.02, 0.08)  # upward bias
            life = random.randint(22, 52)
            color = random.choice(palette)
            size = random.randint(2, 5)
            self._particles.append([
                wx + random.uniform(-0.25, 0.25),
                wy + random.uniform(-0.25, 0.25),
                vx, vy, life, life, color, size
            ])

    def update(self) -> None:
        GRAVITY = 0.005
        alive = []
        for p in self._particles:
            p[3] += GRAVITY   # vy += gravity
            p[0] += p[2]      # x += vx
            p[1] += p[3]      # y += vy
            p[4] -= 1         # life -= 1
            if p[4] > 0:
                alive.append(p)
        self._particles = alive

    def draw(self, surface: pygame.Surface, camera: 'Camera2D') -> None:
        sw = surface.get_width()
        sh = surface.get_height()
        for p in self._particles:
            sx, sy = camera.world_to_screen(p[0], p[1])
            if sx < -8 or sx > sw + 8 or sy < -8 or sy > sh + 8:
                continue
            alpha = p[4] / p[5]                     # life / max_life  (0..1)
            r = int(p[6][0] * alpha)
            g = int(p[6][1] * alpha)
            b = int(p[6][2] * alpha)
            sz = max(1, int(p[7] * (0.4 + 0.6 * alpha)))
            pygame.draw.rect(surface, (r, g, b), (int(sx), int(sy), sz, sz))


class CloudSystem:
    """Drifting fluffy clouds rendered in world-space sky"""

    def __init__(self):
        self.clouds: list = []
        # Pre-baked gradient sky surface (1px wide, scaled at draw time)
        self._sky_grad: Optional[pygame.Surface] = None
        for _ in range(12):
            x = random.uniform(-55, 55)
            y = random.uniform(-20, -3)
            self.clouds.append(self._make_cloud(x, y))

    def _make_cloud(self, x: float, y: float) -> dict:
        size = random.uniform(1.0, 2.6)
        n = random.randint(4, 7)
        puffs = []
        for _ in range(n):
            px = random.uniform(-size * 0.65, size * 0.65)
            py = random.uniform(-size * 0.15, size * 0.15)
            rx = random.uniform(size * 0.35, size * 0.75)
            ry = random.uniform(size * 0.20, size * 0.40)
            puffs.append((px, py, rx, ry))
        return {
            'x': x, 'y': y,
            'drift': random.uniform(0.003, 0.009),
            'puffs': puffs,
        }

    def reset(self) -> None:
        self.clouds.clear()
        for _ in range(12):
            x = random.uniform(-55, 55)
            y = random.uniform(-20, -3)
            self.clouds.append(self._make_cloud(x, y))

    def update(self) -> None:
        for cloud in self.clouds:
            cloud['x'] += cloud['drift']
            if cloud['x'] > 58:
                cloud['x'] = -58
                cloud['y'] = random.uniform(-20, -3)

    def draw_sky(self, surface: pygame.Surface) -> None:
        """Draw a smooth top-to-bottom sky gradient."""
        if self._sky_grad is None or self._sky_grad.get_height() != surface.get_height():
            h = surface.get_height()
            self._sky_grad = pygame.Surface((1, h))
            top = (82, 172, 230)
            bot = (148, 218, 250)
            for row in range(h):
                t = row / max(h - 1, 1)
                r = int(top[0] + (bot[0] - top[0]) * t)
                g = int(top[1] + (bot[1] - top[1]) * t)
                b = int(top[2] + (bot[2] - top[2]) * t)
                self._sky_grad.set_at((0, row), (r, g, b))
        scaled = pygame.transform.scale(self._sky_grad, surface.get_size())
        surface.blit(scaled, (0, 0))

    def draw_clouds(self, surface: pygame.Surface, camera: 'Camera2D') -> None:
        """Draw all clouds; skip any below the top of the screen."""
        bs = camera.block_size
        sw = surface.get_width()
        sh = surface.get_height()
        for cloud in self.clouds:
            cx, cy = camera.world_to_screen(cloud['x'], cloud['y'])
            if cx < -300 or cx > sw + 300 or cy > sh:
                continue
            # Subtle blue-grey shadow slightly below each puff
            for (px, py, rx, ry) in cloud['puffs']:
                ex = int(cx + px * bs)
                ey = int(cy + py * bs)
                ew = max(6, int(rx * bs * 2))
                eh = max(4, int(ry * bs * 2))
                pygame.draw.ellipse(surface, (190, 218, 240),
                                    (ex - ew // 2, ey - eh // 2 + 4, ew, eh))
            # White puffs on top
            for (px, py, rx, ry) in cloud['puffs']:
                ex = int(cx + px * bs)
                ey = int(cy + py * bs)
                ew = max(6, int(rx * bs * 2))
                eh = max(4, int(ry * bs * 2))
                pygame.draw.ellipse(surface, (255, 255, 255),
                                    (ex - ew // 2, ey - eh // 2, ew, eh))


class Button:
    """Playful, colorful button class for UI elements."""

    # Map keywords in button text to a color theme name
    _THEME_MAP = [
        ("PLAY AGAIN",    "play_again"),
        ("PLAY",          "play"),
        ("HOW TO",        "instructions"),
        ("RESUME",        "resume"),
        ("SETTINGS",      "settings"),
        ("EXIT",          "exit"),
        ("QUIT",          "exit"),
        ("BACK",          "back"),
    ]

    def __init__(self, x: int, y: int, width: int, height: int, text: str,
                 font_size: int = 32, theme: str = ""):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font_size = font_size
        self.is_hovered = False
        self.font = pygame.font.Font(None, font_size)
        self._hover_anim = 0.0   # 0.0 → 1.0, animated toward target each frame

        # Pick theme automatically if not specified
        if theme:
            self._theme = theme
        else:
            upper = text.upper()
            self._theme = "default"
            for keyword, tname in self._THEME_MAP:
                if keyword in upper:
                    self._theme = tname
                    break

    def _lerp_color(self, c1: tuple, c2: tuple, t: float) -> tuple:
        return (
            int(c1[0] + (c2[0] - c1[0]) * t),
            int(c1[1] + (c2[1] - c1[1]) * t),
            int(c1[2] + (c2[2] - c1[2]) * t),
        )

    def draw(self, surface: pygame.Surface) -> None:
        # Smoothly animate hover factor
        target = 1.0 if self.is_hovered else 0.0
        self._hover_anim += (target - self._hover_anim) * 0.25
        t = self._hover_anim

        base, shadow_col, outline_col, text_col = BUTTON_THEMES.get(
            self._theme, BUTTON_THEMES["default"]
        )

        # Brighten base slightly on hover
        hover_base = tuple(min(255, int(c * 1.25)) for c in base)
        fill_color = self._lerp_color(base, hover_base, t)

        # Scale the button up slightly on hover
        expand = int(4 * t)
        draw_rect = self.rect.inflate(expand * 2, expand * 2)
        radius = draw_rect.height // 2  # pill shape

        # 1. Drop shadow
        shadow_rect = draw_rect.move(3, 5)
        pygame.draw.rect(surface, shadow_col, shadow_rect, border_radius=radius)

        # 2. Main fill
        pygame.draw.rect(surface, fill_color, draw_rect, border_radius=radius)

        # 3. Highlight stripe (top sheen)
        shine_rect = pygame.Rect(
            draw_rect.x + radius,
            draw_rect.y + 4,
            draw_rect.width - radius * 2,
            draw_rect.height // 3,
        )
        shine_surf = pygame.Surface((shine_rect.width, shine_rect.height), pygame.SRCALPHA)
        shine_surf.fill((255, 255, 255, 55))
        surface.blit(shine_surf, shine_rect.topleft)

        # 4. Outline
        outline_color = self._lerp_color(outline_col,
                                         tuple(min(255, int(c * 1.3)) for c in outline_col), t)
        pygame.draw.rect(surface, outline_color, draw_rect, 3, border_radius=radius)

        # 5. Text (bold shadow + main)
        font_size_big = int(self.font_size * (1.0 + 0.06 * t))
        try:
            font = pygame.font.Font(None, font_size_big)
        except Exception:
            font = self.font
        label = font.render(self.text, True, text_col)
        shadow_label = font.render(self.text, True, shadow_col)
        cx, cy = draw_rect.centerx, draw_rect.centery
        surface.blit(shadow_label, shadow_label.get_rect(center=(cx + 1, cy + 2)))
        surface.blit(label, label.get_rect(center=(cx, cy)))

    def is_clicked(self, mouse_pos: tuple) -> bool:
        return self.rect.collidepoint(mouse_pos)

    def update_hover(self, mouse_pos: tuple) -> None:
        self.is_hovered = self.rect.collidepoint(mouse_pos)


# ---------------------------------------------------------------------------
# Settings widgets
# ---------------------------------------------------------------------------

class SettingsData:
    """Central store for all game settings values."""
    def __init__(self):
        self.master_volume: float = 1.0   # 0.0 – 1.0
        self.music_volume:  float = 0.8   # 0.0 – 1.0
        self.sfx_on:  bool = True
        self.music_on: bool = True
        # Keybinds (pygame key constants)
        self.key_left:  int = pygame.K_a
        self.key_right: int = pygame.K_d
        self.key_jump:  int = pygame.K_w
        self.key_dig:   int = pygame.K_SPACE  # placeholder – actual dig is mouse click


class Slider:
    """Horizontal drag slider that stores a 0–1 float value."""
    TRACK_H   = 8
    KNOB_R    = 12
    TRACK_COL = (60, 60, 60)
    FILL_COL  = (60, 200, 80)
    KNOB_COL  = (255, 255, 255)
    KNOB_HOV  = (200, 255, 210)

    def __init__(self, x: int, y: int, width: int, label: str, value: float = 1.0):
        self.x = x
        self.y = y
        self.width = width
        self.label = label
        self.value = max(0.0, min(1.0, value))
        self.dragging = False
        self._hovered = False
        self._font = pygame.font.Font(None, 30)
        self._val_font = pygame.font.Font(None, 28)

    @property
    def track_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y - self.TRACK_H // 2, self.width, self.TRACK_H)

    @property
    def knob_x(self) -> int:
        return int(self.x + self.value * self.width)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Return True if the slider consumed the event."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            kx = self.knob_x
            ky = self.y
            if math.hypot(event.pos[0] - kx, event.pos[1] - ky) <= self.KNOB_R + 6 \
                    or self.track_rect.collidepoint(event.pos):
                self.dragging = True
                self._update_from_mouse(event.pos[0])
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.dragging = False
                return True
        elif event.type == pygame.MOUSEMOTION:
            self._hovered = (
                math.hypot(event.pos[0] - self.knob_x, event.pos[1] - self.y) <= self.KNOB_R + 6
            )
            if self.dragging:
                self._update_from_mouse(event.pos[0])
                return True
        return False

    def _update_from_mouse(self, mx: int) -> None:
        self.value = max(0.0, min(1.0, (mx - self.x) / self.width))

    def draw(self, surface: pygame.Surface) -> None:
        # Label
        label_surf = self._font.render(self.label, True, TEXT_WHITE)
        surface.blit(label_surf, (self.x, self.y - 28))
        # Percentage
        pct = f"{int(self.value * 100)}%"
        pct_surf = self._val_font.render(pct, True, ACCENT_ORANGE)
        surface.blit(pct_surf, (self.x + self.width + 14, self.y - 12))
        # Track background
        tr = self.track_rect
        pygame.draw.rect(surface, self.TRACK_COL, tr, border_radius=4)
        # Filled portion
        fill_w = int(self.value * self.width)
        if fill_w > 0:
            pygame.draw.rect(surface, self.FILL_COL,
                             pygame.Rect(tr.x, tr.y, fill_w, tr.height), border_radius=4)
        # Knob
        knob_col = self.KNOB_HOV if (self.dragging or self._hovered) else self.KNOB_COL
        pygame.draw.circle(surface, (30, 30, 30), (self.knob_x, self.y), self.KNOB_R + 2)
        pygame.draw.circle(surface, knob_col, (self.knob_x, self.y), self.KNOB_R)


class Toggle:
    """On/Off pill toggle switch."""
    W, H = 64, 32
    ON_COL  = (60, 200, 80)
    OFF_COL = (120, 40, 40)
    KNOB_COL = (255, 255, 255)

    def __init__(self, x: int, y: int, label: str, value: bool = True):
        self.x = x
        self.y = y
        self.label = label
        self.value = value
        self._anim = 1.0 if value else 0.0
        self._font = pygame.font.Font(None, 30)
        self._hovered = False

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.W, self.H)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.value = not self.value
                return True
        elif event.type == pygame.MOUSEMOTION:
            self._hovered = self.rect.collidepoint(event.pos)
        return False

    def draw(self, surface: pygame.Surface) -> None:
        # Animate knob
        target = 1.0 if self.value else 0.0
        self._anim += (target - self._anim) * 0.25
        t = self._anim
        # Label
        label_surf = self._font.render(self.label, True, TEXT_WHITE)
        surface.blit(label_surf, (self.x, self.y - 26))
        # Track
        r = self.H // 2
        bg_col = (
            int(self.OFF_COL[0] + (self.ON_COL[0] - self.OFF_COL[0]) * t),
            int(self.OFF_COL[1] + (self.ON_COL[1] - self.OFF_COL[1]) * t),
            int(self.OFF_COL[2] + (self.ON_COL[2] - self.OFF_COL[2]) * t),
        )
        pygame.draw.rect(surface, bg_col, self.rect, border_radius=r)
        if self._hovered:
            pygame.draw.rect(surface, (255, 255, 255), self.rect, 2, border_radius=r)
        # State label
        state_surf = self._font.render("ON" if self.value else "OFF", True,
                                       (255, 255, 255) if self.value else (180, 100, 100))
        state_x = self.x + self.W + 12
        surface.blit(state_surf, (state_x, self.y + 5))
        # Knob
        knob_x = int(self.x + r + t * (self.W - self.H))
        knob_y = self.y + r
        pygame.draw.circle(surface, (30, 30, 30), (knob_x, knob_y), r - 2)
        pygame.draw.circle(surface, self.KNOB_COL, (knob_x, knob_y), r - 4)



class KeybindRow:
    """A settings row that shows an action name + current key, click to rebind."""
    W, H = 320, 40

    def __init__(self, x: int, y: int, action: str, key: int):
        self.x = x
        self.y = y
        self.action = action
        self.key = key           # pygame key constant
        self.awaiting = False    # True while listening for a new key press
        self._hovered = False
        self._font_lbl = pygame.font.Font(None, 30)
        self._font_key = pygame.font.Font(None, 28)

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.W, self.H)

    @property
    def key_name(self) -> str:
        name = pygame.key.name(self.key)
        return name.upper() if name else "?"

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.awaiting = True
                return True
        elif event.type == pygame.MOUSEMOTION:
            self._hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.awaiting:
            if event.key != pygame.K_ESCAPE:
                self.key = event.key
            self.awaiting = False
            return True
        return False

    def draw(self, surface: pygame.Surface) -> None:
        # Row background
        if self.awaiting:
            bg_col = (80, 60, 20)
            border_col = (255, 200, 0)
        elif self._hovered:
            bg_col = (55, 55, 55)
            border_col = (120, 120, 120)
        else:
            bg_col = (40, 40, 40)
            border_col = (70, 70, 70)
        pygame.draw.rect(surface, bg_col, self.rect, border_radius=8)
        pygame.draw.rect(surface, border_col, self.rect, 2, border_radius=8)
        # Action label
        lbl = self._font_lbl.render(self.action, True, TEXT_WHITE)
        surface.blit(lbl, (self.x + 14, self.y + self.H // 2 - lbl.get_height() // 2))
        # Key badge
        if self.awaiting:
            badge_text = "Press a key..."
            badge_col = (255, 200, 0)
            text_col = (30, 20, 0)
        else:
            badge_text = self.key_name
            badge_col = (60, 140, 220)
            text_col = (255, 255, 255)
        key_surf = self._font_key.render(badge_text, True, text_col)
        badge_w = max(60, key_surf.get_width() + 20)
        badge_h = 28
        badge_x = self.x + self.W - badge_w - 10
        badge_y = self.y + self.H // 2 - badge_h // 2
        pygame.draw.rect(surface, badge_col,
                         pygame.Rect(badge_x, badge_y, badge_w, badge_h), border_radius=6)
        surface.blit(key_surf, (badge_x + (badge_w - key_surf.get_width()) // 2,
                                badge_y + (badge_h - key_surf.get_height()) // 2))


class MoleGame:
    """Main game class"""
    def __init__(self):
        # Grab the desktop resolution BEFORE creating any window
        _info = pygame.display.Info()
        self.desktop_w = _info.current_w
        self.desktop_h = _info.current_h

        # Real display window – resizable, starts at the logical size
        self.display = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            pygame.RESIZABLE
        )
        # Fixed-size virtual surface – all game rendering happens here
        self.screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.fullscreen = False
        pygame.display.set_caption("Mole Escape - Garden Defense")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = GameState.HOME
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        self.font_tiny = pygame.font.Font(None, 24)
        
        self.block_size = 40
        self.texture_manager = TextureManager(self.block_size)
        
        try:
            self.font_title = pygame.font.SysFont("Supply Center", 130, bold=True)
        except:
            self.font_title = self.font_large
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.bg_image = ImageBackground(os.path.join(base_dir, "addinfo", "bg_image.png"), SCREEN_WIDTH, SCREEN_HEIGHT)
        self.bg_offset = 0.0
        self.bg_offset_direction = 1
        self.bg_offset_min = -50
        self.bg_offset_max = 50
        self.bg_offset_speed = 0.25
        
        self.previous_state = GameState.HOME
        self._init_buttons()
        
        self.camera = Camera2D(SCREEN_WIDTH, SCREEN_HEIGHT, self.block_size)
        
        self.terrain = Terrain2D(self.texture_manager, self.block_size)
        self.terrain.generate_terrain()
        
        self.minimap = Minimap(SCREEN_WIDTH - 160, 10, 150, 150)
        
        # Initialize player, gardener, and snakes
        self.game_over_reason = "gardener"
        self.seed_destroyed_count = 0
        self.player = Player(-50, 14)
        self.gardener = Gardener(10, -1)
        self.snakes = self._create_snakes(4)
        self.snake_spawn_timer = 600  # 10 seconds at 60 FPS
        self.camera.set_position(self.player.x + self.player.width/2, self.player.y + self.player.height/2)
        # Timer (in frames at 60 FPS)
        self.play_time: int = 0
        self.finish_time: int = 0
        self.clouds = CloudSystem()
        self.particles = ParticleSystem()
        self.terrain.particle_system = self.particles
        
    def reset_game(self) -> None:
        """Reset the game state for a new playthrough"""
        self.terrain.generate_terrain()
        self.game_over_reason = "gardener"
        self.seed_destroyed_count = 0
        self.player = Player(-50, 14)
        self.gardener = Gardener(10, -1)  # Gardener patrols surface (y=-1)
        self.snakes = self._create_snakes(4)
        self.snake_spawn_timer = 600
        self.camera.set_position(self.player.x + self.player.width/2, self.player.y + self.player.height/2)
        self.play_time = 0
        self.finish_time = 0
        self.clouds.reset()
        self.particles.clear()
        self.terrain.particle_system = self.particles
        
    def _init_buttons(self) -> None:
        button_width = 250
        button_height = 60
        button_x = (SCREEN_WIDTH - button_width) // 2
        
        # Home buttons
        self.play_button = Button(button_x, 300, button_width, button_height, "PLAY")
        self.instructions_button = Button(button_x, 400, button_width, button_height, "HOW TO PLAY")
        self.settings_button = Button(button_x, 500, button_width, button_height, "SETTINGS")
        self.quit_button = Button(button_x, 600, button_width, button_height, "EXIT")
        
        # Pause buttons
        self.resume_button = Button(button_x, 300, button_width, button_height, "RESUME")
        self.pause_settings_button = Button(button_x, 400, button_width, button_height, "SETTINGS")
        self.exit_to_home_button = Button(button_x, 500, button_width, button_height, "EXIT TO HOME")
        
        # Game Over buttons
        self.play_again_button = Button(button_x, 400, button_width, button_height, "PLAY AGAIN")

        # ---- Settings data & widgets ----
        self.settings = SettingsData()
        cx = SCREEN_WIDTH // 2
        slider_w = 320
        sx = cx - slider_w // 2

        # --- Sound section ---
        self._s_master = Slider(sx, 180, slider_w, "Master Volume", self.settings.master_volume)
        self._s_music  = Slider(sx, 265, slider_w, "Music Volume",  self.settings.music_volume)
        self._t_sfx    = Toggle(sx, 330, "Sound FX",  self.settings.sfx_on)

        # --- Keybind section ---
        kb_x = cx - KeybindRow.W // 2
        self._kb_left  = KeybindRow(kb_x, 420, "Move Left",  self.settings.key_left)
        self._kb_right = KeybindRow(kb_x, 470, "Move Right", self.settings.key_right)
        self._kb_jump  = KeybindRow(kb_x, 520, "Jump",       self.settings.key_jump)
        self._kb_dig   = KeybindRow(kb_x, 570, "Dig (hold)", self.settings.key_dig)

        self._settings_sound_widgets = [
            self._s_master, self._s_music,
            self._t_sfx,
        ]
        self._settings_kb_widgets = [
            self._kb_left, self._kb_right, self._kb_jump, self._kb_dig,
        ]
        self._settings_widgets = self._settings_sound_widgets + self._settings_kb_widgets
        self._settings_back_btn = Button(50, SCREEN_HEIGHT - 80, 150, 50, "BACK")
        self._settings_save_btn = Button(SCREEN_WIDTH - 220, SCREEN_HEIGHT - 80, 170, 50, "SAVE",
                                         theme="play")

        # Active keybinds used by the game loop (updated on Save)
        self.active_key_left  = self.settings.key_left
        self.active_key_right = self.settings.key_right
        self.active_key_jump  = self.settings.key_jump

    def _is_safe_snake_spawn(self, x: float, y: float) -> bool:
        bx = int(math.floor(x))
        by = int(math.floor(y))
        return not (self.terrain.is_block_at(bx, by) and self.terrain.blocks.get((bx, by)) == "stone")

    def _find_safe_snake_spawn(self, attempts: int = 200) -> tuple[float, float]:
        for _ in range(attempts):
            sx = random.uniform(-40, 40)
            sy = random.uniform(2, 13)
            if self._is_safe_snake_spawn(sx, sy):
                return sx, sy
        # Fallback to a default safe position if all random attempts hit stone blocks
        return -40.0, 8.0

    def _create_snakes(self, count: int) -> list['Snake']:
        snakes = []
        for _ in range(count):
            sx, sy = self._find_safe_snake_spawn()
            snakes.append(Snake(sx, sy))
        return snakes
        
    def draw_home_screen(self) -> None:
        if self.bg_image.image_loaded and self.bg_image.image_surface:
            bg_x = self.bg_image.base_x + int(self.bg_offset)
            self.screen.blit(self.bg_image.image_surface, (bg_x, 0))
            if self.bg_image.image_width < SCREEN_WIDTH:
                self.screen.blit(self.bg_image.image_surface, (bg_x + self.bg_image.image_width, 0))
            elif bg_x > 0:
                self.screen.blit(self.bg_image.image_surface, (bg_x - self.bg_image.image_width, 0))
            elif bg_x + self.bg_image.image_width < SCREEN_WIDTH:
                self.screen.blit(self.bg_image.image_surface, (bg_x + self.bg_image.image_width, 0))
        else:
            self.screen.fill(BG_COLOR)
        
        title_text = self.font_title.render("KROT", True, (255, 255, 240))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 120))
        self.screen.blit(title_text, title_rect)
        
        subtitle_text = self.font_small.render("Garden Defense Challenge", True, ACCENT_ORANGE)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 210))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        self.play_button.draw(self.screen)
        self.instructions_button.draw(self.screen)
        self.settings_button.draw(self.screen)
        self.quit_button.draw(self.screen)
        
        footer_text = self.font_tiny.render("Can you escape the garden before the gardener catches you?", True, TEXT_WHITE)
        footer_rect = footer_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        self.screen.blit(footer_text, footer_rect)
        
    def draw_instructions_screen(self) -> None:
        self._draw_animated_bg(overlay_alpha=155)
        
        title_text = self.font_large.render("HOW TO PLAY", True, GRASS_GREEN)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 40))
        self.screen.blit(title_text, title_rect)
        
        instructions = [
            "OBJECTIVE: Escape from the garden to win!",
            "",
            "2D PLATFORMER CONTROLS:",
            "A / D: Move left and right",
            "W / SPACE: Jump",
            "LEFT CLICK: Dig blocks with your mouse cursor",
            "",
            "GAMEPLAY:",
            "- You start deep underground as a mole",
            "- Dig through soil blocks by clicking on them with your mouse",
            "- Dig upwards to reach the grass surface level",
            "- Find holes to escape!",
            "",
            "TIPS: Plan your escape route carefully and watch out for falling!",
        ]
        
        y_offset = 120
        line_height = 30
        for instruction in instructions:
            if instruction == "":
                y_offset += line_height * 0.5
            else:
                text = self.font_tiny.render(instruction, True, TEXT_WHITE)
                text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
                self.screen.blit(text, text_rect)
                y_offset += line_height
        
        back_button = Button(50, SCREEN_HEIGHT - 80, 150, 50, "BACK")
        back_button.draw(self.screen)
        
    def draw_settings_screen(self) -> None:
        self._draw_animated_bg(overlay_alpha=155)

        cx = SCREEN_WIDTH // 2
        font_sec = pygame.font.Font(None, 34)

        # ── Title ──
        title_text = self.font_large.render("SETTINGS", True, GRASS_GREEN)
        self.screen.blit(title_text, title_text.get_rect(center=(cx, 55)))

        # ── SOUND section header ──
        sec = font_sec.render("SOUND", True, ACCENT_ORANGE)
        self.screen.blit(sec, (cx - 160, 110))
        pygame.draw.line(self.screen, (100, 80, 30), (cx - 160, 128), (cx + 160, 128), 1)

        # ── CONTROLS section header ──
        sec2 = font_sec.render("CONTROLS", True, ACCENT_ORANGE)
        self.screen.blit(sec2, (cx - 160, 385))
        pygame.draw.line(self.screen, (100, 80, 30), (cx - 160, 403), (cx + 160, 403), 1)
        hint = pygame.font.Font(None, 22).render(
            "Click a row, then press a key to rebind", True, (160, 160, 160))
        self.screen.blit(hint, (cx - 160, 405))

        # Sync pending values (not yet committed)
        self.settings.master_volume = self._s_master.value
        self.settings.music_volume  = self._s_music.value
        self.settings.sfx_on        = self._t_sfx.value
        self.settings.key_left      = self._kb_left.key
        self.settings.key_right     = self._kb_right.key
        self.settings.key_jump      = self._kb_jump.key
        self.settings.key_dig       = self._kb_dig.key

        # Draw all widgets
        for widget in self._settings_widgets:
            widget.draw(self.screen)

        # Back + Save buttons
        mouse_pos = self._scale_mouse_pos(pygame.mouse.get_pos())
        self._settings_back_btn.update_hover(mouse_pos)
        self._settings_back_btn.draw(self.screen)
        self._settings_save_btn.update_hover(mouse_pos)
        self._settings_save_btn.draw(self.screen)
        
    def _get_render_rect(self) -> pygame.Rect:
        """Return the letterboxed rect where the virtual surface is drawn on the display."""
        win_w, win_h = self.display.get_size()
        scale = min(win_w / SCREEN_WIDTH, win_h / SCREEN_HEIGHT)
        render_w = int(SCREEN_WIDTH * scale)
        render_h = int(SCREEN_HEIGHT * scale)
        offset_x = (win_w - render_w) // 2
        offset_y = (win_h - render_h) // 2
        return pygame.Rect(offset_x, offset_y, render_w, render_h)

    def _scale_mouse_pos(self, pos: tuple) -> tuple:
        """Convert real-window mouse coordinates to virtual-surface coordinates."""
        rect = self._get_render_rect()
        # Clamp to the rendered area then map
        rx = max(0, min(pos[0] - rect.x, rect.width  - 1))
        ry = max(0, min(pos[1] - rect.y, rect.height - 1))
        sx = int(rx * SCREEN_WIDTH  / rect.width)
        sy = int(ry * SCREEN_HEIGHT / rect.height)
        return (sx, sy)

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.MOUSEBUTTONUP:
                if self.state == GameState.SETTINGS:
                    mouse_pos = self._scale_mouse_pos(event.pos)
                    up_proxy = type('_E', (), {
                        'type': pygame.MOUSEBUTTONUP,
                        'button': event.button,
                        'pos': mouse_pos,
                    })()
                    for widget in self._settings_sound_widgets:
                        widget.handle_event(up_proxy)

            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = self._scale_mouse_pos(event.pos)
                if self.state == GameState.HOME:
                    self.play_button.update_hover(mouse_pos)
                    self.instructions_button.update_hover(mouse_pos)
                    self.settings_button.update_hover(mouse_pos)
                    self.quit_button.update_hover(mouse_pos)
                elif self.state == GameState.PAUSED:
                    self.resume_button.update_hover(mouse_pos)
                    self.pause_settings_button.update_hover(mouse_pos)
                    self.exit_to_home_button.update_hover(mouse_pos)
                elif self.state in [GameState.GAME_OVER, GameState.WIN]:
                    self.play_again_button.update_hover(mouse_pos)
                    self.exit_to_home_button.update_hover(mouse_pos)
                elif self.state == GameState.SETTINGS:
                    proxy = type('_E', (), {
                        'type': pygame.MOUSEMOTION, 'pos': mouse_pos
                    })()
                    for widget in self._settings_widgets:
                        widget.handle_event(proxy)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = self._scale_mouse_pos(event.pos)
                if self.state == GameState.HOME:
                    if self.play_button.is_clicked(mouse_pos):
                        self.reset_game()
                        self.state = GameState.PLAYING
                    elif self.instructions_button.is_clicked(mouse_pos):
                        self.previous_state = GameState.HOME
                        self.state = GameState.INSTRUCTIONS
                    elif self.settings_button.is_clicked(mouse_pos):
                        self.previous_state = GameState.HOME
                        self.state = GameState.SETTINGS
                    elif self.quit_button.is_clicked(mouse_pos):
                        self.running = False
                
                elif self.state == GameState.PAUSED:
                    if self.resume_button.is_clicked(mouse_pos):
                        self.state = GameState.PLAYING
                    elif self.pause_settings_button.is_clicked(mouse_pos):
                        self.previous_state = GameState.PAUSED
                        self.state = GameState.SETTINGS
                    elif self.exit_to_home_button.is_clicked(mouse_pos):
                        self.state = GameState.HOME
                
                elif self.state in [GameState.GAME_OVER, GameState.WIN]:
                    if self.play_again_button.is_clicked(mouse_pos):
                        self.reset_game()
                        self.state = GameState.PLAYING
                    elif self.exit_to_home_button.is_clicked(mouse_pos):
                        self.state = GameState.HOME
                
                elif self.state == GameState.INSTRUCTIONS:
                    back_button = Button(50, SCREEN_HEIGHT - 80, 150, 50, "BACK")
                    if back_button.is_clicked(mouse_pos):
                        self.state = self.previous_state
                
                elif self.state == GameState.SETTINGS:
                    if self._settings_back_btn.is_clicked(mouse_pos):
                        self.state = self.previous_state
                    elif self._settings_save_btn.is_clicked(mouse_pos):
                        # Commit keybinds to the active game keys
                        self.active_key_left  = self._kb_left.key
                        self.active_key_right = self._kb_right.key
                        self.active_key_jump  = self._kb_jump.key
                        self.settings.key_left  = self._kb_left.key
                        self.settings.key_right = self._kb_right.key
                        self.settings.key_jump  = self._kb_jump.key
                        self.settings.key_dig   = self._kb_dig.key
                        self.state = self.previous_state
                    else:
                        for widget in self._settings_widgets:
                            widget.handle_event(
                                type('_E', (), {
                                    'type': pygame.MOUSEBUTTONDOWN,
                                    'button': 1,
                                    'pos': mouse_pos,
                                })())
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    self.fullscreen = not self.fullscreen
                    if self.fullscreen:
                        self.display = pygame.display.set_mode(
                            (self.desktop_w, self.desktop_h), pygame.FULLSCREEN
                        )
                    else:
                        self.display = pygame.display.set_mode(
                            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE
                        )
                elif self.state == GameState.SETTINGS:
                    # Forward to keybind rows first (they consume it if awaiting)
                    consumed = False
                    for kb in self._settings_kb_widgets:
                        if kb.handle_event(event):
                            consumed = True
                            break
                    if not consumed and event.key == pygame.K_ESCAPE:
                        self.state = self.previous_state
                elif event.key == pygame.K_ESCAPE:
                    if self.state == GameState.PLAYING:
                        self.state = GameState.PAUSED
                    elif self.state == GameState.PAUSED:
                        self.state = GameState.PLAYING
                    elif self.state == GameState.INSTRUCTIONS:
                        self.state = self.previous_state
    
    def _draw_animated_bg(self, overlay_alpha: int = 160) -> None:
        """Blit the scrolling background image (same as home) then apply a dark overlay."""
        if self.bg_image.image_loaded and self.bg_image.image_surface:
            bg_x = self.bg_image.base_x + int(self.bg_offset)
            self.screen.blit(self.bg_image.image_surface, (bg_x, 0))
            if self.bg_image.image_width < SCREEN_WIDTH:
                self.screen.blit(self.bg_image.image_surface, (bg_x + self.bg_image.image_width, 0))
            elif bg_x > 0:
                self.screen.blit(self.bg_image.image_surface, (bg_x - self.bg_image.image_width, 0))
            elif bg_x + self.bg_image.image_width < SCREEN_WIDTH:
                self.screen.blit(self.bg_image.image_surface, (bg_x + self.bg_image.image_width, 0))
        else:
            self.screen.fill(BG_COLOR)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(overlay_alpha)
        overlay.fill((10, 10, 10))
        self.screen.blit(overlay, (0, 0))

    def update(self) -> None:
        # Keep background animating on home, instructions, and settings screens
        if self.state in (GameState.HOME, GameState.INSTRUCTIONS, GameState.SETTINGS) \
                and self.bg_image.image_loaded:
            self.bg_offset += self.bg_offset_direction * self.bg_offset_speed
            if self.bg_offset >= self.bg_offset_max:
                self.bg_offset = self.bg_offset_max
                self.bg_offset_direction = -1
            elif self.bg_offset <= self.bg_offset_min:
                self.bg_offset = self.bg_offset_min
                self.bg_offset_direction = 1
        
        elif self.state == GameState.PLAYING:
            self.play_time += 1
            self.clouds.update()
            self.particles.update()

            keys = pygame.key.get_pressed()
            mouse_buttons = pygame.mouse.get_pressed()
            mouse_pos = self._scale_mouse_pos(pygame.mouse.get_pos())
            
            if self.player.handle_input(keys, self.camera, self.terrain, mouse_buttons, mouse_pos,
                                         key_left=self.active_key_left,
                                         key_right=self.active_key_right,
                                         key_jump=self.active_key_jump):
                self.seed_destroyed_count += 1
                if self.seed_destroyed_count >= 10:
                    self.finish_time = self.play_time
                    self.state = GameState.WIN
            if self.player.update(self.terrain):
                self.seed_destroyed_count += 1
                if self.seed_destroyed_count >= 10:
                    self.finish_time = self.play_time
                    self.state = GameState.WIN
            self.gardener.update(self.terrain, self.player)
            
            # Update snakes
            for snake in self.snakes:
                snake.update(self.terrain)

            self.snake_spawn_timer -= 1
            if self.snake_spawn_timer <= 0:
                sx, sy = self._find_safe_snake_spawn()
                self.snakes.append(Snake(sx, sy))
                self.snake_spawn_timer = 600
                
            self.camera.set_position(self.player.x + self.player.width/2, self.player.y + self.player.height/2)
            
            # Check collision between player and snakes (all segments)
            for snake in self.snakes:
                for segment in snake.segments:
                    if abs(self.player.x - segment[0]) < 0.9 and abs(self.player.y - segment[1]) < 0.9:
                        self.game_over_reason = "snake"
                        self.finish_time = self.play_time
                        self.state = GameState.GAME_OVER
                        break
                if self.state == GameState.GAME_OVER:
                    break
            
            # Check if player and gardener coordinates overlap (within 1 block)
            if self.state != GameState.GAME_OVER and abs(self.player.x - self.gardener.x) < 1.0 and abs(self.player.y - self.gardener.y) < 1.0:
                self.game_over_reason = "gardener"
                self.finish_time = self.play_time
                self.state = GameState.GAME_OVER
                
            # Check if player fell out of the world
            if self.state != GameState.GAME_OVER and self.player.y > 30:
                self.game_over_reason = "fall"
                self.finish_time = self.play_time
                self.state = GameState.GAME_OVER
    
    def draw(self) -> None:
        if self.state == GameState.HOME:
            self.draw_home_screen()
        elif self.state == GameState.INSTRUCTIONS:
            self.draw_instructions_screen()
        elif self.state == GameState.SETTINGS:
            self.draw_settings_screen()
        elif self.state == GameState.PLAYING:
            self.draw_playing_screen()
        elif self.state == GameState.PAUSED:
            self.draw_pause_screen()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over_screen()
        elif self.state == GameState.WIN:
            self.draw_win_screen()

        # Letterbox: fill display black, then blit scaled virtual surface centred
        rect = self._get_render_rect()
        scaled = pygame.transform.smoothscale(self.screen, (rect.width, rect.height))
        self.display.fill((0, 0, 0))
        self.display.blit(scaled, (rect.x, rect.y))
        pygame.display.flip()
        
    def draw_pause_screen(self) -> None:
        self.draw_playing_screen()
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        title_text = self.font_large.render("PAUSED", True, ACCENT_ORANGE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(title_text, title_rect)
        
        self.resume_button.draw(self.screen)
        self.pause_settings_button.draw(self.screen)
        self.exit_to_home_button.draw(self.screen)
        
    def draw_game_over_screen(self) -> None:
        self.draw_playing_screen()
        
        # Customize screen style and text depending on loss reason
        reason = getattr(self, "game_over_reason", "gardener")
        if reason == "snake":
            tint_color = (60, 20, 80)      # Purple tint for venomous snake bite
            title_str = "BITTEN!"
            title_color = (200, 100, 255)  # Lavender/light purple title
            subtitle_str = "A venomous snake caught you underground! Stay alert!"
        elif reason == "fall":
            tint_color = (20, 20, 20)       # Dark charcoal tint for falling out of world
            title_str = "FELL OUT OF WORLD!"
            title_color = (180, 180, 180)  # Grey title
            subtitle_str = "You dug too deep and fell out of the garden!"
        else:
            tint_color = (100, 0, 0)        # Dark red tint for gardener catch
            title_str = "CAUGHT!"
            title_color = (255, 100, 100)  # Red title
            subtitle_str = "The gardener found you. Try to be more sneaky next time."

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(tint_color)
        self.screen.blit(overlay, (0, 0))
        
        title_text = self.font_large.render(title_str, True, title_color)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(title_text, title_rect)
        
        subtitle_text = self.font_small.render(subtitle_str, True, TEXT_WHITE)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 280))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Show how long the run lasted before game over
        fin_s = self.finish_time // 60
        fin_ms = (self.finish_time % 60) * 100 // 60
        time_str = f"Time survived: {fin_s // 60:02d}:{fin_s % 60:02d}.{fin_ms:02d}"
        time_text = self.font_small.render(time_str, True, (220, 220, 220))
        time_rect = time_text.get_rect(center=(SCREEN_WIDTH // 2, 330))
        self.screen.blit(time_text, time_rect)

        self.play_again_button.draw(self.screen)
        
        # Position Exit button lower for game over screen
        orig_y = self.exit_to_home_button.rect.y
        self.exit_to_home_button.rect.y = 500
        self.exit_to_home_button.draw(self.screen)
        self.exit_to_home_button.rect.y = orig_y  # Restore
    
    def draw_win_screen(self) -> None:
        self.draw_playing_screen()
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((30, 100, 30))
        self.screen.blit(overlay, (0, 0))
        
        title_text = self.font_large.render("YOU WIN!", True, (255, 215, 0))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(title_text, title_rect)
        
        subtitle_text = self.font_small.render(
            "You destroyed 10 seeds and saved the garden!", True, TEXT_WHITE
        )
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 280))
        self.screen.blit(subtitle_text, subtitle_rect)

        # Show the final completion time
        fin_s = self.finish_time // 60
        fin_ms = (self.finish_time % 60) * 100 // 60
        time_str = f"Time: {fin_s // 60:02d}:{fin_s % 60:02d}.{fin_ms:02d}"
        time_text = self.font_medium.render(time_str, True, (255, 215, 0))
        time_rect = time_text.get_rect(center=(SCREEN_WIDTH // 2, 340))
        self.screen.blit(time_text, time_rect)

        self.play_again_button.draw(self.screen)
        orig_y = self.exit_to_home_button.rect.y
        self.exit_to_home_button.rect.y = 500
        self.exit_to_home_button.draw(self.screen)
        self.exit_to_home_button.rect.y = orig_y  # Restore
    
    def draw_playing_screen(self) -> None:
        # Sky gradient + clouds (drawn before terrain so terrain overlaps)
        self.clouds.draw_sky(self.screen)
        self.clouds.draw_clouds(self.screen, self.camera)
        
        self.terrain.draw(self.screen, self.camera)
        self.player.draw(self.screen, self.camera, self.texture_manager)
        self.gardener.draw(self.screen, self.camera, self.texture_manager)
        
        # Draw snakes
        for snake in self.snakes:
            snake.draw(self.screen, self.camera, self.texture_manager)

        # Draw block-break particles on top of everything
        self.particles.draw(self.screen, self.camera)
            
        pos_text = self.font_tiny.render(
            f"X: {self.player.x:.1f} Y: {self.player.y:.1f}", 
            True, TEXT_WHITE
        )
        pos_rect = pos_text.get_rect(topleft=(10, 10))
        self.screen.blit(pos_text, pos_rect)
        
        self.minimap.draw(self.screen, self.player, self.terrain, self.gardener, self.snakes)
        
        seed_text = self.font_tiny.render(
            f"Seeds destroyed: {self.seed_destroyed_count} / 10",
            True, TEXT_WHITE
        )
        seed_rect = seed_text.get_rect(topleft=(10, 30))
        self.screen.blit(seed_text, seed_rect)

        # Live timer displayed in the HUD
        elapsed_s = self.play_time // 60
        elapsed_ms = (self.play_time % 60) * 100 // 60  # 2-digit centiseconds approximation
        timer_text = self.font_small.render(
            f"Time: {elapsed_s // 60:02d}:{elapsed_s % 60:02d}.{elapsed_ms:02d}",
            True, ACCENT_ORANGE
        )
        timer_rect = timer_text.get_rect(center=(SCREEN_WIDTH // 2, 15))
        self.screen.blit(timer_text, timer_rect)
        
        controls_text = self.font_tiny.render(
            "A/D: Move | W/SPACE: Jump | LEFT CLICK: Dig | ESC: Pause",
            True, TEXT_WHITE
        )
        controls_rect = controls_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20))
        self.screen.blit(controls_text, controls_rect)
    
    def run(self) -> None:
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    try:
        game = MoleGame()
        game.run()
    except Exception as e:
        import traceback
        with open('crash.log', 'w') as f:
            traceback.print_exc(file=f)
        raise
