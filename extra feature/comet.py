import pygame, sys, math, random

# Setup
pygame.init()
pygame.display.set_caption("Comet Streak Effect")
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# Colors
COMET_COLOR = (254, 242, 80)
TAIL_COLOR = (255, 255, 191)

# Particle class (for tail)
class Particle:
    def __init__(self, x, y, angle, speed, size, life):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.size = size
        self.life = life
        self.alpha = 255

    def update(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        self.alpha -= 5
        self.life -= 1
        self.size *= 0.95
        return self.life > 0 and self.alpha > 0

    def draw(self, surface):
        if self.alpha > 0:
            s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*TAIL_COLOR, int(self.alpha)), (int(self.size), int(self.size)), int(self.size))
            surface.blit(s, (self.x - self.size, self.y - self.size))


# Comet class
class Comet:
    def __init__(self):
        self.reset()

    def reset(self):
        # Start from upper-left area
        self.x = random.randint(-100, 100)   # slightly off-screen to the left
        self.y = random.randint(-100, 100)   # slightly above the top
        self.angle = math.radians(45)        # diagonal down-right
        self.speed = random.uniform(6, 9)
        self.trail = []
        self.timer = 0

    def update(self):
        # Move comet
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

        # Generate trail particles
        self.timer += 1
        if self.timer % 2 == 0:
            for i in range(3):
                self.trail.append(Particle(
                    self.x, self.y,
                    self.angle + random.uniform(-0.1, 0.1),
                    random.uniform(0.5, 1.5),
                    random.randint(3, 6),
                    random.randint(15, 25)
                ))

        # Update and remove dead particles
        self.trail = [p for p in self.trail if p.update()]

        # Reset if off-screen
        if self.x > 900 or self.y > 700:
            self.reset()

    def draw(self, surface):
        for p in self.trail:
            p.draw(surface)

        # Draw comet head
        pygame.draw.circle(surface, COMET_COLOR, (int(self.x), int(self.y)), 6)
        pygame.draw.circle(surface, (255, 255, 0), (int(self.x), int(self.y)), 3)


# Main Loop
comet = Comet()

while True:
    screen.fill((10, 10, 25))  # dark night sky

    comet.update()
    comet.draw(screen)

    # Optional random small stars
    for _ in range(2):
        sx, sy = random.randint(0, 800), random.randint(0, 600)
        pygame.draw.circle(screen, (255, 255, 255), (sx, sy), 1)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    pygame.display.update()
    clock.tick(60)
