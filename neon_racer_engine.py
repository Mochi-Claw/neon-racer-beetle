import pygame
import math
import random
import json
import os

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

# Perspective Settings
MAX_Z = 25.0        # How "deep" the world is
HORIZON_WIDTH_FACTOR = 0.4 # Narrower horizon for more dramatic perspective

# --- CLASSES ---

class Player:
    def __init__(self, car_id=None):
        self.width = 60
        self.height = 40
        self.x = WIDTH // 2
        self.y = HEIGHT - 100
        
        # Default stats
        self.top_speed = 8
        self.acceleration = 0.1
        self.handling = 5
        self.health = 3
        self.current_speed = 0
        
        if car_id:
            self.load_car_stats(car_id)

    def load_car_stats(self, car_id):
        try:
            # Using relative path from the script's directory to be safe
            base_dir = os.path.dirname(os.path.abspath(__file__))
            with open(os.path.join(base_dir, "cars.json"), "r") as f:
                data = json.load(f)
                for car in data["cars"]:
                    if car["id"] == car_id:
                        self.top_speed = car["top_speed"]
                        self.acceleration = car["acceleration"]
                        self.handling = car["handling"]
                        self.health = car["health"]
                        break
        except Exception as e:
            print(f"Error loading car stats: {e}")

    def move(self, keys):
        # Handling affects how much we can change x
        move_amount = self.handling * 0.5
        
        if keys[pygame.K_LEFT] and self.x > 200:
            self.x -= move_amount
        if keys[pygame.K_RIGHT] and self.x << WIDTH WIDTH - 200 - self.width:
            self.x += move_amount

        # Constant acceleration towards top speed
        if self.current_speed << self self.top_speed:
            self.current_speed += self.acceleration
        elif self.current_speed > self.top_speed:
            self.current_speed -= self.acceleration * 2 # Decelerate faster if somehow over

    def take_damage(self, amount):
        self.health -= amount
        self.current_speed = 0 # Crash penalty!
        print(f"CRASH! Health: {self.health}")

    def draw(self, surface):
        # Draw car body
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, (255, 255, 255), rect)
        pygame.draw.rect(surface, NEON_PINK, (self.x, self.y + 30, 15, 5))
        pygame.draw.rect(surface, NEON_PINK, (self.x + self.width - 15, self.y + 30, 15, 5))
        
        # Simple Health Bar
        bar_width = 60
        bar_height = 5
        health_ratio = max(0, self.health / 6) # Assuming max 6 for scale
        pygame.draw.rect(surface, (50, 50, 50), (self.x, self.y - 10, bar_width, bar_height))
        pygame.draw.rect(surface, NEON_CYAN, (self.x, self.y - 10, bar_width * health_ratio, bar_height))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

def get_perspective_params(z):
    """Returns scaling and position factors based on depth z."""
    # Non-linear scaling: things stay small longer then grow.
    scale = math.pow(z / MAX_Z, 1.7) 
    return scale

class EnemyCar:
    def __init__(self, lane_x):
        self.lane_x = lane_x  # Relative to road center (-100 to 100)
        self.z = 0.1          # Depth (0 = horizon, 20 = player)
        self.speed = 0.15     
        self.width = 70       
        self.height = 45      
        self.color = random.choice([NEON_CYAN, NEON_PURPLE, MAGENTA])
        self.rect = None      

    def update(self):
        self.z += self.speed
        return self.z >= MAX_Z

    def draw(self, surface, center_x):
        scale = get_perspective_params(self.z)
        draw_w = self.width * scale
        draw_h = self.height * scale
        
        y = HORIZON_Y + (self.z / MAX_Z) * (HEIGHT - HORIZON_Y)
        
        # Road width at this Y
        current_horizon_width = WIDTH * HORIZON_WIDTH_FACTOR
        road_width_at_y = current_horizon_width + (y - HORIZON_Y) * (2.5 / HORIZON_WIDTH_FACTOR)
        
        x = center_x + (self.lane_x * (road_width_at_y / 150)) - (draw_w / 2)
        
        self.rect = pygame.Rect(x, y - draw_h, draw_w, draw_h)
        
        if self.rect.width > 1:
            pygame.draw.rect(surface, self.color, self.rect)
            pygame.draw.rect(surface, (255, 50, 50), (x, y - draw_h + draw_h - 5, draw_w*0.2, draw_h*0.2))
            pygame.draw.rect(surface, (255, 50, 50), (x + draw_w*0.8, y - draw_h + draw_h - 5, draw_w*0.2, draw_h*0.2))

class PalmTree:
    def __init__(self, side):
        self.side = side 
        self.z = 0.1
        self.speed = 0.15
        self.base_x_offset = 350 
        self.height = 100

    def update(self):
        self.z += self.speed
        return self.z >= MAX_Z

    def draw(self, surface, center_x):
        scale = get_perspective_params(self.z)
        tree_h = self.height * scale
        y = HORIZON_Y + (self.z / MAX_Z) * (HEIGHT - HORIZON_Y)
        
        current_horizon_width = WIDTH * HORIZON_WIDTH_FACTOR
        road_width_at_y = current_horizon_width + (y - HORIZON_Y) * (2.5 / HORIZON_WIDTH_FACTOR)
        
        x = center_x + (self.side * (road_width_at_y / 2 + self.base_x_offset * scale))
        
        pygame.draw.rect(surface, (40, 20, 0), (x - 2*scale, y - tree_h, 4*scale, tree_h))
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
        current_horizon_width = WIDTH * HORIZON_WIDTH_FACTOR
        
        # 1. Draw Horizontal Lines
        for i in range(0, 25): 
            z = (i + self.offset / self.grid_size) % 25
            y = HORIZON_Y + (z / MAX_Z) * (HEIGHT - HORIZON_Y)
            
            road_width_at_y = current_horizon_width + (y - HORIZON_Y) * (2.5 / HORIZON_WIDTH_FACTOR)
            start_x = center_x - (road_width_at_y / 2)
            end_x = center_x + (road_width_at_y / 2)
            
            color = GRID_COLOR_1 if int(z + self.offset/self.grid_size) % 2 == 0 else GRID_COLOR_2
            
            glow_rect = pygame.Surface((end_x - start_x + 4, 3), pygame.SRCALPHA)
            glow_rect.fill((*color, 60))
            surface.blit(glow_rect, (start_x - 2, y - 1))
            pygame.draw.aaline(surface, color, (start_x, y), (end_x, y))

        # 2. Draw Vertical Lines
        for i in range(-6, 7):
            for j in range(25):
                z = (j + self.offset / self.grid_size) % 25
                y = HORIZON_Y + (z / MAX_Z) * (HEIGHT - HORIZON_Y)
                
                road_width_at_y = current_horizon_width + (y - HORIZON_Y) * (2.5 / HORIZON_WIDTH_FACTOR)
                line_x = center_x + (i * (road_width_at_y / 7))
                
                next_z = (j + 1 + self.offset / self.grid_size) % 25
                next_y = HORIZON_Y + (next_z / MAX_Z) * (HEIGHT - HORIZON_Y)
                
                color = GRID_COLOR_1 if int(j + self.offset/self.grid_size) % 2 == 0 else GRID_COLOR_2
                pygame.draw.aaline(surface, color, (line_x, y), (line_x, next_y))

# --- MAIN LOOP ---

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Neon Beetle: Cyberpunk Racer")
    clock = pygame.time.Clock()

    # Load a default car for testing
    player = Player(car_id="speedster_01")
    road = Road()
    
    enemies = []
    trees = []
    
    spawn_timer = 0
    tree_timer = 0
    score = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        player.move(keys)

        spawn_timer += 1
        if spawn_timer > 60: 
            lane = random.choice([-80, -40, 0, 40, 80])
            enemies.append(EnemyCar(lane))
            spawn_timer = 0
            
        tree_timer += 1
        if tree_timer > 45:
            side = random.choice([-1, 1])
            trees.append(PalmTree(side))
            tree_timer = 0

        road.update()
        
        for e in enemies[:]:
            if e.update():
                enemies.remove(e)
                score += 10
            else:
                if e.rect and player.get_rect().colliderect(e.rect):
                    player.take_damage(1)
                    enemies.remove(e) # Remove enemy on crash to avoid double collision

        for t in trees[:]:
            if t.update():
                trees.remove(t)

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

        # Simple Score HUD
        font = pygame.font.SysFont("Arial", 24)
        score_text = font.render(f"Score: {score}", True, NEON_CYAN)
        screen.blit(score_text, (10, 10))

        if player.health <= 0:
            print("GAME OVER!")
            running = False

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
