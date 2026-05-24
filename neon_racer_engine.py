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
GRID_COLOR = (30, 30, 80)

# --- CLASSES ---

class Player:
    def __init__(self):
        self.width = 60
        self.height = 40
        self.x = WIDTH // 2
        self.y = HEIGHT - 100
        self.speed = 7

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > 150:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < WIDTH - 150 - self.width:
            self.x += self.speed

    def draw(self, surface):
        # Placeholder for the White A5 Beetle sprite
        # We'll draw a white rectangle for now
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, (255, 255, 255), rect)
        # Adding some "taillight" glows
        pygame.draw.rect(surface, NEON_PINK, (self.x, self.y + 30, 15, 5))
        pygame.draw.rect(surface, NEON_PINK, (self.x + self.width - 15, self.y + 30, 15, 5))

class Road:
    def __init__(self):
        self.offset = 0
        self.speed = 15

    def update(self):
        self.offset = (self.offset + self.speed) % 100

    def draw(self, surface):
        # Draw the vanishing point / horizon
        pygame.draw.rect(surface, BLACK, (0, 0, WIDTH, HEIGHT // 2))
        
        # Draw the perspective grid (pseudo-3D)
        horizon_y = HEIGHT // 2
        
        # Draw horizontal lines (moving towards viewer)
        for i in range(0, HEIGHT // 2 + 10):
            current_y = horizon_y + ((i * 10 + self.offset) % (HEIGHT // 2))
            
            if current_y < HEIGHT:
                # Draw the line widening as it gets closer
                width_at_y = (current_y - horizon_y) * 2 
                start_x = (WIDTH // 2) - (width_at_y // 2)
                end_x = (WIDTH // 2) + (width_at_y // 2)
                pygame.draw.line(surface, GRID_COLOR, (start_x, current_y), (end_x, current_y), 1)

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
        pygame.draw.rect(screen, (10, 0, 20), (0, 0, WIDTH, HEIGHT // 2))
        
        road.draw(screen)
        player.draw(screen)

        # Scanline effect
        for y in range(0, HEIGHT, 4):
            line = pygame.Surface((WIDTH, 1), pygame.SRCALPHA)
            line.fill((0, 0, 0, 50))
            screen.blit(line, (0, y))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
