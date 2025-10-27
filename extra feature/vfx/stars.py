import pygame, sys, random, math

# Initialize pygame
pygame.init()

# Get screen info and set up window
info = pygame.display.Info()
width, height = info.current_w, info.current_h

screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
pygame.display.set_caption("Shining Star Animation")

clock = pygame.time.Clock()

# Star class to store position, speed, and twinkle behavior
class Star:
    def __init__(self):
        self.x = random.randint(0, width)
        self.y = random.randint(0, height)
        self.speed = random.uniform(0.0001, 0.1)  # Different speeds
        self.size = random.randint(1, 3)
        self.phase = random.uniform(0, math.pi * 2)  # Used for blinking
        self.brightness = random.randint(1, 255)

    def update(self):
        # Move star downward
        self.y += self.speed
        if self.y > height:
            self.y = 0
            self.x = random.randint(0, width)
            self.speed = random.uniform(1, 4)
        
        # Twinkle (blink) using sine wave
        self.phase += 0.05
        self.brightness = 180 + int(75 * math.sin(self.phase))
        self.brightness = max(0, min(255, self.brightness))

    def draw(self, surface):
        color = (self.brightness, self.brightness, self.brightness)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.size)

# Create a list of stars
stars = [Star() for _ in range(150)]

# Main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()

    screen.fill((0, 0, 10))  # Slightly bluish night sky

    # Update and draw stars
    for star in stars:
        star.update()
        star.draw(screen)

    pygame.display.flip()
    clock.tick(60)
