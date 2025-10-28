import pygame
import random
import math

class SparkleParticle:
    """A single twinkling star particle."""
    def __init__(self, x, y, size, color, speed_mod):
        self.pos = pygame.Vector2(x, y)
        self.size = size
        self.color = color
        self.max_alpha = random.randint(150, 255)
        
        # random offset for the sine wave
        self.sin_offset = random.uniform(0, math.pi * 2) 
        # random speed
        self.speed = random.uniform(speed_mod * 0.8, speed_mod * 1.2)
        
        self.current_alpha = self.max_alpha
        
    def update(self, dt):
        """Updates the particle's twinkling alpha."""
        wave = (math.sin(pygame.time.get_ticks() * self.speed + self.sin_offset) + 1) / 2
        
        min_alpha = 50 
        alpha_range = self.max_alpha - min_alpha
        self.current_alpha = int(min_alpha + wave * alpha_range)
        
        return True

    def draw(self, screen):
        """Draws the particle as a circle with the current alpha value."""
        surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))
        
        pygame.draw.circle(surf, self.color, (self.size, self.size), self.size)
        
        surf.set_alpha(self.current_alpha)
        
        screen.blit(surf, (self.pos.x - self.size, self.pos.y - self.size))


class SparkleVFX:
    """Manages a persistent field of twinkling particles across the screen."""
    def __init__(self, width, height, num_particles=150, color=(255, 255, 255), speed_mod=0.006):
        self.width = width
        self.height = height
        self.particles = []
        self.color = color
        
        for _ in range(num_particles):
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(2, 4) # star size
            self.particles.append(SparkleParticle(x, y, size, color, speed_mod))

    def update(self, dt):
        """Updates all particles."""
        for p in self.particles:
            p.update(dt)

    def draw(self, screen):
        """Draws all particles."""
        for p in self.particles:
            p.draw(screen)