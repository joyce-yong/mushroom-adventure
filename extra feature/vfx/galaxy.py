import pygame, sys, random, math

pygame.init()
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Galaxy Environment VFX")
clock = pygame.time.Clock()

# ========================
# CONFIG
# ========================
STAR_COUNT = 300
COMET_CHANCE = 0.002
SHAKE_INTENSITY = 5
WARP_ACTIVE = False
WARP_SPEED = 0.25
NEBULA_COLORS = [(100, 30, 150, 40), (20, 100, 180, 50), (200, 50, 100, 35)]

# ========================
# STARFIELD
# ========================
stars = []
for _ in range(STAR_COUNT):
    depth = random.uniform(0.3, 1.0)
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)
    size = random.randint(1, 3)
    blink_phase = random.random() * math.pi * 2
    stars.append([x, y, depth, size, blink_phase])

def update_stars():
    for s in stars:
        s[1] += s[2] * 2
        if s[1] > HEIGHT:
            s[0] = random.randint(0, WIDTH)
            s[1] = 0
            s[2] = random.uniform(0.3, 1.0)
            s[3] = random.randint(1, 3)
            s[4] = random.random() * math.pi * 2

def draw_stars(surface, t):
    for x, y, depth, size, phase in stars:
        blink = (math.sin(t * 0.05 + phase) + 1) / 2
        brightness = int(150 + 105 * blink * depth)
        color = (brightness, brightness, brightness)
        pygame.draw.circle(surface, color, (int(x), int(y)), size)

# ========================
# NEBULA LAYERS
# ========================
def generate_nebula_surface():
    surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for color in NEBULA_COLORS:
        for _ in range(20):
            x, y = random.randint(0, WIDTH), random.randint(0, HEIGHT)
            radius = random.randint(200, 500)
            pygame.draw.circle(surf, color, (x, y), radius)
    return surf

nebula = generate_nebula_surface()
nebula_offset = 0

def draw_nebula(surface, t):
    global nebula_offset
    nebula_offset = (nebula_offset + 0.1) % HEIGHT
    surface.blit(nebula, (0, -nebula_offset))
    surface.blit(nebula, (0, HEIGHT - nebula_offset))

# ========================
# PLANETS
# ========================
planets = []
for _ in range(2):
    size = random.randint(120, 200)
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)
    speed = random.uniform(0.05, 0.2)
    color = random.choice([(80, 80, 180), (150, 100, 100), (100, 150, 100)])
    planets.append([x, y, size, speed, color])

def draw_planets(surface):
    for p in planets:
        p[0] += p[3]
        if p[0] > WIDTH + p[2]:
            p[0] = -p[2]
            p[1] = random.randint(100, HEIGHT - 100)
        pygame.draw.circle(surface, p[4], (int(p[0]), int(p[1])), p[2])
        glow = pygame.Surface((p[2]*2, p[2]*2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*p[4], 40), (p[2], p[2]), p[2])
        surface.blit(glow, (p[0]-p[2], p[1]-p[2]), special_flags=pygame.BLEND_ADD)

# ========================
# COMETS
# ========================
comets = []

def spawn_comet():
    x = random.randint(0, WIDTH)
    y = 0
    speed = random.uniform(8, 12)
    length = random.randint(50, 100)
    angle = random.uniform(math.radians(65), math.radians(115))
    comets.append([x, y, speed, length, angle])

def update_comets():
    for c in comets:
        c[0] += math.cos(c[4]) * c[2]
        c[1] += math.sin(c[4]) * c[2]
    for c in comets[:]:
        if c[1] > HEIGHT or c[0] < -100 or c[0] > WIDTH + 100:
            comets.remove(c)

def draw_comets(surface):
    for c in comets:
        end_x = c[0] - math.cos(c[4]) * c[3]
        end_y = c[1] - math.sin(c[4]) * c[3]
        pygame.draw.line(surface, (200, 200, 255), (c[0], c[1]), (end_x, end_y), 3)

# ========================
# SCREEN SHAKE
# ========================
shake_timer = 0
def trigger_shake(frames=20):
    global shake_timer
    shake_timer = frames

def apply_shake():
    global shake_timer
    if shake_timer > 0:
        shake_timer -= 1
        return random.randint(-SHAKE_INTENSITY, SHAKE_INTENSITY), random.randint(-SHAKE_INTENSITY, SHAKE_INTENSITY)
    return 0, 0

# ========================
# WARP TRANSITION
# ========================
warp_time = 0
def trigger_warp():
    global WARP_ACTIVE, warp_time
    WARP_ACTIVE = True
    warp_time = 0

def draw_warp(surface):
    global WARP_ACTIVE, warp_time
    if not WARP_ACTIVE: return
    warp_time += 1
    intensity = min(1, warp_time * WARP_SPEED)
    for i in range(0, WIDTH, 40):
        pygame.draw.line(surface, (255, 255, 255), (i, 0), (i, HEIGHT), int(3 * intensity))
    if intensity >= 1:
        WARP_ACTIVE = False

# ========================
# MAIN LOOP
# ========================
time = 0
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            nebula = generate_nebula_surface()

    time += 1
    if random.random() < COMET_CHANCE:
        spawn_comet()
    if random.randint(0, 2000) == 0:
        trigger_shake()
    if random.randint(0, 4000) == 0:
        trigger_warp()

    update_stars()
    update_comets()

    shake_x, shake_y = apply_shake()

    bg = pygame.Surface((WIDTH, HEIGHT))
    bg.fill((5, 5, 15))
    draw_stars(bg, time)
    draw_nebula(bg, time)
    draw_planets(bg)
    draw_comets(bg)
    draw_warp(bg)

    screen.blit(bg, (shake_x, shake_y))
    pygame.display.flip()
    clock.tick(60)
