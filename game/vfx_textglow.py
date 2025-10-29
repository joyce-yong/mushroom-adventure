import pygame
import random
from vfx_glowparticle import GlowParticle

class GlowTextVFX:
    """Manages continuous particle spawning within a text area for a glow effect."""
    def __init__(self, rect, color, spawn_rate=0.4, particle_count_min=1, particle_count_max=3):
        self.rect = rect
        self.color = color
        self.particles = []
        self.spawn_rate = spawn_rate 
        self.count_min = particle_count_min
        self.count_max = particle_count_max
        
    def _spawn_particle(self):
        """Spawns a single particle randomly within the text's bounding box."""
        if not self.rect:
            return
            
        # random spawn point
        x = random.uniform(self.rect.left, self.rect.right)
        y = random.uniform(self.rect.top, self.rect.bottom)
        
        self.particles.append(GlowParticle(x, y, self.color))

    def update(self, dt):
        """Updates particles and manages continuous spawning."""
        if random.random() < self.spawn_rate:
            count = random.randint(self.count_min, self.count_max)
            for _ in range(count):
                self._spawn_particle()
            
        self.particles = [p for p in self.particles if p.update()]

    def draw(self, surface):
        """Draws all active particles."""
        for p in self.particles:
            p.draw(surface)