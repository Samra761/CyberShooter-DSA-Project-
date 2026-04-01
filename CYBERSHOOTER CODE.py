# Added comments by using AI for user's understanding - Hope it helps
# CyberShooter - DSA edition 

import pygame
import random
import sys
import os
import math

# ---------- DSA structures (doubly-linked list, Stack, Queue) ----------
class Node:
    def __init__(self, value):
        self.value = value
        self.prev = None
        self.next = None

class DoublyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self._len = 0

    def append(self, value):
        node = Node(value)
        if not self.head:
            self.head = self.tail = node
        else:
            node.prev = self.tail
            self.tail.next = node
            self.tail = node
        self._len += 1
        return node

    def popleft(self):
        if not self.head:
            return None
        node = self.head
        val = node.value
        if self.head == self.tail:
            self.head = self.tail = None
        else:
            self.head = node.next
            if self.head:
                self.head.prev = None
        self._len -= 1
        return val

    def pop(self):
        if not self.tail:
            return None
        node = self.tail
        val = node.value
        if self.head == self.tail:
            self.head = self.tail = None
        else:
            self.tail = node.prev
            if self.tail:
                self.tail.next = None
        self._len -= 1
        return val

    def remove_value(self, value):
        """Remove first node whose node.value is the same object (identity) as value."""
        cur = self.head
        while cur:
            if cur.value is value:
                if cur.prev:
                    cur.prev.next = cur.next
                else:
                    self.head = cur.next
                if cur.next:
                    cur.next.prev = cur.prev
                else:
                    self.tail = cur.prev
                self._len -= 1
                return True
            cur = cur.next
        return False

    def clear(self):
        self.head = None
        self.tail = None
        self._len = 0

    def __len__(self):
        return self._len

    def iter_nodes(self):
        cur = self.head
        while cur:
            yield cur
            cur = cur.next

    def iter_values(self):
        cur = self.head
        while cur:
            yield cur.value
            cur = cur.next

    def to_list(self):
        return [v for v in self.iter_values()]

# Stack (LIFO) using DLL
class Stack:
    def __init__(self):
        self._dll = DoublyLinkedList()

    def push(self, value):
        return self._dll.append(value)

    def pop(self):
        return self._dll.pop()

    def remove(self, value):
        return self._dll.remove_value(value)

    def clear(self):
        self._dll.clear()

    def __iter__(self):
        return self._dll.iter_values()

    def __len__(self):
        return len(self._dll)

    def to_list(self):
        return self._dll.to_list()

# Queue (FIFO) using DLL
class Queue:
    def __init__(self):
        self._dll = DoublyLinkedList()

    def enqueue(self, value):
        return self._dll.append(value)

    def dequeue(self):
        return self._dll.popleft()

    def remove(self, value):
        return self._dll.remove_value(value)

    def clear(self):
        self._dll.clear()

    def __iter__(self):
        return self._dll.iter_values()

    def __len__(self):
        return len(self._dll)

    def to_list(self):
        return self._dll.to_list()

# ---------- Initialization ----------
pygame.init()
WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CyberShooter - EXTRA ORDINARY DSA Edition")

# Colors (Neon/Cyber Palette)
NEO_BLACK = (6, 8, 18)
NEO_WHITE = (200, 200, 255)
NEO_RED = (255, 60, 100)
NEO_GREEN = (0, 255, 120)
NEO_BLUE = (60, 180, 255)
NEO_YELLOW = (255, 255, 0)
NEO_PURPLE = (200, 60, 255)
NEO_GRAY = (80, 80, 100)

# Asteroid Colors (more earthy/rocky tones but with a cyber edge)
ASTEROID_GREY = (90, 95, 110)
ASTEROID_BROWN = (120, 80, 70)
ASTEROID_DARK = (50, 55, 65)
ASTEROID_CRACK = (30, 30, 40)

# Planet Colors (Base colors used for rotation logic) - RGB only
PLANET_COLORS = [
    (30, 80, 150),  # Blue
    (40, 120, 80),  # Green
    (150, 90, 30),  # Orange
    (80, 40, 120)   # Purple
]


# Fonts
font_big = pygame.font.SysFont("consolas", 64)
font_med = pygame.font.SysFont("consolas", 32)
font_small = pygame.font.SysFont("consolas", 24)
font_mono = pygame.font.SysFont("monospace", 18, bold=True) # New font for HUD detail

clock = pygame.time.Clock()
FPS = 60
GLOBAL_TICK = 0 # for dynamic effects

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets") # optional sounds directory

# ---------- Game variables ----------
player_size = 58
player = pygame.Rect(WIDTH // 2 - player_size//2, HEIGHT - 120, player_size, player_size)
player_speed = 7 # Increased speed for better feel

# using DSA:
bullets = Stack()           # bullets stack (LIFO) but supports arbitrary removal
bullet_speed = -16
SHOT_COOLDOWN = 10
bullet_cooldown = 0

enemies = Queue()           # queue (FIFO)
enemy_size = 48
spawn_timer = 0
SPAWN_RATE = 35 # lower -> more frequent

powerups = Queue()          # queue for powerups
powerup_size = 38
POWERUP_SPAWN_RATE = 800 # frames
powerup_timer = 0

explosions = Queue()        # queue for explosions, processed in order

score = 0
high_score = 0
HIGHSCORE_FILE = "highscore.txt"

lives = 3
double_fire = False
DOUBLE_FIRE_DURATION = FPS * 8
double_fire_timer = 0

# background stars and planets as DSA containers
stars = DoublyLinkedList()  # each node.value = [x, y, size, speed]
planets = Queue()           # each value = {'x','y','spd','scale', 'base_color', 'display_color', 'has_rings', 'rotation_offset', 'spots'}

# Visual effects
bullet_trails = DoublyLinkedList() # Stores {'x', 'y', 'color', 'radius', 'ttl'}
static_sparks = DoublyLinkedList() # Stores {'x', 'y', 'ttl', 'color'}

# Global Glow Surface (for hyper-glow effect)
GLOW_SURFACE = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
GLOW_SURFACE.set_colorkey((0,0,0)) 

# Track last planet color index to ensure no two adjacent planets are the same base color
last_planet_color_index = -1


# ---------- Safe sound loader (optional) ----------
def safe_load_sound(name):
    path = os.path.join(ASSETS_DIR, name)
    try:
        snd = pygame.mixer.Sound(path)
        return snd
    except Exception:
        return None

# try init mixer
try:
    pygame.mixer.init()
except Exception:
    pass

# sounds (optional - keep variables so user can add audios to assets/)
shoot_sound = safe_load_sound("shoot.wav")
explosion_sound = safe_load_sound("explosion.wav")
click_sound = safe_load_sound("click.wav")
powerup_sound = safe_load_sound("powerup.wav")

# ---------- Background Music ----------
try:
    pygame.mixer.music.load(os.path.join(ASSETS_DIR, "bg_music.wav"))
    pygame.mixer.music.set_volume(0.35)   # volume (0.0 - 1.0)
    pygame.mixer.music.play(-1)           # loop forever
except:
    pass

# ---------- Utility functions ----------
def load_highscore():
    global high_score
    try:
        if os.path.exists(HIGHSCORE_FILE):
            with open(HIGHSCORE_FILE, "r") as f:
                high_score = int(f.read().strip() or 0)
    except Exception:
        high_score = 0

def save_highscore():
    try:
        with open(HIGHSCORE_FILE, "w") as f:
            f.write(str(high_score))
    except Exception:
        pass

def reset_player():
    player.x = WIDTH // 2 - player_size//2
    player.y = HEIGHT - 120

def add_explosion(pos, color=NEO_RED, size=32):
    explosions.enqueue({"pos": pos, "r": 2, "max": size, "color": color})

def update_explosions():
    to_remove = []
    explosion_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for ex in list(explosions.to_list()):
        ex["r"] += 3
        alpha = max(0, 255 - int((ex["r"]/ex["max"])*255))
        r, g, b = ex["color"]
        color_with_alpha = (r, g, b, alpha)
        
        pygame.draw.circle(explosion_surface, color_with_alpha, ex["pos"], ex["r"], 1)
        pygame.draw.circle(explosion_surface, (255, 255, 255, alpha), ex["pos"], ex["r"]//4)
        
        if ex["r"] >= ex["max"]:
            to_remove.append(ex)
    
    screen.blit(explosion_surface, (0, 0))
    for ex in to_remove:
        explosions.remove(ex)

def add_trail(pos, color, radius, duration):
    bullet_trails.append({'x': pos[0], 'y': pos[1], 'color': color, 'radius': radius, 'ttl': duration})

def update_trails():
    to_remove = []
    
    for t in list(bullet_trails.to_list()):
        t['ttl'] -= 1
        alpha = int(255 * (t['ttl'] / 10))
        r, g, b = t['color']
        color_with_alpha = (r, g, b, alpha)
        
        prev_x = t['x'] + (t['ttl'] - 1) * 0.5 * random.uniform(-1, 1) 
        prev_y = t['y'] + (t['ttl'] - 1) * 0.5 
        
        pygame.draw.line(GLOW_SURFACE, color_with_alpha, (int(t['x']), int(t['y'])), (int(prev_x), int(prev_y)), t['radius'] * 2)
        
        if t['ttl'] <= 0:
            to_remove.append(t)
            
    for t in to_remove:
        bullet_trails.remove_value(t) 

def add_static_spark(x, y, color):
    static_sparks.append({'x': x, 'y': y, 'ttl': random.randint(3, 8), 'color': color})

def update_static_sparks():
    to_remove = []
    
    if GLOBAL_TICK % 3 == 0:
        for _ in range(3):
            add_static_spark(random.randint(0, WIDTH), random.randint(0, HEIGHT), NEO_GRAY)
    
    for s in list(static_sparks.to_list()):
        s['ttl'] -= 1
        
        alpha = int(255 * (s['ttl'] / 8))
        r, g, b = s['color']
        color_with_alpha = (r, g, b, alpha)
        
        GLOW_SURFACE.set_at((s['x'], s['y']), color_with_alpha)
        
        if s['ttl'] <= 0:
            to_remove.append(s)
            
    for s in to_remove:
        static_sparks.remove_value(s)


# ---------- Background (DSA managed) ----------
def spawn_stars(n=150):
    stars.clear()
    for _ in range(n):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        size = random.randint(1, 3)
        spd = 1 + size * 0.4
        stars.append([x, y, size, spd])

def spawn_planets():
    global last_planet_color_index
    planets.clear()
    
    num_planets = random.randint(2, 4)
    
    for i in range(num_planets):
        scale = random.uniform(0.4, 2.0)
        has_rings = random.random() < 0.35
        
        # 1. Select a new base color, ensuring it's different from the last one
        available_colors_indices = [i for i in range(len(PLANET_COLORS)) if i != last_planet_color_index]
        
        if not available_colors_indices:
             # Fallback if only one color exists or logic error, just use a random one
            base_color_index = random.randint(0, len(PLANET_COLORS) - 1)
        else:
            base_color_index = random.choice(available_colors_indices)

        base_color = PLANET_COLORS[base_color_index]
        last_planet_color_index = base_color_index # Update index for tracking

        # Apply slight color variation for display color (RGB only)
        display_color = tuple(max(0, min(255, c + random.randint(-20, 20))) for c in base_color)
        
        # 2. Generate spots
        num_spots = random.randint(3, 6)
        spots = []
        planet_radius = 40 * scale
        for _ in range(num_spots):
            # Spot size relative to planet scale
            spot_r = random.uniform(3 * scale, 8 * scale)
            # Spot position relative to center (r, angle)
            spot_dist = random.uniform(0, planet_radius - spot_r) 
            spot_angle = random.uniform(0, math.pi * 2)
            spots.append({'r': spot_r, 'dist': spot_dist, 'angle': spot_angle})


        planets.enqueue({
            "x": random.randint(0, WIDTH),
            "y": random.randint(20, HEIGHT//2 - 50),
            "spd": random.uniform(0.1, 0.5),
            "scale": scale,
            "base_color": base_color,         # Store base color for recycling
            "display_color": display_color,   # Store actual color used for drawing
            "has_rings": has_rings,
            "rotation_offset": random.uniform(0, math.pi * 2),
            "spots": spots
        })
    
    # After initial spawn, set the index to the last one created
    if planets._dll.tail: # <--- CORRECTED LINE (Access DLL's tail)
        # Find the index of the base color of the last planet
        tail_base_color = planets._dll.tail.value['base_color']
        try:
            last_planet_color_index = PLANET_COLORS.index(tail_base_color)
        except ValueError:
            last_planet_color_index = -1
    else:
        last_planet_color_index = -1


def draw_background():
    screen.fill(NEO_BLACK)
    
    # 1. Neon Grid/Scanline Effect
    grid_color = (20, 30, 40)
    for y in range(0, HEIGHT, 50):
        pygame.draw.line(screen, grid_color, (0, y), (WIDTH, y), 1)
        
    for x in range(0, WIDTH, 50):
        pulse_factor = math.sin(GLOBAL_TICK * 0.05 + x * 0.01) * 3
        pygame.draw.line(screen, grid_color, (x + pulse_factor, 0), (x + pulse_factor, HEIGHT), 1)

    # 2. Stars (drawn with glow)
    for s in list(stars.to_list()):
        brightness = int(200 + 55 * math.sin(GLOBAL_TICK * 0.1 + s[0] * 0.01))
        star_color = (brightness, brightness, brightness)
        pygame.draw.circle(GLOW_SURFACE, star_color, (int(s[0]), int(s[1])), s[2])
        s[1] += s[3]
        if s[1] > HEIGHT:
            s[1] = -2
            s[0] = random.randint(0, WIDTH)

    # 3. Planets (Clean Interiors, Spots, and Stable Rings)
    global last_planet_color_index
    
    planets_to_remove = []
    
    for p in list(planets.to_list()):
        r = int(40 * p["scale"])
        color = p["display_color"] # RGB tuple
        center_x, center_y = int(p["x"]), int(p["y"])
        
        # Draw semi-transparent atmosphere/glow on GLOW_SURFACE
        s_g = pygame.Surface((r*2 + 20, r*2 + 20), pygame.SRCALPHA)
        # Use RGB for the base color, then add alpha (50)
        pygame.draw.circle(s_g, (color[0], color[1], color[2], 50), (r+10, r+10), r + 5)
        GLOW_SURFACE.blit(s_g, (center_x - r - 10, center_y - r - 10))
        
        # Draw the solid planet core (Uses RGB color)
        pygame.draw.circle(screen, color, (center_x, center_y), r)

        # Draw spots/craters
        spot_color = tuple(max(0, c - 40) for c in color) # Darker version of planet color (still RGB)
        planet_rotation = GLOBAL_TICK * 0.005 # Slow, steady rotation
        
        for spot in p['spots']:
            # Calculate spot position relative to the rotating planet center
            current_angle = spot['angle'] + planet_rotation
            spot_x = center_x + spot['dist'] * math.cos(current_angle)
            spot_y = center_y + spot['dist'] * math.sin(current_angle)
            
            # Only draw spots within the main planet radius
            if math.hypot(spot_x - center_x, spot_y - center_y) < r:
                pygame.draw.circle(screen, spot_color, (int(spot_x), int(spot_y)), int(spot['r']))

        # Draw glowing rings if present
        ring_outer_radius = 0
        if p["has_rings"]:
            # Ring color is the display color brightened (still RGB)
            ring_color = tuple(min(255, c + 100) for c in color)
            ring_thickness = int(r * 0.15)
            ring_outer_radius = r + random.randint(r//4, r//2)
            
            angle = p["rotation_offset"]
            scale_y = 0.4 # Fixed aspect ratio for stable elliptical ring
            
            ring_surf = pygame.Surface((ring_outer_radius*2 + 20, ring_outer_radius*2 + 20), pygame.SRCALPHA)
            ring_center = (ring_outer_radius + 10, ring_outer_radius + 10)
            
            # Outer ring band (Semi-transparent)
            pygame.draw.ellipse(ring_surf, (ring_color[0], ring_color[1], ring_color[2], 100), 
                                (ring_center[0] - ring_outer_radius, ring_center[1] - ring_outer_radius * scale_y, 
                                 ring_outer_radius * 2, ring_outer_radius * 2 * scale_y), ring_thickness + 2)
            
            # Inner ring band (More opaque)
            pygame.draw.ellipse(ring_surf, (ring_color[0], ring_color[1], ring_color[2], 200), 
                                (ring_center[0] - ring_outer_radius * 0.8, ring_center[1] - ring_outer_radius * 0.8 * scale_y, 
                                 ring_outer_radius * 1.6, ring_outer_radius * 1.6 * scale_y), ring_thickness)
            
            # Add subtle glow to the rings on GLOW_SURFACE
            pygame.draw.ellipse(GLOW_SURFACE, (ring_color[0], ring_color[1], ring_color[2], 80), 
                                (center_x - ring_outer_radius - 10, center_y - ring_outer_radius * scale_y - 10, 
                                 ring_outer_radius * 2 + 20, ring_outer_radius * 2 * scale_y + 20), ring_thickness + 6)

            screen.blit(ring_surf, (center_x - ring_outer_radius - 10, center_y - ring_outer_radius - 10))

        p["x"] -= p["spd"]
        removal_radius = max(r, ring_outer_radius)
        if p["x"] < -removal_radius - 200:
            planets_to_remove.append(p)
    
    # Respawn/Recycle Logic
    for p_removed in planets_to_remove:
        planets.remove(p_removed)
        
        # 1. Select a new base color index, ensuring it's different from the last one
        available_colors_indices = [i for i in range(len(PLANET_COLORS)) if i != last_planet_color_index]
        
        if not available_colors_indices:
            new_base_color_index = random.randint(0, len(PLANET_COLORS) - 1)
        else:
            new_base_color_index = random.choice(available_colors_indices)
            
        base_color = PLANET_COLORS[new_base_color_index]
        last_planet_color_index = new_base_color_index # Update index for tracking

        # Apply slight color variation for display color
        new_display_color = tuple(max(0, min(255, c + random.randint(-20, 20))) for c in base_color)
        
        # 2. Generate new spots
        scale = random.uniform(0.4, 2.0)
        num_spots = random.randint(3, 6)
        new_spots = []
        planet_radius = 40 * scale
        for _ in range(num_spots):
            spot_r = random.uniform(3 * scale, 8 * scale)
            spot_dist = random.uniform(0, planet_radius - spot_r) 
            spot_angle = random.uniform(0, math.pi * 2)
            new_spots.append({'r': spot_r, 'dist': spot_dist, 'angle': spot_angle})
            
        planets.enqueue({
            "x": WIDTH + random.randint(20, 200),
            "y": random.randint(40, HEIGHT//2),
            "spd": random.uniform(0.1, 0.5),
            "scale": scale,
            "base_color": base_color,
            "display_color": new_display_color,
            "has_rings": random.random() < 0.35,
            "rotation_offset": random.uniform(0, math.pi * 2),
            "spots": new_spots
        })
    
    # Ensure the 'last_planet_color_index' is correctly updated based on the rightmost planet
    if planets._dll.tail: # <--- CORRECTED LINE (Access DLL's tail)
        # Since we stored base_color, we can reliably update the index
        tail_base_color = planets._dll.tail.value['base_color']
        try:
            last_planet_color_index = PLANET_COLORS.index(tail_base_color)
        except ValueError:
            last_planet_color_index = -1
    else:
        last_planet_color_index = -1


# ---------- Spawning enemies and powerups (same logic) ----------
def spawn_enemy():
    t = random.choices(["small","medium","large"], weights=[70,22,8])[0]
    
    x = random.randint(20, WIDTH - enemy_size - 20)
    
    if t == "small":
        size_factor = random.uniform(0.8, 1.2)
        speed = random.randint(3,5)
        hp = 1
        color = ASTEROID_GREY
    elif t == "medium":
        size_factor = random.uniform(1.2, 1.6)
        speed = random.randint(2,4)
        hp = 2
        color = ASTEROID_BROWN
    else: # large
        size_factor = random.uniform(1.6, 2.2)
        speed = random.randint(1,2)
        hp = 4
        color = ASTEROID_DARK
        
    actual_size = int(enemy_size * size_factor)
    
    enemies.enqueue({"rect": pygame.Rect(x, -actual_size, actual_size, actual_size),
                    "speed": speed, "hp": hp, "color": color, "max_hp": hp,
                    "asteroid_shape_seed": random.randint(0, 10000)}) # Seed for irregular shape

def spawn_powerup():
    kind = random.choice(["life", "double"])
    x = random.randint(20, WIDTH - powerup_size - 20)
    powerups.enqueue({"rect": pygame.Rect(x, -powerup_size, powerup_size, powerup_size), "kind": kind})

# ---------- Drawing functions (Significantly Improved GUI) ----------

def draw_player():
    
    p = player
    c = p.centerx, p.centery
    
    distort_x = math.sin(GLOBAL_TICK * 0.2) * 2
    c_distorted = (c[0] + distort_x, c[1])

    # A. Cannons
    cannon_color = NEO_BLUE
    if double_fire:
        cannon_color = NEO_YELLOW
    cannon_offset = 12
    pygame.draw.rect(screen, NEO_WHITE, (c_distorted[0] - 22 - 3, p.y + cannon_offset, 6, 10), border_radius=1)
    pygame.draw.rect(screen, cannon_color, (c_distorted[0] - 22 - 3, p.y + cannon_offset, 6, 10), 1, border_radius=1)
    pygame.draw.rect(screen, NEO_WHITE, (c_distorted[0] + 22 - 3, p.y + cannon_offset, 6, 10), border_radius=1)
    pygame.draw.rect(screen, cannon_color, (c_distorted[0] + 22 - 3, p.y + cannon_offset, 6, 10), 1, border_radius=1)

    # B. Main Body (Stylized Rocket Core)
    core_points = [
        (c_distorted[0], p.y),
        (p.x + 15, p.y + 45),
        (p.x + 10, p.bottom - 16),
        (p.right - 10, p.bottom - 16),
        (p.right - 15, p.y + 45)
    ]
    pygame.draw.polygon(screen, NEO_BLUE, core_points, 2)
    pygame.draw.polygon(screen, (60, 100, 200), core_points)

    # C. Wings
    wing_points = [
        ((p.x, p.bottom - 10), (p.x + 10, p.bottom - 16), (c_distorted[0] - 18, p.y + 10), (c_distorted[0] - 28, p.y + 18)),
        ((p.right, p.bottom - 10), (p.right - 10, p.bottom - 16), (c_distorted[0] + 18, p.y + 10), (c_distorted[0] + 28, p.y + 18))
    ]
    
    for points in wing_points:
        pulse_y = math.sin(GLOBAL_TICK * 0.1) * 2
        shifted_points = [(pt[0], pt[1] + pulse_y) for pt in points]
        pygame.draw.polygon(screen, NEO_GRAY, shifted_points, 0)
        pygame.draw.polygon(screen, NEO_WHITE, shifted_points, 1)

    # D. Neon Thrusters
    thrust_base_y = p.bottom - 10
    thrust_width = 8
    
    for thrust_x_factor in [-p.width//4, p.width//4]:
        thruster_x = c_distorted[0] + thrust_x_factor
        thruster_y = thrust_base_y
        thrust_h = 10 + 5 * math.sin(GLOBAL_TICK * 0.5)
        
        thrust_points = [
            (thruster_x - thrust_width, thruster_y), 
            (thruster_x + thrust_width, thruster_y), 
            (thruster_x, thruster_y + thrust_h)
        ]
        pygame.draw.polygon(screen, NEO_RED, thrust_points)
        
        glow_color = (NEO_RED[0], NEO_RED[1], NEO_RED[2], 120)
        pygame.draw.circle(GLOW_SURFACE, glow_color, (int(thruster_x), int(thruster_y)), 12)

    # E. Double Fire Effect
    if double_fire:
        pulse_alpha = int(50 + 205 * (math.sin(GLOBAL_TICK * 0.3)**2))
        outline_color = (pulse_alpha, pulse_alpha, 50)
        pygame.draw.polygon(screen, outline_color, core_points, 3) 
        yellow_glow = (NEO_YELLOW[0], NEO_YELLOW[1], NEO_YELLOW[2], 80)
        pygame.draw.circle(GLOW_SURFACE, yellow_glow, (int(c_distorted[0]), int(c_distorted[1])), 40)

def draw_enemy(e):
    r_rect = e["rect"]
    base_color = e["color"]
    
    # Generate irregular asteroid shape using the seed
    random.seed(e["asteroid_shape_seed"])
    
    num_points = random.randint(8, 12)
    points = []
    
    base_radius = r_rect.width * 0.4
    
    rotation_offset = GLOBAL_TICK * 0.05
    
    for i in range(num_points):
        angle = (math.pi * 2 / num_points) * i + rotation_offset
        radius_offset = random.uniform(base_radius * 0.8, base_radius * 1.2) 
        x = r_rect.centerx + radius_offset * math.cos(angle)
        y = r_rect.centery + radius_offset * math.sin(angle)
        points.append((x, y))
    
    random.seed()

    if not points: return

    # 1. Draw asteroid body (Solid Fill)
    pygame.draw.polygon(screen, base_color, [(int(p[0]), int(p[1])) for p in points])
    
    # 2. Add darker shadow/texture (Cracks and Outline)
    pygame.draw.polygon(screen, ASTEROID_CRACK, [(int(p[0]), int(p[1])) for p in points], 1)
    
    # 3. Add internal cracks
    num_cracks = random.randint(2, 4)
    for _ in range(num_cracks):
        start_point_index = random.randint(0, num_points - 1)
        end_point_index = random.randint(0, num_points - 1)
        
        start_p = points[start_point_index]
        end_p = points[end_point_index]
        
        pygame.draw.line(screen, ASTEROID_CRACK, (int(start_p[0]), int(start_p[1])), (int(end_p[0]), int(end_p[1])), 1)
    
    # 4. HP Bar (if > 1)
    if e.get("max_hp", 1) > 1:
        hp_ratio = e["hp"] / e["max_hp"]
        hp_w = int(r_rect.width * hp_ratio)
        bar_color = NEO_GREEN if hp_ratio > 0.5 else NEO_YELLOW
        
        glitch_x_offset = random.randint(-1, 1)
        
        pygame.draw.rect(screen, NEO_GRAY, (r_rect.x + glitch_x_offset, r_rect.y - 12, r_rect.width, 5))
        pygame.draw.rect(screen, bar_color, (r_rect.x + glitch_x_offset, r_rect.y - 12, hp_w, 5))
        
        pygame.draw.rect(GLOW_SURFACE, (bar_color[0], bar_color[1], bar_color[2], 100), (r_rect.x, r_rect.y - 12, hp_w, 5), border_radius=1)


def draw_bullet(b):
    trail_color = NEO_GREEN if not double_fire else NEO_YELLOW
    add_trail(b.center, trail_color, 2, 5)
    
    head_color = NEO_WHITE if not double_fire else NEO_YELLOW
    
    pygame.draw.line(screen, trail_color, (b.centerx, b.y + b.height), (b.centerx, b.y), 4)
    pygame.draw.rect(screen, head_color, (b.x, b.y, b.width, b.height), border_radius=2)
    
    pygame.draw.circle(GLOW_SURFACE, (trail_color[0], trail_color[1], trail_color[2], 150), b.center, 5)

def draw_powerup(p):
    r = p["rect"]
    
    if p["kind"] == "life":
        col = NEO_GREEN
        symbol = "♥" 
    else:
        col = NEO_YELLOW
        symbol = "⚡"
    
    pulse = int(2 + 2 * math.sin(GLOBAL_TICK * 0.2))
    
    glow_color = (col[0], col[1], col[2], 100)
    pygame.draw.rect(GLOW_SURFACE, glow_color, r.inflate(10, 10), border_radius=8)

    pygame.draw.rect(screen, col, r, border_radius=6)
    pygame.draw.rect(screen, NEO_WHITE, r.inflate(pulse, pulse), 2, border_radius=6)
    
    lbl = font_small.render(symbol, True, NEO_BLACK)
    screen.blit(lbl, (r.x + r.width//2 - lbl.get_width()//2, r.y + r.height//2 - lbl.get_height()//2))

def show_hud():
    
    score_surf = font_mono.render(f"[SCORE]{score:06d}", True, NEO_GREEN)
    hs_surf = font_mono.render(f"[H-SCORE]{high_score:06d}", True, NEO_WHITE)
    lives_surf = font_mono.render(f"[SYSTEM-HP]{lives}", True, NEO_RED)
    
    box_padding = 8
    
    corner_size = 15
    line_thickness = 2
    
    # Top Left Corner (NEO_GREEN for primary status)
    pygame.draw.line(screen, NEO_GREEN, (box_padding, box_padding + corner_size), (box_padding, box_padding), line_thickness)
    pygame.draw.line(screen, NEO_GREEN, (box_padding, box_padding), (box_padding + corner_size, box_padding), line_thickness)
    
    # Bottom Left Corner
    box_h = lives_surf.get_height() * 3 + 20
    pygame.draw.line(screen, NEO_RED, (box_padding, box_padding + box_h), (box_padding + corner_size, box_padding + box_h), line_thickness)
    pygame.draw.line(screen, NEO_RED, (box_padding, box_padding + box_h - corner_size), (box_padding, box_padding + box_h), line_thickness)
    
    # 2. Blit Text
    y_offset = box_padding + 6
    screen.blit(score_surf, (box_padding + 10, y_offset))
    y_offset += score_surf.get_height() + 4
    screen.blit(hs_surf, (box_padding + 10, y_offset))
    y_offset += hs_surf.get_height() + 4
    screen.blit(lives_surf, (box_padding + 10, y_offset))
    
    # 3. Double Fire Status (Right Side)
    if double_fire:
        df_text = f"[POWER-UP] D-FIRE: {int(double_fire_timer/FPS) + 1:02d}s"
        df_surf = font_mono.render(df_text, True, NEO_YELLOW)
        
        df_x = WIDTH - df_surf.get_width() - box_padding
        df_y = box_padding
        
        glitch_shift = random.choice([0, 0, 0, 1, -1]) 
        
        screen.blit(df_surf, (df_x + glitch_shift, df_y))
        
        pygame.draw.line(screen, NEO_YELLOW, (df_x, df_y), (df_x, df_y + corner_size), line_thickness)
        pygame.draw.line(screen, NEO_YELLOW, (df_x + df_surf.get_width(), df_y), (df_x + df_surf.get_width() - corner_size, df_y), line_thickness)

def apply_glow_and_static():
    
    # Blit glow surface multiple times for blur effect
    GLOW_SURFACE.set_alpha(30)
    screen.blit(GLOW_SURFACE, (1, 1))
    screen.blit(GLOW_SURFACE, (-1, -1))
    
    GLOW_SURFACE.set_alpha(150)
    screen.blit(GLOW_SURFACE, (0, 0))

    GLOW_SURFACE.fill((0, 0, 0, 0))

    # Apply a light noise/static overlay
    static_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    
    if GLOBAL_TICK % 4 == 0:
        flicker_y = random.randint(0, HEIGHT)
        flicker_h = random.randint(1, 3)
        flicker_a = random.randint(10, 30)
        pygame.draw.rect(static_overlay, (200, 200, 255, flicker_a), (0, flicker_y, WIDTH, flicker_h))
        
    screen.blit(static_overlay, (0, 0))


# ---------- Intro / Menu UI ----------
def draw_button(rect, text, hover=False):
    clr = NEO_BLUE if hover else NEO_GRAY
    text_clr = NEO_WHITE if hover else NEO_BLACK
    
    pygame.draw.rect(screen, clr, rect, border_radius=8)
    pygame.draw.rect(screen, NEO_WHITE, rect, 2, border_radius=8)
    
    if hover:
        pygame.draw.rect(GLOW_SURFACE, (NEO_BLUE[0], NEO_BLUE[1], NEO_BLUE[2], 100), rect.inflate(10, 10), border_radius=10)
    
    t = font_med.render(text, True, text_clr)
    screen.blit(t, (rect.x + rect.width//2 - t.get_width()//2, rect.y + rect.height//2 - t.get_height()//2))

def intro_screen():
    global GLOBAL_TICK
    reset_player()
    load_highscore()
    spawn_planets()
    spawn_stars()
    while True:
        GLOBAL_TICK += 1
        
        draw_background()
        GLOW_SURFACE.fill((0, 0, 0, 0))
        update_static_sparks()
        
        title = font_big.render("CYBERSHOOTER", True, NEO_GREEN)
        subtitle = font_med.render("DSA EDITION", True, NEO_WHITE)
        
        title_glow_color = (0, 150, 80, 150)
        pygame.draw.rect(GLOW_SURFACE, title_glow_color, title.get_rect(topleft=(WIDTH//2 - title.get_width()//2 - 5, 70 - 5)).inflate(10, 10), border_radius=5)
        
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 70))
        screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 130))

        start_rect = pygame.Rect(WIDTH//2 - 120, HEIGHT//2 - 10, 240, 60)
        quit_rect = pygame.Rect(WIDTH//2 - 120, HEIGHT//2 + 80, 240, 60)
        
        mx,my = pygame.mouse.get_pos()
        draw_button(start_rect, "START GAME", start_rect.collidepoint((mx,my)))
        draw_button(quit_rect, "QUIT", quit_rect.collidepoint((mx,my)))

        hint = font_small.render("P=Pause | <-> to Move | SPACE to Shoot", True, NEO_GRAY)
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 60))

        apply_glow_and_static()

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if start_rect.collidepoint(event.pos):
                    try:
                        if click_sound: click_sound.play()
                    except: pass
                    return True
                if quit_rect.collidepoint(event.pos):
                    try:
                        if click_sound: click_sound.play()
                    except: pass
                    return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    try:
                        if click_sound: click_sound.play()
                    except: pass
                    return True
                if event.key == pygame.K_ESCAPE:
                    return False
        clock.tick(FPS)

# ---------- Main game loop ----------
def game_loop():
    global bullet_cooldown, spawn_timer, powerup_timer, GLOBAL_TICK
    global score, high_score, lives, double_fire, double_fire_timer

    bullets.clear()
    enemies.clear()
    powerups.clear()
    explosions.clear()
    bullet_trails.clear()
    static_sparks.clear()
    
    spawn_timer = 0
    powerup_timer = 0
    bullet_cooldown = 0
    score = 0
    lives = 3
    double_fire = False
    double_fire_timer = 0
    reset_player()

    running = True
    paused = False

    while running:
        GLOBAL_TICK += 1
        
        draw_background()
        GLOW_SURFACE.fill((0, 0, 0, 0))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                if event.key == pygame.K_ESCAPE:
                    return False

        if paused:
            pause_surf = font_big.render("PAUSED", True, NEO_YELLOW)
            resume_surf = font_med.render("(P to resume)", True, NEO_WHITE)
            
            glitch_x = random.randint(-2, 2)
            screen.blit(pause_surf, (WIDTH//2 - pause_surf.get_width()//2 + glitch_x, HEIGHT//2 - 50))
            screen.blit(resume_surf, (WIDTH//2 - resume_surf.get_width()//2, HEIGHT//2 + 10))
            
            glow_alpha = int(100 + 100 * math.sin(GLOBAL_TICK * 0.1))
            pygame.draw.circle(GLOW_SURFACE, (NEO_YELLOW[0], NEO_YELLOW[1], NEO_YELLOW[2], glow_alpha), (WIDTH//2, HEIGHT//2), 50, 5)
            
            apply_glow_and_static()
            pygame.display.flip()
            clock.tick(FPS)
            continue

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.left > 0:
            player.x -= player_speed
        if keys[pygame.K_RIGHT] and player.right < WIDTH:
            player.x += player_speed

        if bullet_cooldown > 0:
            bullet_cooldown -= 1
        if keys[pygame.K_SPACE] and bullet_cooldown <= 0:
            if double_fire:
                bullets.push(pygame.Rect(player.centerx - 20, player.y + 6, 8, 18))
                bullets.push(pygame.Rect(player.centerx + 12, player.y + 6, 8, 18))
            else:
                bullets.push(pygame.Rect(player.centerx - 4, player.y + 6, 8, 18))
            
            bullet_cooldown = SHOT_COOLDOWN
            try:
                if shoot_sound: shoot_sound.play()
            except: pass

        # move bullets and remove OOB
        bullets_to_remove = []
        for b in list(bullets.to_list()):
            b.y += bullet_speed
            if b.bottom < -10:
                bullets_to_remove.append(b)
        for b in bullets_to_remove:
            bullets.remove(b)

        # spawn enemies
        spawn_timer += 1
        if spawn_timer >= SPAWN_RATE:
            spawn_enemy()
            spawn_timer = 0

        # move enemies and remove off-screen
        enemies_to_remove = []
        for e in list(enemies.to_list()):
            e["rect"].y += e["speed"]
            if e["rect"].top > HEIGHT + 30:
                enemies_to_remove.append(e)
        for e in enemies_to_remove:
            enemies.remove(e)

        # spawn powerups
        powerup_timer += 1
        if powerup_timer >= POWERUP_SPAWN_RATE:
            spawn_powerup()
            powerup_timer = 0

        # move powerups and remove if off-screen
        pwr_to_remove = []
        for p in list(powerups.to_list()):
            p["rect"].y += 2
            if p["rect"].top > HEIGHT + 20:
                pwr_to_remove.append(p)
        for p in pwr_to_remove:
            powerups.remove(p)

        # collisions: bullets vs enemies
        enemy_snapshot = list(enemies.to_list())
        for e in enemy_snapshot:
            bullet_snapshot = list(bullets.to_list())
            for b in bullet_snapshot:
                if e["rect"].colliderect(b):
                    bullets.remove(b)
                    e["hp"] -= 1
                    
                    impact_pos = (b.centerx, b.y)
                    add_explosion(impact_pos, color=e["color"], size=10)
                    
                    if e["hp"] <= 0:
                        add_explosion(e["rect"].center, color=e["color"], size=36)
                        enemies_to_remove.append(e)
                        score += 10
                        if score > high_score:
                            high_score = score
                        try:
                            if explosion_sound: explosion_sound.play()
                        except: pass
                    break
        
        for e in enemies_to_remove:
            enemies.remove(e)

        # collisions: player vs enemies (damage)
        enemies_to_remove = []
        for e in list(enemies.to_list()):
            if player.colliderect(e["rect"]):
                add_explosion(player.center, color=NEO_RED, size=50)
                add_explosion(e["rect"].center, color=e["color"], size=40)
                try:
                    if explosion_sound: explosion_sound.play()
                except: pass
                
                lives -= 1
                double_fire = False
                reset_player()
                enemies_to_remove.append(e)
                if lives <= 0:
                    save_highscore()
                    return True
        
        for e in enemies_to_remove:
            enemies.remove(e)
            
        # collisions: player vs powerups
        pwr_to_remove = []
        for p in list(powerups.to_list()):
            if player.colliderect(p["rect"]):
                if p["kind"] == "life":
                    lives = min(5, lives + 1)
                elif p["kind"] == "double":
                    double_fire = True
                    double_fire_timer = DOUBLE_FIRE_DURATION
                pwr_to_remove.append(p)
                try:
                    if powerup_sound: powerup_sound.play()
                except: pass

        for p in pwr_to_remove:
            powerups.remove(p)

        # powerup timer logic
        if double_fire:
            double_fire_timer -= 1
            if double_fire_timer <= 0:
                double_fire = False
                double_fire_timer = 0
            
        # --- Drawing ---
        
        for p in list(powerups.to_list()):
            draw_powerup(p)
        
        for b in list(bullets.to_list()):
            draw_bullet(b)
        
        for e in list(enemies.to_list()):
            draw_enemy(e)
        
        draw_player()
        
        update_trails()
        update_static_sparks()
        update_explosions()

        show_hud()
        
        apply_glow_and_static()

        pygame.display.flip()
        clock.tick(FPS)
    
    return True

# ---------- Game Over Screen (Enhanced and Fixed) ----------
def game_over_screen():
    global score, high_score, GLOBAL_TICK
    
    if score > high_score:
        high_score = score
        save_highscore()
    
    explosions.clear()
    bullet_trails.clear()
    static_sparks.clear()
    
    while True:
        GLOBAL_TICK += 1
        
        draw_background()
        GLOW_SURFACE.fill((0, 0, 0, 0))
        update_static_sparks()
        
        go_text = font_big.render("GAME OVER", True, NEO_RED)
        go_rect = go_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 100))
        
        final_score_text = font_med.render(f"FINAL SCORE: {score}", True, NEO_GREEN)
        hs_text = font_small.render(f"HIGH SCORE: {high_score}", True, NEO_YELLOW)
        
        # Ensure alpha is clamped 
        flicker_alpha = int(100 + 155 * math.sin(GLOBAL_TICK * 0.3))
        clamped_alpha = max(0, min(255, flicker_alpha)) 
        
        flicker_color = (NEO_RED[0], NEO_RED[1], NEO_RED[2], clamped_alpha)
        
        pygame.draw.rect(GLOW_SURFACE, flicker_color, go_rect.inflate(10, 10), border_radius=5)
        
        glitch_x = random.randint(-4, 4) if GLOBAL_TICK % 10 < 3 else 0
        screen.blit(go_text, (go_rect.x + glitch_x, go_rect.y))
        
        screen.blit(final_score_text, (WIDTH//2 - final_score_text.get_width()//2, HEIGHT//2))
        screen.blit(hs_text, (WIDTH//2 - hs_text.get_width()//2, HEIGHT//2 + 50))

        restart_rect = pygame.Rect(WIDTH//2 - 120, HEIGHT//2 + 120, 240, 50)
        quit_rect = pygame.Rect(WIDTH//2 - 120, HEIGHT//2 + 190, 240, 50)
        
        mx,my = pygame.mouse.get_pos()
        draw_button(restart_rect, "RESTART", restart_rect.collidepoint((mx,my)))
        draw_button(quit_rect, "QUIT", quit_rect.collidepoint((mx,my)))

        apply_glow_and_static()

        pygame.display.flip()
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if restart_rect.collidepoint(event.pos):
                    try:
                        if click_sound: click_sound.play()
                    except: pass
                    return True
                if quit_rect.collidepoint(event.pos):
                    try:
                        if click_sound: click_sound.play()
                    except: pass
                    return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    try:
                        if click_sound: click_sound.play()
                    except: pass
                    return True
                if event.key == pygame.K_ESCAPE:
                    return False

# ---------- Main Execution Block ----------
def main():
    keep_running = True
    while keep_running:
        if intro_screen():
            if game_loop():
                if not game_over_screen():
                    keep_running = False
            else:
                keep_running = False
        else:
            keep_running = False

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
