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
GRID_COLOR_1 = (60, 0, 60)  # Dark Magenta
GRID_COLOR_2 = (40, 0, 40)  # Even Darker
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
        # Placeholder for the White A5 Beetle sprite
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, (255, 255, 255), rect)
        # Taillight glows
        pygame.draw.rect(surface, NEON_PINK, (self.x, self.y + 30, 15, 5))
        pygame.draw.rect(surface, NEON_PINK, (self.x + self.width - 15, self.y + 30, 15, 5))

class Road:
    def __init__(self):
        self.offset = 0
        self.speed = 15
        self.grid_size = 40 # Number of segments

    def update(self):
        self.offset = (self.offset + self.speed) % self.grid_size

    def draw(self, surface):
        # Draw the sky/background
        pygame.draw.rect(surface, (10, 0, 20), (0, 0, WIDTH, HORIZON_Y))
        
        # Draw the perspective grid
        # We draw lines that converge at the horizon center
        center_x = WIDTH // 2
        
        # 1. Draw Horizontal Lines (Z-axis movement)
        for i in range(0, 20): 
            z = (i + self.offset / self.grid_size) % 20
            y = HORIZON_Y + (z / 20) * (HEIGHT - HORIZON_Y)
            
            road_width_at_y = (y - HORIZON_Y) * 2.5
            start_x = center_x - (road_width_at_y / 2)
            end_x = center_x + (road_width_at_y / 2)
            
            color = GRID_COLOR_1 if int(z + self.offset/self.grid_size) % 2 == 0 else GRID_COLOR_2
            
            # Draw a "glow" line first (slightly thicker and transparent)
            glow_rect = pygame.Surface((end_x - start_x + 4, 3), pygame.SRCALPHA)
            glow_rect.fill((*color, 60))
            surface.blit(glow_rect, (start_x - 2, y - 1))
            
            # Draw the main anti-aliased line
            pygame.draw.aaline(surface, color, (start_x, y), (end_x, y))

        # 2. Draw Vertical Lines (X-axis convergence)
        for i in range(-5, 6):
            for j in range(20):
                z = (j + self.offset / self.grid_size) % 20
                y = HORIZON_Y + (z / 20) * (HEIGHT - HORIZON_Y)
                
                road_width_at_y = (y - HORIZON_Y) * 2.5
                line_x = center_x + (i * (road_width_at_y / 6))
                
                next_z = (j + 1 + self.offset / self.grid_size) % 20
                next_y = HORIZON_Y + (next_z / 20) * (HEIGHT - HORIZON_Y)
                
                color = GRID_COLOR_1 if int(j + self.offset/self.grid_size) % 2 == 0 else GRID_COLOR_2
                
                # Draw anti-aliased vertical segments
                pygame.draw.aaline(surface, color, (line_x, y), (line_x, next_y))

# --- MAIN LOOP ---

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Neon Beetle: Cyberpunk Racer")
    clock = pygame.time.Clock()

    player = Player()
    road = Road()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        player.move(keys)

        road.update()

        screen.fill(BLACK)
        
        # Draw the road first
        road.draw(screen)
        
        # Draw the player on top
        player.draw(screen)

        # Scanline effect
        for y in range(0, HEIGHT, 4):
            # Create a semi-transparent surface for scanlines
            scanline = pygame.Surface((WIDTH, 1), pygame.SRCALPHA)
            scanline.fill((0, 0, 0, 60))
            screen.blit(scanline, (0, y))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
