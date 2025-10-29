import pygame
import math
import random

class GlowParticle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(3, 6)
        self.angle = random.uniform(0, 2 * math.pi)
        self.speed = random.uniform(2.0, 4.0)
        self.life = random.randint(60, 100)
        self.alpha = 255

    def update(self):
        # move outward
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        
        # fade and shrink
        self.alpha -= (255 / self.life) * 2 # fade faster than life reduction
        self.size *= 0.98
        self.life -= 1
        
        return self.life > 0 and self.alpha > 0

    def draw(self, surface):
        if self.alpha > 0 and self.size > 1:
            s = pygame.Surface((int(self.size * 6), int(self.size * 6)), pygame.SRCALPHA)
            final_alpha = max(0, int(self.alpha))

            # outer glow (very transparent)
            center = (s.get_width() // 2, s.get_height() // 2)
            pygame.draw.circle(s, (*self.color, int(final_alpha * 0.1)), 
                               center, int(self.size * 3))
            # inner core (more opaque)
            pygame.draw.circle(s, (*self.color, int(final_alpha)), 
                               center, int(self.size * 1.5))
            
            surface.blit(s, (self.x - s.get_width() // 2, self.y - s.get_height() // 2))