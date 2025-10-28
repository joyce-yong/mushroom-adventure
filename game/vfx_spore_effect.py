import pygame
import random 
import math

class Spore:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.uniform(2, 6)
        self.angle = random.uniform(0, 2 * math.pi)
        self.speed = random.uniform(0.5, 2)
        self.life = random.randint(30, 80)
        self.alpha = 255

        mushroom_colors = [
            (181, 101, 29),    # brown cap
            (212, 163, 115),   # beige
            (154, 205, 50),    # spore green
            (170, 132, 224),   # violet mushroom
            (173, 255, 255)    # glowing cyan spores
        ]
        self.color = random.choice(mushroom_colors)

    def update(self):
        # move slowly outward
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

        # gradually shrink and fade
        self.size *= 0.96
        self.alpha -= 4
        self.life -= 1

        return self.life > 0 and self.alpha > 0 and self.size > 0.5

    def draw(self, surface):
        # create a glowing circle using alpha surface
        spore_surface = pygame.Surface((self.size * 6, self.size * 6), pygame.SRCALPHA)
        glow_color = (*self.color, int(self.alpha))
        pygame.draw.circle(spore_surface, glow_color, (int(self.size * 3), int(self.size * 3)), int(self.size * 1.5))
        surface.blit(spore_surface, (self.x - self.size * 3, self.y - self.size * 3))
