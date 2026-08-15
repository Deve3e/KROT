# KROT — Garden Defense Challenge

A 2D platformer where you play as a mole trying to survive underground. Dig through soil, dodge the gardener on the surface, avoid venomous snakes underground, and destroy 10 seeds to win!

---

## Objective

**Destroy 10 seeds** planted by the gardener before the gardener or snakes catch you.

---

## Features

- **2D Platformer**: Side-scrolling platformer with gravity, jumping, and digging
- **Procedural Terrain**: Randomly generated soil, grass, stone, and plant seeds each run
- **Enemy AI — Gardener**: Patrols the surface, chases when it spots you, repairs the garden, and plants new seeds
- **Enemy AI — Snakes**: Slither through underground soil (pass through soil, blocked by stone), growing in number over time
- **Minimap**: Live top-down overview showing your position, the gardener, and all snakes
- **Particle Effects**: Block-break debris particles for soil, grass, stone, and plants
- **Drifting Clouds**: Animated sky with fluffy clouds above ground
- **Animated Menus**: Scrolling background on the home, instructions, and settings screens
- **Playful Buttons**: Color-coded pill buttons with hover animations and drop shadows
- **Settings Panel**: Adjustable volume sliders, Sound FX toggle, and rebindable controls

---

## Controls

### Menu Navigation
| Input | Action |
|-------|--------|
| **Mouse** | Click buttons to navigate |
| **ESC** | Return to previous screen / Pause |
| **F11** | Toggle fullscreen |

### Gameplay (defaults — rebindable in Settings)
| Input | Action |
|-------|--------|
| **A** | Move left |
| **D** | Move right |
| **W / SPACE** | Jump |
| **Left Click** | Dig the block under the cursor (up to 4 blocks away) |
| **ESC** | Pause |

> Stone blocks cannot be dug. Seeds require holding for a moment to destroy.

---

## Enemies

### 🌿 Gardener
- Patrols the grass surface and wanders randomly
- Spots you if you're at the same vertical level and chases at higher speed
- Plants new seeds while wandering
- Repairs holes in the grass as it walks
- Climbs back to the surface if it falls underground

### 🐍 Snakes
- Spawn underground and slither in random directions
- Pass through soil freely but are blocked by stone
- More snakes spawn over time (every ~10 seconds)
- Contact with any segment ends the run instantly

---

## Win / Lose Conditions

| Condition | Result |
|-----------|--------|
| Destroy **10 seeds** | **WIN** |
| Gardener touches you | **CAUGHT** — Game Over |
| Snake touches you | **BITTEN** — Game Over |
| Fall below the world | **FELL OUT** — Game Over |

Your survival time is displayed on each end screen.

---

## Settings

Open **Settings** from the main menu or pause screen.

| Setting | Type | Description |
|---------|------|-------------|
| Master Volume | Slider | Overall game volume (0–100%) |
| Music Volume | Slider | Music volume (0–100%) |
| Sound FX | Toggle | Enable / disable sound effects |
| Move Left | Keybind | Default: **A** |
| Move Right | Keybind | Default: **D** |
| Jump | Keybind | Default: **W** |
| Dig (hold) | Keybind | Placeholder (actual dig is mouse click) |

> Click **SAVE** to apply keybind changes. Click **BACK** to discard.

---

## Texture System

Place PNG files in `textures/` to override any block appearance.

| File | Block |
|------|-------|
| `soil.png` | Underground soil |
| `soil2.png`, `soil3.png`, … | Soil variants (auto-loaded) |
| `grass.png` | Surface grass |
| `plant.png` | Seeds / plants |
| `stone.png` | Unbreakable stone |
| `player.png` | Mole (player) |
| `gardener.png` | Gardener enemy |
| `snake_head.png` | Snake head segment |
| `snake_tail.png` | Snake tail segment |
| `snake_body1.png`, `snake_body2.png`, … | Snake body variants (auto-loaded) |
| `sky.png` | Sky fallback |

All textures are scaled to 40×40 pixels. Missing files fall back to colored shapes.

To generate placeholder textures:
```bash
python generate_textures.py
```

---

## File Structure

```
game/
├── main.py                 # All game code
├── generate_textures.py    # Generates placeholder textures
├── textures/               # Block & character textures
│   ├── soil.png / soil2.png / soil3.png / soil4.png
│   ├── grass.png
│   ├── plant.png
│   ├── stone.png
│   ├── player.png
│   ├── gardener.png
│   ├── snake_head.png
│   ├── snake_tail.png
│   └── snake_body1.png … snake_body4.png
└── addinfo/
    └── bg_image.png        # Animated menu background
```

---

## Running the Game

```bash
pip install pygame
python main.py
```

Requires **Python 3.10+** and **pygame 2.x**.

---

Good luck escaping the garden! 🐭