
# CyberShooter — DSA Edition

> *"When data meets design — code becomes a game."*

A neon-themed 2D space shooter built entirely in **Python + Pygame**, where every moving object in the game — bullets, enemies, explosions, planets — is managed by **custom-built Data Structures** coded from scratch. No Python `deque`, no built-in collections for game state. Just raw DSA.

Built as a DSA course project @ **NUST** | Semester 3

---

## Preview

> *Shoot. Survive. Score.*

A cyberpunk arcade experience — neon glow effects, rotating asteroid fields, procedurally generated planets with rings, and a double-fire power-up system. All running on a Stack and a Queue.

---

## Controls

| Key | Action |
|-----|--------|
| `←` / `→` | Move spaceship |
| `SPACE` | Shoot bullets |
| `P` | Pause / Resume |
| `ESC` | Quit to menu |

---

## Installation

**Requirements:** Python 3.8+

```bash
pip install pygame
python cybershooter.py
```

### Optional Sound Effects
Create an `assets/` folder in the same directory and add:
```
assets/
├── shoot.wav
├── explosion.wav
├── powerup.wav
├── click.wav
└── bg_music.wav
```
The game runs perfectly fine without them.

---

## DSA Implementation

This is the core of the project. Every structure is built from scratch using a **Doubly Linked List** as the backbone — no Python built-ins used for game state management.

### `DoublyLinkedList` — the foundation
All other structures are built on top of this. Supports:
- O(1) append to tail
- O(1) removal from head or tail
- O(n) identity-based arbitrary node removal
- Forward iteration via `iter_values()`

### `Stack` (LIFO) — wraps the DLL
```
Used for: Player bullets
```
Each bullet fired is pushed onto the Stack. When a bullet exits the screen or hits an enemy, it is removed in-place. LIFO order naturally matches how the most recently fired bullet is the first one to go off screen.

### `Queue` (FIFO) — wraps the DLL
```
Used for: Enemies, Power-ups, Explosions, Background Planets
```
Enemies and power-ups are enqueued at spawn time and dequeued/removed on collision or exit. FIFO order ensures enemies are processed in the order they appeared — fair, predictable, and correct.

### `DoublyLinkedList` (direct)
```
Used for: Stars, Bullet trails, Static spark effects
```
Direct use allows efficient mid-list removal of visual effect nodes without any index shifting, keeping the render loop fast.

---

## Features

- **Custom DSA from scratch** — Stack, Queue, and DLL, zero built-in collections for game state
- **3 asteroid types** — small, medium, large with individual HP bars and irregular procedural shapes
- **Neon visual theme** — scanline grid, glow surfaces, CRT flicker, and static spark effects
- **Procedural planets** — rotating spots, elliptical ring systems, color variation per spawn
- **Double-fire power-up** — 8-second countdown timer with yellow glow effect
- **Persistent high score** — saved to `highscore.txt` across sessions
- **Pause screen, game over screen, main menu** — full game flow
- **Optional audio** — background music + sound effects via `assets/` folder

---

## Game Architecture

The main game loop runs at 60 FPS and continuously updates all DSA containers each frame:

```
User Input
    ↓
Update Player Position
    ↓
Generate Bullets (pushed to Stack)
    ↓
Spawn Enemies (enqueued to Queue)
    ↓
Detect Collisions (O(n×m) bullet × enemy check)
    ↓
Update Score
    ↓
Redraw Screen
```

Collision detection uses **bounding box checks** instead of pixel-perfect detection — a deliberate algorithmic choice to keep per-frame cost manageable at O(n) for movement updates and O(n×m) for collision pairs.

---

## Project Structure

```
CyberShooter-DSA/
├── cybershooter.py       # All DSA structures + complete game logic
├── highscore.txt         # Auto-generated on first run
├── docs/
│   └── presentation.pdf  # Project presentation slides
├── assets                # Optional for sound effects
└── README.md
```

---

## A Note on AI-Assisted Development

This project was built with the help of **AI tools** during development — used as a coding assistant for debugging, visual polish, and resolving tricky DSA edge cases like the `Queue` tail access bug.

The core idea, architecture, DSA design decisions, and game logic were conceived and driven by us. AI served as a smart rubber duck — it didn't build the game, it helped us build it better.

> Using AI as a tool, not a shortcut — that's the move.

---

## Team

| Name | Role |
|------|------|
| **Samra Mehmood** | Project lead, core DSA implementation, game logic, visual design |
| **Abdullah Khan** | Documentation, sound integration |

**Department of Electrical Engineering**  
NUST | Semester 3 | DSA Course Project
