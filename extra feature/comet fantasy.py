import pygame, sys, math, random

# Setup
pygame.init()
pygame.display.set_caption("Magical Comet Shower")
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# Colors
COMET_COLOR = (255, 255, 255)
TAIL_COLORS = [
    (180, 220, 255),
    (220, 180, 255),
    (255, 200, 230),
    (200, 255, 230),
    (255, 240, 200)
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

            surface.blit(s, (self.x - self.size * 2, self.y - self.size * 2))


# Comet class
class Comet:
    FLOW_ANGLE = math.radians(35)  # same direction for all

    def __init__(self):
        self.reset()

    def reset(self):
        # Spawn randomly along left side
        self.x = random.randint(-50, 0)
        self.y = random.randint(-50, 650)
        self.angle = Comet.FLOW_ANGLE
        self.speed = random.uniform(5, 9)
        self.size = random.randint(3, 8)
        self.trail = []
        self.timer = 0
        # Increase spawn delay range → makes new comets appear less often
        self.spawn_delay = random.randint(100, 500)

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
            for _ in range(2):  # fewer trail particles too
                self.trail.append(Particle(
                    self.x, self.y,
                    self.angle,
                    random.uniform(0.5, 1.4),
                    random.randint(2, self.size + 1),
                    random.randint(25, 45),
                    random.choice(TAIL_COLORS)
                ))

        # Update particles
        self.trail = [p for p in self.trail if p.update()]

        # Reset when off-screen
        if self.x > 850 or self.y > 650:
            self.reset()

    def draw(self, surface):
        if self.spawn_delay > 0:
            return

        # Draw trail first for layering
        for p in self.trail:
            p.draw(surface)

        # Simple soft head (no harsh glow)
        pygame.draw.circle(surface, COMET_COLOR, (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(surface, (255, 255, 210), (int(self.x), int(self.y)), int(self.size * 0.6))


# Main
comets = [Comet() for _ in range(5)]  # fewer comets at once

# Optional: slow global spawn timer
SPAWN_INTERVAL = 120
spawn_timer = 0

while True:
    # Semi-transparent background for trailing blur effect
    overlay = pygame.Surface((800, 600))
    overlay.fill((10, 10, 25))
    overlay.set_alpha(40)
    screen.blit(overlay, (0, 0))

    # Occasionally add new comets if fewer are active
    spawn_timer += 1
    if spawn_timer > SPAWN_INTERVAL and len(comets) < 6:
        comets.append(Comet())
        spawn_timer = 0

    # Update & draw comets
    for comet in comets:
        comet.update()
        comet.draw(screen)

    # Subtle stars twinkling
    for _ in range(2):
        sx, sy = random.randint(0, 800), random.randint(0, 600)
        brightness = random.randint(180, 255)
        pygame.draw.circle(screen, (brightness, brightness, 255), (sx, sy), 1)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    pygame.display.update()
    clock.tick(60)
