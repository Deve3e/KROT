# KROT - 3D Minecraft-Style Mole Game

A 3D first-person mole escape game where you dig through underground tunnels and navigate above ground to escape the garden!

## Features

- **3D First-Person Perspective**: Full Minecraft-style 3D rendering with mouse look
- **Dual Layer System**: Switch between underground and above-ground views
- **Block-Based Terrain**: Dig through soil blocks to create tunnels
- **Texture System**: Customizable block textures
- **Real-time 3D Rendering**: Perspective projection with depth sorting

## Controls

### Menu Navigation
- **Mouse**: Click buttons to navigate menus
- **ESC**: Return to main menu

### 3D Gameplay
- **Mouse**: Look around (camera rotation)
- **WASD**: Move forward/backward and strafe left/right
- **Q**: Dig up (remove blocks above)
- **E**: Dig down (remove blocks below)
- **TAB**: Switch between underground and above-ground layers
- **ESC**: Return to main menu

## Texture System

The game supports custom textures for all block types. Place your texture files in the `game/textures/` folder.

### Supported Textures

- `soil.png` - Underground soil blocks
- `grass.png` - Above-ground grass blocks
- `plant.png` - Vegetable/plant obstacles
- `sky.png` - Sky background (currently unused)

### Texture Requirements

- **Format**: PNG, JPG, or BMP
- **Recommended Size**: 32x32 or 64x64 pixels
- **Square Aspect Ratio**: Width should equal height
- **Transparency**: PNG files support transparency

### Adding Custom Textures

1. Create or find texture images
2. Save them with the correct filenames in `game/textures/`
3. Restart the game to load new textures

### Generating Placeholder Textures

Run the included texture generator to create basic placeholder textures:

```bash
python game/generate_textures.py
```

This will create simple colored textures with basic patterns that you can replace with your own art.

## Game Mechanics

### Underground Layer
- Navigate through 3D soil blocks
- Dig tunnels by removing blocks with Q/E keys
- Avoid getting trapped by digging strategically

### Above-Ground Layer
- Navigate the garden surface
- Avoid gardener (future feature)
- Find escape holes to win

### Layer Switching
- Use TAB to switch between layers
- Each layer has its own terrain and obstacles
- Plan your escape route across both layers

## Development

The game uses a modular architecture:

- `TextureManager`: Handles loading and managing block textures
- `Camera3D`: First-person 3D camera with mouse look
- `Terrain3D`: Block-based 3D world generation and rendering
- `Player`: Mole character with 3D movement and digging

## Future Features

- Gardener AI that patrols and blocks escape holes
- Multiple escape holes with different buffs/debuffs
- Sound effects and background music
- Save/load game progress
- More block types and terrain features

## File Structure

```
game/
├── main.py                 # Main game file
├── generate_textures.py    # Texture generator script
├── textures/               # Block texture files
│   ├── soil.png
│   ├── grass.png
│   ├── plant.png
│   └── sky.png
└── addinfo/               # Additional assets
    └── bg_image.png       # Menu background
```

Enjoy digging your way to freedom! 🐭