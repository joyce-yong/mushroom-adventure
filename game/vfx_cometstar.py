import pygame, os, sys, config, math, random

COMET_COLOR = (255, 255, 255)
TAIL_COLORS = [
    (180, 220, 255),
    (220, 180, 255),
    (255, 200, 230),
    (200, 255, 230),
    (255, 240, 200)
]

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


# Comet class
class Comet:
    FLOW_ANGLE = math.radians(35) # same direction for all

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.reset()

    def reset(self):
        self.x = random.randint(-50, 0)
        self.y = random.randint(-50, self.screen_height + 50)
        self.angle = Comet.FLOW_ANGLE
        self.speed = random.uniform(7, 12) 
        self.size = random.randint(2, 5) 
        self.trail = []
        self.timer = 0

        self.spawn_delay = random.randint(50, 200)

    def update(self):
        if self.spawn_delay > 0:
            self.spawn_delay -= 1
            return

        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

        self.timer += 1
        if self.timer % 1 == 0:
            for _ in range(2): 
                self.trail.append(Particle(
                    self.x, self.y, self.angle, random.uniform(0.5, 1.4),
                    random.randint(1, self.size), random.randint(20, 40),
                    random.choice(TAIL_COLORS)
                ))

        self.trail = [p for p in self.trail if p.update()]

        if self.x > self.screen_width + 50 or self.y > self.screen_height + 50:
            self.reset()

    def draw(self, surface):
        if self.spawn_delay > 0: return

        for p in self.trail:
            p.draw(surface)

        pygame.draw.circle(surface, COMET_COLOR, (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(surface, (255, 255, 210), (int(self.x), int(self.y)), int(self.size * 0.6))


class CometStarVFX:
    def __init__(self, screen_width, screen_height, num_comets=8, star_density=5):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.comets = [Comet(screen_width, screen_height) for _ in range(num_comets)]
        self.star_density = star_density 
        self.SPAWN_INTERVAL = 60
        self.spawn_timer = 0
        self.max_comets = num_comets + 4

    def update(self):
        non_resetting_comets = [c for c in self.comets if c.spawn_delay <= 0]
        self.spawn_timer += 1
        if self.spawn_timer > self.SPAWN_INTERVAL and len(non_resetting_comets) < self.max_comets:
            self.comets.append(Comet(self.screen_width, self.screen_height))
            self.spawn_timer = 0
        
        for comet in self.comets:
            comet.update()

    def draw(self, surface):
        # Draw Comets
        for comet in self.comets:
            comet.draw(surface)

        # Subtle Stars Twinkling
        for _ in range(self.star_density): 
            sx = random.randint(0, self.screen_width)
            sy = random.randint(0, self.screen_height)
            brightness = random.randint(180, 255)
            
            pygame.draw.circle(surface, (brightness, brightness, 255), (sx, sy), 2) 