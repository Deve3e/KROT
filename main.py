# pyrefly: ignore [missing-import]
import pygame
import sys
import math
import os
from enum import Enum
from typing import Optional

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

# Colors
BG_COLOR = (34, 34, 34)  # Dark gray
GRASS_GREEN = (76, 175, 80)  # Green for grass theme
SOIL_BROWN = (139, 69, 19)  # Brown for soil
TEXT_WHITE = (255, 255, 255)
ACCENT_ORANGE = (255, 165, 0)  # Orange for accents
BUTTON_HOVER = (255, 154, 66)  # Bright gold on hover


class TextureManager:
    """Manages block textures for 2D rendering"""
    def __init__(self, block_size: int = 40):
        self.textures = {}  # block_type -> pygame.Surface
        self.block_size = block_size
        self.load_textures()
    
    def load_textures(self) -> None:
        """Load textures from textures/ folder"""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        texture_files = {
            "soil": os.path.join(base_dir, "textures", "soil.png"),
            "grass": os.path.join(base_dir, "textures", "grass.png"), 
            "plant": os.path.join(base_dir, "textures", "plant.png"),
            "sky": os.path.join(base_dir, "textures", "sky.png")
        }
        
        for block_type, file_path in texture_files.items():
            try:
                texture = pygame.image.load(file_path)
                texture = texture.convert_alpha()
                texture = pygame.transform.scale(texture, (self.block_size, self.block_size))
                self.textures[block_type] = texture
                print(f"Loaded texture: {block_type}")
            except Exception as e:
                print(f"Failed to load texture {block_type}: {e}")
                self.textures[block_type] = self._create_fallback_texture(block_type)
    
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
        else:
            surface.fill((100, 100, 100))
        
        return surface
    
    def get_texture(self, block_type: str) -> pygame.Surface:
        """Get texture for block type"""
        return self.textures.get(block_type, self.textures.get("soil", None))


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
        
    def add_block(self, x: int, y: int, block_type: str = "soil") -> None:
        self.blocks[(x, y)] = block_type
    
    def remove_block(self, x: int, y: int) -> None:
        if (x, y) in self.blocks:
            del self.blocks[(x, y)]
    
    def is_block_at(self, x: int, y: int) -> bool:
        return (x, y) in self.blocks
    
    def generate_terrain(self) -> None:
        self.blocks.clear()
        
        # Surface grass at y = 0, soil below
        for x in range(-50, 51):
            for y in range(0, 30):
                if y == 0:
                    self.add_block(x, y, "grass")
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
                    texture = self.texture_manager.get_texture(block_type)
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
        
    def draw(self, surface: pygame.Surface, player: 'Player', terrain: 'Terrain2D') -> None:
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
                    color = (76, 175, 80) if block_type == "grass" else (100, 50, 10)
                    mx = self.x + (bx - start_bx) * map_block_w
                    my = self.y + (by - start_by) * map_block_h
                    pygame.draw.rect(surface, color, (mx, my, max(1, map_block_w), max(1, map_block_h)))
        
        player_mx = self.x + (player.x - start_bx) * map_block_w
        player_my = self.y + (player.y - start_by) * map_block_h
        pygame.draw.circle(surface, ACCENT_ORANGE, (int(player_mx), int(player_my)), 3)


class Player:
    """Player (Mole) class with 2D platformer movement"""
    def __init__(self, start_x: float, start_y: float, size: float = 0.8):
        self.x = start_x
        self.y = start_y
        self.width = size
        self.height = size
        
        self.speed = 0.15
        self.dig_cooldown = 0
        
        self.vy = 0.0
        self.is_on_ground = False
        
    def handle_input(self, keys, camera: Camera2D, terrain: Terrain2D, mouse_buttons, mouse_pos) -> None:
        dx = 0
        if keys[pygame.K_a]:
            dx -= self.speed
        if keys[pygame.K_d]:
            dx += self.speed
            
        if dx != 0:
            new_x = self.x + dx
            if not self._check_collision(new_x, self.y, terrain):
                self.x = new_x
                
        if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and self.is_on_ground:
            self.vy = -0.4
            self.is_on_ground = False
            
        if self.dig_cooldown > 0:
            self.dig_cooldown -= 1
            
        if mouse_buttons[0] and self.dig_cooldown <= 0:
            world_x, world_y = camera.screen_to_world(mouse_pos[0], mouse_pos[1])
            bx, by = int(math.floor(world_x)), int(math.floor(world_y))
            
            dist = math.hypot(self.x + self.width/2 - bx - 0.5, self.y + self.height/2 - by - 0.5)
            if dist <= 4.0:
                if terrain.is_block_at(bx, by):
                    terrain.remove_block(bx, by)
                    self.dig_cooldown = 15
    
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
            if terrain.is_block_at(bx, by):
                return True
        return False
        
    def update(self, terrain: Terrain2D) -> None:
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
    
    def draw(self, surface: pygame.Surface, camera: Camera2D) -> None:
        screen_x, screen_y = camera.world_to_screen(self.x, self.y)
        pixel_width = int(self.width * camera.block_size)
        pixel_height = int(self.height * camera.block_size)
        
        rect = pygame.Rect(screen_x, screen_y, pixel_width, pixel_height)
        pygame.draw.rect(surface, ACCENT_ORANGE, rect, border_radius=8)
        
        # Eyes
        pygame.draw.circle(surface, (0, 0, 0), (int(screen_x + pixel_width * 0.7), int(screen_y + pixel_height * 0.3)), 3)


class Button:
    """Button class for UI elements"""
    def __init__(self, x: int, y: int, width: int, height: int, text: str, font_size: int = 32):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font_size = font_size
        self.is_hovered = False
        self.font = pygame.font.Font(None, font_size)
        
    def draw(self, surface: pygame.Surface) -> None:
        color = BUTTON_HOVER if self.is_hovered else (255, 190, 133)
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, (255, 154, 66), self.rect, 3, border_radius=10)
        
        text_surface = self.font.render(self.text, True, BG_COLOR if self.is_hovered else TEXT_WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def is_clicked(self, mouse_pos: tuple) -> bool:
        return self.rect.collidepoint(mouse_pos)
    
    def update_hover(self, mouse_pos: tuple) -> None:
        self.is_hovered = self.rect.collidepoint(mouse_pos)


class MoleGame:
    """Main game class"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
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
        
        self.player = Player(0, 26)  # Start underground in the cave
        
    def reset_game(self) -> None:
        """Reset the game state for a new playthrough"""
        self.terrain.generate_terrain()
        self.player = Player(0, 26)
        self.camera.set_position(self.player.x + self.player.width/2, self.player.y + self.player.height/2)
        
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
        self.screen.fill(BG_COLOR)
        
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
        self.screen.fill(BG_COLOR)
        
        title_text = self.font_large.render("SETTINGS", True, GRASS_GREEN)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 40))
        self.screen.blit(title_text, title_rect)
        
        settings_text = [
            "Volume: 100%",
            "Difficulty: Normal",
            "Sound Effects: ON",
            "Music: ON",
        ]
        
        y_offset = 200
        for setting in settings_text:
            text = self.font_small.render(setting, True, TEXT_WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 80
        
        back_button = Button(50, SCREEN_HEIGHT - 80, 150, 50, "BACK")
        back_button.draw(self.screen)
        
    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos
                if self.state == GameState.HOME:
                    self.play_button.update_hover(mouse_pos)
                    self.instructions_button.update_hover(mouse_pos)
                    self.settings_button.update_hover(mouse_pos)
                    self.quit_button.update_hover(mouse_pos)
                elif self.state == GameState.PAUSED:
                    self.resume_button.update_hover(mouse_pos)
                    self.pause_settings_button.update_hover(mouse_pos)
                    self.exit_to_home_button.update_hover(mouse_pos)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
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
                
                elif self.state == GameState.INSTRUCTIONS:
                    back_button = Button(50, SCREEN_HEIGHT - 80, 150, 50, "BACK")
                    if back_button.is_clicked(mouse_pos):
                        self.state = self.previous_state
                
                elif self.state == GameState.SETTINGS:
                    back_button = Button(50, SCREEN_HEIGHT - 80, 150, 50, "BACK")
                    if back_button.is_clicked(mouse_pos):
                        self.state = self.previous_state
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == GameState.PLAYING:
                        self.state = GameState.PAUSED
                    elif self.state == GameState.PAUSED:
                        self.state = GameState.PLAYING
                    elif self.state in [GameState.INSTRUCTIONS, GameState.SETTINGS]:
                        self.state = self.previous_state
    
    def update(self) -> None:
        if self.state == GameState.HOME and self.bg_image.image_loaded:
            self.bg_offset += self.bg_offset_direction * self.bg_offset_speed
            if self.bg_offset >= self.bg_offset_max:
                self.bg_offset = self.bg_offset_max
                self.bg_offset_direction = -1
            elif self.bg_offset <= self.bg_offset_min:
                self.bg_offset = self.bg_offset_min
                self.bg_offset_direction = 1
        
        elif self.state == GameState.PLAYING:
            keys = pygame.key.get_pressed()
            mouse_buttons = pygame.mouse.get_pressed()
            mouse_pos = pygame.mouse.get_pos()
            
            self.player.handle_input(keys, self.camera, self.terrain, mouse_buttons, mouse_pos)
            self.player.update(self.terrain)
            self.camera.set_position(self.player.x + self.player.width/2, self.player.y + self.player.height/2)
    
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
    
    def draw_playing_screen(self) -> None:
        self.screen.fill((135, 206, 235))  # Sky blue background
        
        self.terrain.draw(self.screen, self.camera)
        self.player.draw(self.screen, self.camera)
        
        pos_text = self.font_tiny.render(
            f"X: {self.player.x:.1f} Y: {self.player.y:.1f}", 
            True, TEXT_WHITE
        )
        pos_rect = pos_text.get_rect(topleft=(10, 10))
        self.screen.blit(pos_text, pos_rect)
        
        self.minimap.draw(self.screen, self.player, self.terrain)
        
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
