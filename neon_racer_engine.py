import pygame
import math
import random

# --- CONFIGURATION ---
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors (Cyberpunk Palette)
BLACK = (5, 5, 15)
NEON_PINK = (255, 20, 147)
NEON_CYAN = (0, 255, 255)
NEON_PURPLE = (138, 43, 226)
MAGENTA = (255, 0, 255)
GRID_COLOR_1 = (60, 0, 60)
GRID_COLOR_2 = (40, 0, 40)
HORIZON_Y = HEIGHT // 2

# --- CLASSES ---

class Player:
    def __init__(self):
        self.width = 60
        self.height = 40
        self.x = WIDTH // 2
        self.y = HEIGHT - 100
        self.speed = 8

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > 200:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < WIDTH - 200 - self.width:
            self.x += self.speed

    def draw(self, surface):
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, (255, 255, 255), rect)
        pygame.draw.rect(surface, NEON_PINK, (self.x, self.y + 30, 15, 5))
        pygame.draw.rect(surface, NEON_PINK, (self.x + self.width - 15, self.y + 30, 15, 5))

class EnemyCar:
    def __init__(self, lane_x):
        self.lane_x = lane_x  # The fixed X coordinate on the road
        self.z = 0            # Depth (0 = horizon, 20 = player)
        self.speed = 0.2      # How fast it approaches
        self.width = 40
        self.height = 25
        self.color = random.choice([NEON_CYAN, NEON_PURPLE, MAGENTA])
        self.passed = False

    def update(self):
        self.z += self.speed
        return self.z >= 20

    def draw(self, surface, center_x):
        # Pseudo-3D scaling
        scale = (self.z / 20)
        draw_w = self.width * scale
        draw_h = self.height * scale
        
        # Calculate screen position
        # As z increases, y moves from HORIZON_Y towards the bottom
        y = HORIZON_Y + (self.z / 20) * (HEIGHT - HORIZON_Y)
        
        # Calculate X position based on the road width at that Y
        road_width_at_y = (y - HORIZON_Y) * 2.5
        # Map the lane_x (which is relative to road center) to screen X
        # lane_x is -100 to 100 (roughly)
        x = center_x + (self.lane_x * (road_width_at_y / 150)) - (draw_w / 2)
        
        # Draw the car
        rect = pygame.Rect(x, y - draw_h, draw_w, draw_h)
        pygame.draw.rect(surface, self.color, rect)
        # Taillights
        pygame.draw.rect(surface, (255, 50, 50), (x, y - draw_h + draw_h - 5, draw_w*0.2, draw_h*0.2))
        pygame.draw.rect(surface, (255, 50, 50), (x + draw_w*0.8, y - draw_h + draw_h - 5, draw_w*0.2, draw_h*0.2))

class PalmTree:
    def __init__(self, side):
        self.side = side # -1 for left, 1 for right
        self.z = 0
        self.speed = 0.15
        self.base_x_offset = 250 # Distance from center at horizon
        self.height = 80

    def update(self):
        self.z += self.speed
        return self.z >= 20

    def draw(self, surface, center_x):
        scale = (self.z / 20)
        tree_h = self.height * scale
        y = HORIZON_Y + (self.z / 20) * (HEIGHT - HORIZON_Y)
        
        road_width_at_y = (y - HORIZON_Y) * 2.5
        # Place trees on the outside of the road
        x = center_x + (self.side * (road_width_at_y / 2 + self.base_x_offset * scale))
        
        # Draw Trunk
        pygame.draw.rect(surface, (40, 20, 0), (x - 2*scale, y - tree_h, 4*scale, tree_h))
        # Draw Fronds (simple triangles/lines)
        pygame.draw.circle(surface, NEON_CYAN, (int(x), int(y - tree_h)), int(15*scale), 2)

class Road:
    def __init__(self):
        self.offset = 0
        self.speed = 15
        self.grid_size = 40 

    def update(self):
        self.offset = (self.offset + self.speed) % self.grid_size

    def draw(self, surface):
        pygame.draw.rect(surface, BLACK, (0, 0, WIDTH, HORIZON_Y))
        center_x = WIDTH // 2
        
        # 1. Draw Horizontal Lines
        for i in range(0, 20): 
            z = (i + self.offset / self.grid_size) % 20
            y = HORIZON_Y + (z / 20) * (HEIGHT - HORIZON_Y)
            road_width_at_y = (y - HORIZON_Y) * 2.5
            start_x = center_x - (road_width_at_y / 2)
            end_x = center_x + (road_width_at_y / 2)
            
            color = GRID_COLOR_1 if int(z + self.offset/self.grid_size) % 2 == 0 else GRID_COLOR_2
            
            # Glow
            glow_rect = pygame.Surface((end_x - start_x + 4, 3), pygame.SRCALPHA)
            glow_rect.fill((*color, 60))
            surface.blit(glow_rect, (start_x - 2, y - 1))
            pygame.draw.aaline(surface, color, (start_x, y), (end_x, y))

        # 2. Draw Vertical Lines
        for i in range(-5, 6):
            for j in range(20):
                z = (j + self.offset / self.grid_size) % 20
                y = HORIZON_Y + (z / 20) * (HEIGHT - HORIZON_Y)
                road_width_at_y = (y - HORIZON_Y) * 2.5
                line_x = center_x + (i * (road_width_at_y / 6))
                next_z = (j + 1 + self.offset / self.grid_size) % 20
                next_y = HORIZON_Y + (next_z / 20) * (HEIGHT - HORIZON_Y)
                color = GRID_COLOR_1 if int(j + self.offset/self.grid_size) % 2 == 0 else GRID_COLOR_2
                pygame.draw.aaline(surface, color, (line_x, y), (line_x, next_y))

# --- MAIN LOOP ---

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Neon Beetle: Cyberpunk Racer")
    clock = pygame.time.Clock()

    player = Player()
    road = Road()
    
    enemies = []
    trees = []
    
    spawn_timer = 0
    tree_timer = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        player.move(keys)

        # Spawning Logic
        spawn_timer += 1
        if spawn_timer > 40: # Spawn enemy car
            lane = random.choice([-80, -40, 0, 40, 80])
            enemies.append(EnemyCar(lane))
            spawn_timer = 0
            
        tree_timer += 1
        if tree_timer > 30: # Spawn palm tree
            side = random.choice([-1, 1])
            trees.append(PalmTree(side))
            tree_timer = 0

        # Update
        road.update()
        
        # Update Enemies
        for e in enemies[:]:
            if e.update():
                enemies.remove(e)
            # Collision Check (Rough)
            # We check if e.z is near the player's depth and X is near player's X
            if 18 < e.z < 20:
                # Calculate enemy's screen X
                # (Approximation for prototype)
                road_width = (HEIGHT - HORIZON_Y) * 2.5
                e_x_on_road = (WIDTH // 2) + (e.lane_x * (road_width / 150))
                if abs(e_x_on_road - player.x) < 50:
                    print("CRASH!") # For now just print

        # Update Trees
        for t in trees[:]:
            if t.update():
                trees.remove(t)

        # Draw
        screen.fill(BLACK)
        road.draw(screen)
        
        for t in trees:
            t.draw(screen, WIDTH // 2)
            
        for e in enemies:
            e.draw(screen, WIDTH // 2)

        player.draw(screen)

        # Scanline effect
        for y in range(0, HEIGHT, 4):
            scanline = pygame.Surface((WIDTH, 1), pygame.SRCALPHA)
            scanline.fill((0, 0, 0, 60))
            screen.blit(scanline, (0, y))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
