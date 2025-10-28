import pygame
import math
import random

# Colors (Adjust these or import from config if needed)
COMET_COLOR = (255, 255, 255)
TAIL_COLORS = [
    (180, 220, 255),  # Light Blue/Cyan
    (220, 180, 255),  # Light Purple
    (255, 200, 230),  # Pinkish
    (200, 255, 230),  # Mint Green
    (255, 240, 200)   # Light Gold
]

# Particle class (soft tail)
class Particle:
    def __init__(self, x, y, angle, speed, size, life, color):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.size = size
        self.life = life
        self.alpha = 255
        self.color = color

    def update(self):
        # Move softly
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

        # Gradual fade and shrink
        self.alpha -= 4
        self.life -= 1
        self.size *= 0.96

        return self.life > 0 and self.alpha > 0

    def draw(self, surface):
        if self.alpha > 0:
            # Create a small, temporary Surface with per-pixel alpha (SRCALPHA)
            s = pygame.Surface((self.size * 4, self.size * 4), pygame.SRCALPHA)
            grad_alpha = int(self.alpha * 0.8)

            # Outer faint glow
            pygame.draw.circle(
                s, (*self.color, int(grad_alpha * 0.2)),
                (int(self.size * 2), int(self.size * 2)), int(self.size * 2)
            )

            # Middle glow
            pygame.draw.circle(
                s, (*self.color, int(grad_alpha * 0.5)),
                (int(self.size * 2), int(self.size * 2)), int(self.size * 1.2)
            )

            # Core
            pygame.draw.circle(
                s, (*self.color, grad_alpha),
                (int(self.size * 2), int(self.size * 2)), int(self.size)
            )

            # Blit the temporary surface onto the main screen
            surface.blit(s, (self.x - self.size * 2, self.y - self.size * 2))


# Comet class
class Comet:
    # Set the diagonal downward-right flow for all comets
    FLOW_ANGLE = math.radians(35) 

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.reset()

    def reset(self):
        # Spawn randomly off-screen along the top or left side
        side = random.choice(['top', 'left'])
        
        if side == 'top':
            # Spawn above the screen, random X
            self.x = random.randint(0, self.screen_width + 50)
            self.y = random.randint(-50, 0)
        else:
            # Spawn left of the screen, random Y
            self.x = random.randint(-50, 0)
            self.y = random.randint(0, self.screen_height + 50)
            
        self.angle = Comet.FLOW_ANGLE
        self.speed = random.uniform(5, 9)
        self.size = random.randint(3, 8)
        self.trail = []
        self.timer = 0
        
        # Delay before the comet actually appears/starts moving
        self.spawn_delay = random.randint(30, 120) 

    def update(self):
        if self.spawn_delay > 0:
            self.spawn_delay -= 1
            return

        # Move comet
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

        # Create smooth trailing particles
        self.timer += 1
        if self.timer % 1 == 0:
            for _ in range(2): 
                self.trail.append(Particle(
                    self.x, self.y,
                    # Particle angle slightly trails opposite the comet direction
                    self.angle + math.radians(random.uniform(160, 200)), 
                    random.uniform(0.5, 1.4),
                    random.randint(2, self.size + 1),
                    random.randint(25, 45),
                    random.choice(TAIL_COLORS)
                ))

        # Update particles, keeping only the alive ones
        self.trail = [p for p in self.trail if p.update()]

        # Reset when off-screen
        if self.x > self.screen_width + 50 or self.y > self.screen_height + 50:
            self.reset()

    def draw(self, surface):
        if self.spawn_delay > 0:
            return

        # Draw trail first for correct visual layering
        for p in self.trail:
            p.draw(surface)

        # Simple soft head (no harsh glow)
        pygame.draw.circle(surface, COMET_COLOR, (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(surface, (255, 255, 210), (int(self.x), int(self.y)), int(self.size * 0.6))