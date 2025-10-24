import pygame, sys, random, math

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Low HP Border VFX")
clock = pygame.time.Clock()

max_hp = 100
hp = 100
particles = []

def spawn_particles():
    # spawn around border edges
    for _ in range(6):
        side = random.choice(["top", "bottom", "left", "right"])
        w, h = screen.get_size()
        if side == "top":
            x = random.randint(0, w)
            y = random.randint(0, 12)
            vel = [random.uniform(-0.3, 0.3), random.uniform(0.3, 1)]
        elif side == "bottom":
            x = random.randint(0, w)
            y = h - random.randint(0, 12)
            vel = [random.uniform(-0.3, 0.3), random.uniform(-1, -0.3)]
        elif side == "left":
            x = random.randint(0, 12)
            y = random.randint(0, h)
            vel = [random.uniform(0.3, 1), random.uniform(-0.3, 0.3)]
        else:
            x = w - random.randint(0, 12)
            y = random.randint(0, h)
            vel = [random.uniform(-1, -0.3), random.uniform(-0.3, 0.3)]

        size = random.randint(2, 6)
        lifetime = random.randint(35, 70)
        shape = random.choice(["circle", "spark", "dot"])
        particles.append([x, y, vel, size, lifetime, shape])

def update_particles():
    for p in particles:
        p[0] += p[2][0]
        p[1] += p[2][1]
        p[4] -= 1
    for p in particles[:]:
        if p[4] <= 0:
            particles.remove(p)

def draw_particles(surface):
    for p in particles:
        alpha = max(0, min(255, int((p[4] / 70) * 255)))
        color = (255, random.randint(50, 100), 100, alpha)
        if p[5] == "circle":
            pygame.draw.circle(surface, color, (int(p[0]), int(p[1])), p[3])
        elif p[5] == "spark":
            # spark line
            end_x = p[0] + random.uniform(-p[3], p[3])
            end_y = p[1] + random.uniform(-p[3], p[3])
            pygame.draw.line(surface, color, (p[0], p[1]), (end_x, end_y), 1)
        else:
            # small glowing dot
            pygame.draw.rect(surface, color, (p[0], p[1], 2, 2))

def draw_dynamic_border(surface, time, hp):
    w, h = surface.get_size()
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)

    if hp > 70:
        return
    elif hp > 40:
        base_alpha = 100
        thickness = 15
    else:
        base_alpha = 180
        thickness = 25

    # wave offset and pulse
    pulse = (math.sin(time * 2.5) + 1) / 2
    wave_offset = int(math.sin(time * 3) * 3)
    alpha = base_alpha + int(40 * pulse)

    # layer 1: main border
    color = (255, 0, 0, alpha)
    pygame.draw.rect(overlay, color, (0, 0, w, thickness))                # top
    pygame.draw.rect(overlay, color, (0, h - thickness, w, thickness))    # bottom
    pygame.draw.rect(overlay, color, (0, 0, thickness, h))                # left
    pygame.draw.rect(overlay, color, (w - thickness, 0, thickness, h))    # right

    # layer 2: inner shimmer moving
    shimmer_alpha = int(80 + 50 * pulse)
    shimmer_color = (255, 60, 60, shimmer_alpha)
    offset = int((math.sin(time * 4) + 1) * 5)
    pygame.draw.rect(overlay, shimmer_color, (offset, offset, w - offset * 2, thickness // 2))
    pygame.draw.rect(overlay, shimmer_color, (offset, h - thickness // 2 - offset, w - offset * 2, thickness // 2))
    pygame.draw.rect(overlay, shimmer_color, (offset, offset, thickness // 2, h - offset * 2))
    pygame.draw.rect(overlay, shimmer_color, (w - thickness // 2 - offset, offset, thickness // 2, h - offset * 2))

    draw_particles(overlay)
    surface.blit(overlay, (0, 0))

# Main loop
time = 0
while True:
    dt = clock.tick(60) / 1000
    time += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                hp = max(0, hp - 20)
            elif event.key == pygame.K_UP:
                hp = min(max_hp, hp + 20)

    screen.fill((20, 20, 20))

    if hp <= 70:
        spawn_particles()
    update_particles()

    draw_dynamic_border(screen, time, hp)

    font = pygame.font.SysFont(None, 48)
    text = font.render(f"HP: {hp}", True, (255, 255, 255))
    screen.blit(text, (350, 280))

    pygame.display.flip()
