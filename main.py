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


class Player:
    """Player (Mole) class"""
    def __init__(self, start_x: int, start_y: int, size: int = 20):
        self.x = start_x
        self.y = start_y
        self.size = size
        self.velocity_x = 0
        self.velocity_y = 0
        self.speed = 5
        self.is_digging = False
        self.dig_cooldown = 0
        self.dig_duration = 10  # frames
        self.dug_tiles = set()  # Track where mole has dug
        self.tile_size = 30  # Grid tile size for digging
        
        # Start position is automatically dug
        self._mark_dug(start_x, start_y)
        
    def _mark_dug(self, x: int, y: int) -> None:
        """Mark a position and surrounding area as dug"""
        # Convert to grid position
        grid_x = int(x // self.tile_size)
        grid_y = int(y // self.tile_size)
        
        # Mark center and surrounding tiles as dug
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                self.dug_tiles.add((grid_x + dx, grid_y + dy))
    
    def _is_dug(self, x: int, y: int) -> bool:
        """Check if a position has been dug"""
        grid_x = int(x // self.tile_size)
        grid_y = int(y // self.tile_size)
        return (grid_x, grid_y) in self.dug_tiles
    
    def handle_input(self, keys) -> None:
        """Handle keyboard input for movement"""
        new_x = self.x
        new_y = self.y
        moved = False
        
        # Horizontal movement
        if keys[pygame.K_LEFT]:
            new_x = self.x - self.speed
            moved = True
        elif keys[pygame.K_RIGHT]:
            new_x = self.x + self.speed
            moved = True
        
        # Vertical movement
        if keys[pygame.K_UP]:
            new_y = self.y - self.speed
            moved = True
        elif keys[pygame.K_DOWN]:
            new_y = self.y + self.speed
            moved = True
        
        # Only allow movement if the new position is dug
        if moved:
            if self._is_dug(new_x, new_y):
                self.x = new_x
                self.y = new_y
            # If not dug, movement is blocked - velocity stays 0
            self.velocity_x = 0
            self.velocity_y = 0
        else:
            self.velocity_x = 0
            self.velocity_y = 0
    
    def update(self, screen_width: int, screen_height: int) -> None:
        """Update player position with bounds checking"""
        # Bounds checking - keep player on screen
        self.x = max(self.size, min(self.x, screen_width - self.size))
        self.y = max(self.size, min(self.y, screen_height - self.size))
        
        # Update dig cooldown
        if self.dig_cooldown > 0:
            self.dig_cooldown -= 1
        
        if self.is_digging:
            self.dig_duration -= 1
            if self.dig_duration <= 0:
                self.is_digging = False
                self.dig_duration = 10
    
    def start_dig(self) -> None:
        """Start digging action and mark tiles as dug"""
        if self.dig_cooldown <= 0:
            self.is_digging = True
            self.dig_duration = 10
            self.dig_cooldown = 30  # 0.5 seconds at 60 FPS
            # Mark the area around the mole as dug
            self._mark_dug(self.x, self.y)
    
    def draw(self, surface: pygame.Surface, view_type: str) -> None:
        """Draw the player (mole)"""
        # Draw main body (circle)
        pygame.draw.circle(surface, (139, 69, 19), (int(self.x), int(self.y)), self.size)
        
        # Draw eyes
        eye_offset = self.size // 3
        eye_size = 3
        pygame.draw.circle(surface, TEXT_WHITE, (int(self.x - eye_offset), int(self.y - eye_offset)), eye_size)
        pygame.draw.circle(surface, TEXT_WHITE, (int(self.x + eye_offset), int(self.y - eye_offset)), eye_size)
        
        # Draw digging effect
        if self.is_digging:
            for i in range(3):
                offset = i * 5
                pygame.draw.circle(surface, ACCENT_ORANGE, (int(self.x), int(self.y + self.size + offset)), 3)
                pygame.draw.circle(surface, ACCENT_ORANGE, (int(self.x), int(self.y - self.size - offset)), 3)
    
    def draw_dug_tunnels(self, surface: pygame.Surface, mid_y: int) -> None:
        """Draw the dug tunnel paths"""
        for grid_x, grid_y in self.dug_tiles:
            x = grid_x * self.tile_size + self.tile_size // 2
            y = grid_y * self.tile_size + self.tile_size // 2
            
            # Only draw in underground section
            if y >= mid_y - self.tile_size:
                # Draw tunnel as a lighter colored circle
                pygame.draw.circle(surface, (169, 109, 59), (x, y), self.tile_size // 2)
                pygame.draw.circle(surface, (139, 69, 19), (x, y), self.tile_size // 2, 1)


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
        
        # Initialize player (mole) - start in the bottom left area (underground)
        self.player = Player(50, SCREEN_HEIGHT - 50)
        
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
            "MOVEMENT: Use ARROW KEYS to move underground",
            "DIG: SPACE BAR to dig and move upward",
            "",
            "GAMEPLAY:",
            "- You start underground as a mole in the garden",
            "- Find holes to escape, but the gardener keeps blocking them",
            "- The gardener plants vegetables and can't see behind them",
            "- If seen by the gardener, you'll be chased - RUN!",
            "- Reach any remaining hole and escape to win",
            "",
            "SPECIAL EFFECTS: Last hole escape might give you buffs/debuffs",
            "like slowness or night vision.",
            "",
            "TIPS: Plan your escape route and avoid the gardener!",
        ]
        
        y_offset = 120
        line_height = 35
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
                
                elif event.key == pygame.K_SPACE and self.state == GameState.PLAYING:
                    # Start digging
                    self.player.start_dig()
    
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
            # Handle player movement based on keyboard input
            keys = pygame.key.get_pressed()
            self.player.handle_input(keys)
            self.player.update(SCREEN_WIDTH, SCREEN_HEIGHT)
    
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
        """Draw the main game screen (placeholder)"""
        self.screen.fill(BG_COLOR)
        
        # Split screen visual
        mid_y = SCREEN_HEIGHT // 2
        
        # Above ground section
        pygame.draw.rect(self.screen, GRASS_GREEN, (0, 0, SCREEN_WIDTH, mid_y))
        grass_text = self.font_medium.render("ABOVE GROUND - GARDEN VIEW", True, TEXT_WHITE)
        grass_rect = grass_text.get_rect(center=(SCREEN_WIDTH // 2, 30))
        self.screen.blit(grass_text, grass_rect)
        
        # Underground section
        pygame.draw.rect(self.screen, SOIL_BROWN, (0, mid_y, SCREEN_WIDTH, mid_y))
        soil_text = self.font_medium.render("UNDERGROUND - MOLE VIEW", True, TEXT_WHITE)
        soil_rect = soil_text.get_rect(center=(SCREEN_WIDTH // 2, mid_y + 30))
        self.screen.blit(soil_text, soil_rect)
        
        # Draw dug tunnels in underground section
        self.player.draw_dug_tunnels(self.screen, mid_y)
        
        # Draw the mole in the underground section
        # Only draw the mole if it's in the underground area
        if self.player.y >= mid_y - self.player.size:
            self.player.draw(self.screen, "underground")
        
        # Controls info
        controls_text = self.font_tiny.render("ARROW KEYS: Move | SPACE: Dig | ESC: Home", True, TEXT_WHITE)
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
