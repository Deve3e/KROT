import pygame
import sys
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
    """Manages block textures for 3D rendering"""
    def __init__(self):
        self.textures = {}  # block_type -> pygame.Surface
        self.load_textures()
    
    def load_textures(self) -> None:
        """Load textures from game/textures/ folder"""
        texture_files = {
            "soil": "game/textures/soil.png",
            "grass": "game/textures/grass.png", 
            "plant": "game/textures/plant.png",
            "sky": "game/textures/sky.png"
        }
        
        for block_type, file_path in texture_files.items():
            try:
                texture = pygame.image.load(file_path)
                texture = texture.convert_alpha()
                self.textures[block_type] = texture
                print(f"Loaded texture: {block_type}")
            except Exception as e:
                print(f"Failed to load texture {block_type}: {e}")
                # Create fallback colored surface
                self.textures[block_type] = self._create_fallback_texture(block_type)
    
    def _create_fallback_texture(self, block_type: str) -> pygame.Surface:
        """Create a fallback colored texture if image loading fails"""
        surface = pygame.Surface((32, 32))
        
        if block_type == "soil":
            surface.fill((120, 80, 40))
        elif block_type == "grass":
            surface.fill((100, 150, 60))
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


class Minimap:
    """Minimap to show top-down view of underground tunnels and mole position"""
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.zoom = 0.5  # Scale factor for world coordinates
        self.center_x = x + width // 2
        self.center_y = y + height // 2
        
    def world_to_minimap(self, world_x: float, world_z: float) -> tuple:
        """Convert 3D world coordinates (x, z) to 2D minimap coordinates"""
        map_x = self.center_x + (world_x * self.zoom)
        map_y = self.center_y + (world_z * self.zoom)
        return (map_x, map_y)
    
    def draw(self, surface: pygame.Surface, player: 'Player') -> None:
        """Draw the minimap"""
        # Draw background
        pygame.draw.rect(surface, (50, 25, 0), (self.x, self.y, self.width, self.height))
        pygame.draw.rect(surface, (150, 100, 50), (self.x, self.y, self.width, self.height), 2)
        
        # Draw title
        font_small = pygame.font.Font(None, 16)
        title = font_small.render("Map", True, TEXT_WHITE)
        surface.blit(title, (self.x + 5, self.y + 2))
        
        # Draw dug tunnels
        for (grid_x, grid_y, grid_z) in player.dug_positions:
            world_x = grid_x * player.tile_size
            world_z = grid_z * player.tile_size
            map_x, map_y = self.world_to_minimap(world_x, world_z)
            
            # Only draw if within minimap bounds
            if (self.x < map_x < self.x + self.width and 
                self.y < map_y < self.y + self.height):
                pygame.draw.circle(surface, (100, 60, 20), (int(map_x), int(map_y)), 2)
        
        # Draw mole position
        mole_map_x, mole_map_y = self.world_to_minimap(player.x, player.z)
        pygame.draw.circle(surface, ACCENT_ORANGE, (int(mole_map_x), int(mole_map_y)), 4)
        
        # Draw direction indicator (small line showing forward direction)
        forward_scale = 10
        forward_x = mole_map_x - forward_scale
        forward_y = mole_map_y
        pygame.draw.line(surface, ACCENT_ORANGE, 
                        (int(mole_map_x), int(mole_map_y)), 
                        (int(forward_x), int(forward_y)), 2)


import math


class Camera3D:
    """First-person 3D camera (Minecraft-style)"""
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.fov = 90  # Field of view
        self.near = 0.1
        self.far = 1000
        self.aspect_ratio = screen_width / screen_height
        self.yaw = 0  # Rotation around Y axis (left/right)
        self.pitch = 0  # Rotation around X axis (up/down)
        self.position = [0, 0, 0]  # x, y, z position in world
        
    def set_position(self, x: float, y: float, z: float) -> None:
        """Set camera position"""
        self.position = [x, y, z]
    
    def get_forward_vector(self) -> tuple:
        """Get forward direction vector based on yaw and pitch"""
        forward_x = math.sin(math.radians(self.yaw))
        forward_y = -math.sin(math.radians(self.pitch))
        forward_z = math.cos(math.radians(self.yaw))
        return (forward_x, forward_y, forward_z)
    
    def project_point(self, x: float, y: float, z: float) -> tuple:
        """Project 3D point to 2D screen using perspective projection"""
        # Translate point relative to camera
        rel_x = x - self.position[0]
        rel_y = y - self.position[1]
        rel_z = z - self.position[2]
        
        # Rotate by camera angle
        cos_yaw = math.cos(math.radians(self.yaw))
        sin_yaw = math.sin(math.radians(self.yaw))
        
        rotated_x = rel_x * cos_yaw - rel_z * sin_yaw
        rotated_z = rel_x * sin_yaw + rel_z * cos_yaw
        rotated_y = rel_y
        
        # Only project points in front of camera
        if rotated_z <= 0.1:
            return None
        
        # Perspective projection
        scale = (self.screen_height / 2) / math.tan(math.radians(self.fov / 2))
        screen_x = (self.screen_width / 2) + (rotated_x / rotated_z) * scale
        screen_y = (self.screen_height / 2) + (rotated_y / rotated_z) * scale
        depth = rotated_z
        
        return (screen_x, screen_y, depth)


class Terrain3D:
    """3D terrain/block system for Minecraft-like rendering"""
    def __init__(self, texture_manager: TextureManager):
        self.texture_manager = texture_manager
        self.block_size = 1.0  # Size of each block
        self.blocks = {}  # Dictionary of block positions: (x, y, z) -> block_type
        self.dug_blocks = set()  # Track which blocks have been dug
        
    def add_block(self, x: int, y: int, z: int, block_type: str = "soil") -> None:
        """Add a block at position"""
        if (x, y, z) not in self.dug_blocks:
            self.blocks[(x, y, z)] = block_type
    
    def remove_block(self, x: int, y: int, z: int) -> None:
        """Remove a block (dig it)"""
        self.dug_blocks.add((x, y, z))
        if (x, y, z) in self.blocks:
            del self.blocks[(x, y, z)]
    
    def is_block_at(self, x: int, y: int, z: int) -> bool:
        """Check if there's a solid block at position"""
        return (x, y, z) in self.blocks and (x, y, z) not in self.dug_blocks
    
    def generate_terrain(self, layer: str = "underground") -> None:
        """Generate terrain for a layer"""
        self.blocks.clear()
        
        if layer == "underground":
            # Generate underground soil blocks in a reasonable area
            for x in range(-20, 21):
                for y in range(-10, 11):
                    for z in range(-20, 21):
                        # Create solid underground terrain
                        self.add_block(x, y, z, "soil")
            # Remove center area where player starts
            for x in range(-5, 6):
                for y in range(-3, 4):
                    for z in range(-5, 6):
                        self.remove_block(x, y, z)
        
        elif layer == "above_ground":
            # Generate above ground (sky and grass)
            for x in range(-20, 21):
                for z in range(-20, 21):
                    # Grass layer
                    self.add_block(x, 0, z, "grass")
                    # Dirt below
                    for y in range(-5, 0):
                        self.add_block(x, y, z, "soil")
            
            # Add some obstacles (vegetables/plants)
            self.add_block(-8, 0, -8, "plant")
            self.add_block(-8, 0, 8, "plant")
            self.add_block(8, 0, -8, "plant")
            self.add_block(8, 0, 8, "plant")
    
    def draw(self, surface: pygame.Surface, camera: Camera3D) -> None:
        """Draw all visible blocks"""
        # Collect blocks with depth for sorting
        visible_blocks = []
        
        for (x, y, z), block_type in self.blocks.items():
            proj = camera.project_point(x, y, z)
            if proj is not None:
                screen_x, screen_y, depth = proj
                visible_blocks.append(((screen_x, screen_y, depth), block_type, (x, y, z)))
        
        # Sort by depth (back to front) for proper occlusion
        visible_blocks.sort(key=lambda item: item[0][2], reverse=True)
        
        # Draw blocks
        for (screen_x, screen_y, depth), block_type, (world_x, world_y, world_z) in visible_blocks:
            if -100 < screen_x < camera.screen_width + 100 and -100 < screen_y < camera.screen_height + 100:
                self._draw_block(surface, screen_x, screen_y, depth, block_type)
    
    def _draw_block(self, surface: pygame.Surface, screen_x: float, screen_y: float, depth: float, block_type: str) -> None:
        """Draw a single block with texture"""
        # Size decreases with distance
        size = max(4, 32 / (depth + 0.5))
        
        # Get texture
        texture = self.texture_manager.get_texture(block_type)
        if texture:
            # Scale texture to block size
            scaled_texture = pygame.transform.scale(texture, (int(size), int(size)))
            rect = scaled_texture.get_rect(center=(int(screen_x), int(screen_y)))
            surface.blit(scaled_texture, rect)
        else:
            # Fallback to colored rectangle
            color = (120, 80, 40) if block_type == "soil" else (100, 150, 60)
            rect = pygame.Rect(screen_x - size/2, screen_y - size/2, size, size)
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, (50, 50, 50), rect, 1)


class Player:
    """Player (Mole) class with 3D movement"""
    def __init__(self, start_x: float, start_y: float, start_z: float, size: int = 20):
        # 3D position
        self.x = start_x
        self.y = start_y
        self.z = start_z
        
        self.size = size
        self.speed = 0.2
        self.dig_speed = 0.3
        self.is_digging = False
        self.dig_cooldown = 0
        self.dig_target_y = start_y
        self.current_layer = "underground"  # underground or above_ground
        self.dug_tunnels = set()  # Track dug positions
    
    def handle_input(self, keys, camera: Camera3D, terrain: Terrain3D) -> None:
        """Handle keyboard input for 3D movement (Minecraft-style)"""
        # Get forward and right vectors based on camera angle
        forward_x = math.sin(math.radians(camera.yaw))
        forward_z = math.cos(math.radians(camera.yaw))
        right_x = -math.cos(math.radians(camera.yaw))
        right_z = math.sin(math.radians(camera.yaw))
        
        # W/S for forward/backward
        if keys[pygame.K_w]:
            new_x = self.x + forward_x * self.speed
            new_z = self.z + forward_z * self.speed
            if not terrain.is_block_at(int(new_x), int(self.y), int(new_z)):
                self.x = new_x
                self.z = new_z
        elif keys[pygame.K_s]:
            new_x = self.x - forward_x * self.speed
            new_z = self.z - forward_z * self.speed
            if not terrain.is_block_at(int(new_x), int(self.y), int(new_z)):
                self.x = new_x
                self.z = new_z
        
        # A/D for strafing left/right
        if keys[pygame.K_a]:
            new_x = self.x + right_x * self.speed
            new_z = self.z + right_z * self.speed
            if not terrain.is_block_at(int(new_x), int(self.y), int(new_z)):
                self.x = new_x
                self.z = new_z
        elif keys[pygame.K_d]:
            new_x = self.x - right_x * self.speed
            new_z = self.z - right_z * self.speed
            if not terrain.is_block_at(int(new_x), int(self.y), int(new_z)):
                self.x = new_x
                self.z = new_z
        
        # Mouse for camera rotation
        mouse_buttons = pygame.mouse.get_pressed()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        # Camera rotation could be added here if needed
        
        # Q for dig up, E for dig down
        if keys[pygame.K_q]:
            self.dig_up(terrain)
        elif keys[pygame.K_e]:
            self.dig_down(terrain)
    
    def dig_up(self, terrain: Terrain3D) -> None:
        """Dig upward"""
        if self.dig_cooldown <= 0:
            # Remove block above
            for dy in range(1, 3):
                block_x, block_y, block_z = int(self.x), int(self.y) + dy, int(self.z)
                terrain.remove_block(block_x, block_y, block_z)
            self.dig_cooldown = 15
    
    def dig_down(self, terrain: Terrain3D) -> None:
        """Dig downward"""
        if self.dig_cooldown <= 0:
            # Remove block below
            for dy in range(1, 3):
                block_x, block_y, block_z = int(self.x), int(self.y) - dy, int(self.z)
                terrain.remove_block(block_x, block_y, block_z)
            self.dig_cooldown = 15
    
    def update(self) -> None:
        """Update player state"""
        if self.dig_cooldown > 0:
            self.dig_cooldown -= 1
    
    def draw(self, surface: pygame.Surface, camera: Camera3D) -> None:
        """Draw mole indicator on screen"""
        # Draw a simple crosshair/indicator in the center
        center_x = camera.screen_width // 2
        center_y = camera.screen_height // 2
        pygame.draw.circle(surface, ACCENT_ORANGE, (center_x, center_y), 5)
        pygame.draw.line(surface, ACCENT_ORANGE, (center_x - 15, center_y), (center_x + 15, center_y), 1)
        pygame.draw.line(surface, ACCENT_ORANGE, (center_x, center_y - 15), (center_x, center_y + 15), 1)


class Button:
    """Button class for UI elements"""
    def __init__(self, x: int, y: int, width: int, height: int, text: str, font_size: int = 32):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font_size = font_size
        self.is_hovered = False
        self.font = pygame.font.Font(None, font_size)
        
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the button on the surface"""
        # Button background
        color = BUTTON_HOVER if self.is_hovered else (255, 190, 133)
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, (255, 154, 66), self.rect, 3, border_radius=10)
        
        # Button text
        text_surface = self.font.render(self.text, True, BG_COLOR if self.is_hovered else TEXT_WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def is_clicked(self, mouse_pos: tuple) -> bool:
        """Check if button is clicked"""
        return self.rect.collidepoint(mouse_pos)
    
    def update_hover(self, mouse_pos: tuple) -> None:
        """Update hover state based on mouse position"""
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
        
        # Initialize texture manager
        self.texture_manager = TextureManager()
        
        # Try to load Supply Center font for title, fallback to default
        try:
            self.font_title = pygame.font.SysFont("Supply Center", 130, bold=True)
        except:
            self.font_title = self.font_large
        
        # Initialize image background (looks for "bg_image.png" in the game/addinfo folder)
        self.bg_image = ImageBackground("game/addinfo/bg_image.png", SCREEN_WIDTH, SCREEN_HEIGHT)
        self.bg_offset = 0.0
        self.bg_offset_direction = 1
        self.bg_offset_min = -50
        self.bg_offset_max = 50
        self.bg_offset_speed = 0.25
        
        # Initialize buttons for home screen
        self._init_home_buttons()
        
        # Initialize 3D camera
        self.camera = Camera3D(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.camera.set_position(0, 2, 0)  # Start at eye level
        self.camera.yaw = 0  # Looking forward
        self.camera.pitch = 0
        
        # Initialize terrain for both layers
        self.terrain_underground = Terrain3D(self.texture_manager)
        self.terrain_underground.generate_terrain("underground")
        
        self.terrain_above_ground = Terrain3D(self.texture_manager)
        self.terrain_above_ground.generate_terrain("above_ground")
        
        # Initialize minimap for opposite layer view
        self.minimap = Minimap(SCREEN_WIDTH - 210, 10, 200, 150)
        
        # Initialize player (mole) - start underground
        self.player = Player(0, 1, 0)
        
        # Mouse look variables
        self.mouse_sensitivity = 0.2
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        
    def _init_home_buttons(self) -> None:
        """Initialize buttons for the home screen"""
        button_width = 250
        button_height = 60
        button_x = (SCREEN_WIDTH - button_width) // 2
        
        self.play_button = Button(button_x, 300, button_width, button_height, "PLAY")
        self.instructions_button = Button(button_x, 400, button_width, button_height, "HOW TO PLAY")
        self.settings_button = Button(button_x, 500, button_width, button_height, "SETTINGS")
        self.quit_button = Button(button_x, 600, button_width, button_height, "EXIT")
        
    def draw_home_screen(self) -> None:
        """Draw the home screen"""
        # Draw image background if available, with slow horizontal pan around center
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
        
        # Draw decorative elements
        self._draw_decorative_elements()
        
        # Draw title
        title_text = self.font_title.render("KROT", True, (255, 255, 240))  # Using Supply Center font
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 120))
        self.screen.blit(title_text, title_rect)
        
        # Draw subtitle
        subtitle_text = self.font_small.render("Garden Defense Challenge", True, ACCENT_ORANGE)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 210))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Draw buttons
        self.play_button.draw(self.screen)
        self.instructions_button.draw(self.screen)
        self.settings_button.draw(self.screen)
        self.quit_button.draw(self.screen)
        
        # Draw footer text
        footer_text = self.font_tiny.render("Can you escape the garden before the gardener catches you?", True, TEXT_WHITE)
        footer_rect = footer_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        self.screen.blit(footer_text, footer_rect)
        
    def _draw_decorative_elements(self) -> None:
        """Draw decorative elements on home screen"""
        # Decorative lines removed per user request
        pass
        
    def draw_instructions_screen(self) -> None:
        """Draw the instructions/how to play screen"""
        self.screen.fill(BG_COLOR)
        
        # Title
        title_text = self.font_large.render("HOW TO PLAY", True, GRASS_GREEN)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 40))
        self.screen.blit(title_text, title_rect)
        
        # Instructions
        instructions = [
            "OBJECTIVE: Escape from the garden to win!",
            "",
            "3D FIRST-PERSON CONTROLS:",
            "MOUSE: Look around (camera rotation)",
            "WASD: Move forward/backward and strafe",
            "Q: Dig up (remove blocks above)",
            "E: Dig down (remove blocks below)",
            "TAB: Switch between underground/above-ground",
            "",
            "GAMEPLAY:",
            "- You start underground as a mole in the garden",
            "- Dig through soil blocks to create tunnels",
            "- Switch layers to navigate both underground and surface",
            "- Find holes to escape, but the gardener keeps blocking them",
            "- The gardener plants vegetables and can't see behind them",
            "- If seen by the gardener, you'll be chased - RUN!",
            "- Reach any remaining hole and escape to win",
            "",
            "3D NAVIGATION: Use mouse to look around like in Minecraft!",
            "Textures are loaded from game/textures/ folder.",
            "",
            "TIPS: Plan your escape route and avoid the gardener!",
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
        
        # Back button
        back_button = Button(50, SCREEN_HEIGHT - 80, 150, 50, "BACK")
        back_button.draw(self.screen)
        
        return back_button
        
    def draw_settings_screen(self) -> None:
        """Draw the settings screen"""
        self.screen.fill(BG_COLOR)
        
        # Title
        title_text = self.font_large.render("SETTINGS", True, GRASS_GREEN)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 40))
        self.screen.blit(title_text, title_rect)
        
        # Settings options (placeholder for future)
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
        
        # Back button
        back_button = Button(50, SCREEN_HEIGHT - 80, 150, 50, "BACK")
        back_button.draw(self.screen)
        
        return back_button
        
    def handle_events(self) -> None:
        """Handle game events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEMOTION and self.state == GameState.PLAYING:
                # Mouse look for camera
                mouse_x, mouse_y = event.rel
                self.camera.yaw += mouse_x * self.mouse_sensitivity
                self.camera.pitch -= mouse_y * self.mouse_sensitivity
                self.camera.pitch = max(-89, min(89, self.camera.pitch))  # Clamp pitch
            
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos
                
                if self.state == GameState.HOME:
                    self.play_button.update_hover(mouse_pos)
                    self.instructions_button.update_hover(mouse_pos)
                    self.settings_button.update_hover(mouse_pos)
                    self.quit_button.update_hover(mouse_pos)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                
                if self.state == GameState.HOME:
                    if self.play_button.is_clicked(mouse_pos):
                        self.state = GameState.PLAYING
                        pygame.mouse.set_visible(False)
                        pygame.event.set_grab(True)
                    elif self.instructions_button.is_clicked(mouse_pos):
                        self.state = GameState.INSTRUCTIONS
                    elif self.settings_button.is_clicked(mouse_pos):
                        self.state = GameState.SETTINGS
                    elif self.quit_button.is_clicked(mouse_pos):
                        self.running = False
                
                elif self.state == GameState.INSTRUCTIONS:
                    back_button = Button(50, SCREEN_HEIGHT - 80, 150, 50, "BACK")
                    if back_button.is_clicked(mouse_pos):
                        self.state = GameState.HOME
                
                elif self.state == GameState.SETTINGS:
                    back_button = Button(50, SCREEN_HEIGHT - 80, 150, 50, "BACK")
                    if back_button.is_clicked(mouse_pos):
                        self.state = GameState.HOME
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Return to home from any screen
                    if self.state != GameState.HOME:
                        self.state = GameState.HOME
                        pygame.mouse.set_visible(True)
                        pygame.event.set_grab(False)
                
                elif event.key == pygame.K_TAB and self.state == GameState.PLAYING:
                    # Switch layers
                    if self.player.current_layer == "underground":
                        self.player.current_layer = "above_ground"
                        self.camera.set_position(self.player.x, self.player.y + 1, self.player.z)
                    else:
                        self.player.current_layer = "underground"
                        self.camera.set_position(self.player.x, self.player.y + 1, self.player.z)
    
    def update(self) -> None:
        """Update game logic"""
        if self.state == GameState.HOME and self.bg_image.image_loaded:
            self.bg_offset += self.bg_offset_direction * self.bg_offset_speed
            if self.bg_offset >= self.bg_offset_max:
                self.bg_offset = self.bg_offset_max
                self.bg_offset_direction = -1
            elif self.bg_offset <= self.bg_offset_min:
                self.bg_offset = self.bg_offset_min
                self.bg_offset_direction = 1
        
        elif self.state == GameState.PLAYING:
            # Get appropriate terrain based on current layer
            current_terrain = self.terrain_underground if self.player.current_layer == "underground" else self.terrain_above_ground
            
            # Handle player movement based on keyboard input
            keys = pygame.key.get_pressed()
            self.player.handle_input(keys, self.camera, current_terrain)
            self.player.update()
            
            # Update camera to follow player
            self.camera.set_position(self.player.x, self.player.y + 1, self.player.z)
    
    def draw(self) -> None:
        """Draw the current screen"""
        if self.state == GameState.HOME:
            self.draw_home_screen()
        elif self.state == GameState.INSTRUCTIONS:
            self.draw_instructions_screen()
        elif self.state == GameState.SETTINGS:
            self.draw_settings_screen()
        elif self.state == GameState.PLAYING:
            self.draw_playing_screen()
        
        pygame.display.flip()
    
    def draw_playing_screen(self) -> None:
        """Draw the main game screen with single-layer 3D view"""
        self.screen.fill((135, 206, 235))  # Sky blue background
        
        # Get appropriate terrain based on current layer
        current_terrain = self.terrain_underground if self.player.current_layer == "underground" else self.terrain_above_ground
        
        # Draw 3D terrain
        current_terrain.draw(self.screen, self.camera)
        
        # Draw player crosshair
        self.player.draw(self.screen, self.camera)
        
        # Draw current layer indicator
        layer_text = self.font_small.render(
            f"Layer: {'UNDERGROUND' if self.player.current_layer == 'underground' else 'ABOVE GROUND'}", 
            True, TEXT_WHITE
        )
        layer_rect = layer_text.get_rect(topleft=(10, 10))
        self.screen.blit(layer_text, layer_rect)
        
        # Draw position info
        pos_text = self.font_tiny.render(
            f"X: {self.player.x:.1f} Y: {self.player.y:.1f} Z: {self.player.z:.1f}", 
            True, TEXT_WHITE
        )
        pos_rect = pos_text.get_rect(topleft=(10, 40))
        self.screen.blit(pos_text, pos_rect)
        
        # Draw minimap (opposite layer)
        self.screen.fill((50, 25, 0), pygame.Rect(SCREEN_WIDTH - 210, 10, 200, 150))
        pygame.draw.rect(self.screen, (150, 100, 50), pygame.Rect(SCREEN_WIDTH - 210, 10, 200, 150), 2)
        
        minimap_text = self.font_tiny.render("Map", True, TEXT_WHITE)
        self.screen.blit(minimap_text, (SCREEN_WIDTH - 200, 15))
        
        # Draw a simple mole indicator on minimap
        minimap_mole_x = SCREEN_WIDTH - 110
        minimap_mole_y = 85
        pygame.draw.circle(self.screen, ACCENT_ORANGE, (int(minimap_mole_x), int(minimap_mole_y)), 4)
        
        # Draw controls info
        controls_text = self.font_tiny.render(
            "WASD: Move | ◄►: Rotate | ▲▼: Look | Q: DIG UP | E: DIG DOWN | TAB: Layer | ESC: Home", 
            True, TEXT_WHITE
        )
        controls_rect = controls_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20))
        self.screen.blit(controls_text, controls_rect)
    
    def run(self) -> None:
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)  # 60 FPS
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = MoleGame()
    game.run()
