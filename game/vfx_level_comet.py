import pygame
import math
import random

# Colors
COMET_COLOR = (255, 255, 255)
TAIL_COLORS = [
    (180, 220, 255),  # Light Blue/Cyan
    (220, 180, 255),  # Light Purple
    (255, 200, 230),  # Pinkish
    (200, 255, 230),  # Mint Green
    (255, 240, 200)   # Light Gold
]

# Particle class
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
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        self.alpha -= 4
        self.life -= 1
        self.size *= 0.96
        return self.life > 0 and self.alpha > 0

    def draw(self, surface):
        if self.alpha > 0:
            s = pygame.Surface((self.size * 4, self.size * 4), pygame.SRCALPHA)
            grad_alpha = int(self.alpha * 0.8)
            pygame.draw.circle(s, (*self.color, int(grad_alpha * 0.2)), (int(self.size * 2), int(self.size * 2)), int(self.size * 2))
            pygame.draw.circle(s, (*self.color, int(grad_alpha * 0.5)), (int(self.size * 2), int(self.size * 2)), int(self.size * 1.2))
            pygame.draw.circle(s, (*self.color, grad_alpha), (int(self.size * 2), int(self.size * 2)), int(self.size))
            surface.blit(s, (self.x - self.size * 2, self.y - self.size * 2))


class Comet:
    BASE_FLOW_ANGLE = math.radians(45) # Start with 45 degrees for a clear diagonal

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.reset()

    def reset(self):
        # Spawn randomly off-screen along the top or left side
        side = random.choice(['top', 'left'])
        
        if side == 'top':
            # Spawn above the screen, random X
            self.x = random.randint(-50, self.screen_width + 50)
            self.y = random.randint(-100, -20) # Spawn a bit further up
        else:
            # Spawn left of the screen, random Y
            self.x = random.randint(-100, -20) # Spawn a bit further left
            self.y = random.randint(-50, self.screen_height + 50) # Allow spawning from various Y positions
            
        # Add slight random deviation to the angle
        angle_dev = random.uniform(30, 60) # Range from slightly less to slightly more diagonal
        self.angle = math.radians(angle_dev)
        
        # Adjust base speed. Comets should feel faster than the background scroll
        self.base_speed = random.uniform(5, 10) 
        self.size = random.randint(3, 7)
        self.trail = []
        self.timer = 0
        
        self.spawn_delay = random.randint(30, 120) 

    def update(self, scroll_speed):
        """Updates position, incorporating the background scroll speed to make it relative."""
        if self.spawn_delay > 0:
            self.spawn_delay -= 1
            return
        
        # Calculate individual X and Y components of the comet's movement
        dx = math.cos(self.angle) * self.base_speed
        dy = math.sin(self.angle) * self.base_speed

        self.x += dx
        self.y += (dy + scroll_speed) 
        
        # Create smooth trailing particles
        self.timer += 1
        if self.timer % 1 == 0:
            for _ in range(2): 
                self.trail.append(Particle(
                    self.x, self.y,
                    random.uniform(math.radians(200), math.radians(250)), # A range of upward-backward angles
                    random.uniform(0.5, 1.4),
                    random.randint(2, self.size + 1),
                    random.randint(25, 45),
                    random.choice(TAIL_COLORS)
                ))

        # Update particles, keeping only the alive ones
        self.trail = [p for p in self.trail if p.update()]
        for p in self.trail:
            p.y += scroll_speed # Particles also need to scroll down with the background relative to their own movement

        # Reset when completely off-screen (below and to the right)
        if self.x > self.screen_width + 100 or self.y > self.screen_height + 100:
            self.reset()

    def draw(self, surface):
        if self.spawn_delay > 0:
            return

        # Draw trail
        for p in self.trail:
            p.draw(surface)

        # Simple soft head 
        pygame.draw.circle(surface, COMET_COLOR, (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(surface, (255, 255, 210), (int(self.x), int(self.y)), int(self.size * 0.6))