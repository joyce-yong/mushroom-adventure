import pygame, random, math

# --- Color helper ---
def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

# --- Galaxy Text Drawer ---
def draw_galaxy_text(surface, text, font, center, time_ms, base_color1=(255, 230, 100), base_color2=(255, 180, 50)):
    # Animate color shimmer
    t = (math.sin(time_ms * 0.002) + 1) / 2
    color = lerp_color(base_color1, base_color2, t)

    # Draw glowing aura
    glow_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    for i in range(4):
        alpha = 60 - i * 12
        radius = 2 + i * 2
        glow_text = font.render(text, True, color)
        glow_text.set_alpha(alpha)
        pos = (center[0] - glow_text.get_width() // 2, center[1] - glow_text.get_height() // 2)
        glow_surface.blit(glow_text, (pos[0] - radius, pos[1]))
        glow_surface.blit(glow_text, (pos[0] + radius, pos[1]))
        glow_surface.blit(glow_text, (pos[0], pos[1] - radius))
        glow_surface.blit(glow_text, (pos[0], pos[1] + radius))
    surface.blit(glow_surface, (0, 0), special_flags=pygame.BLEND_ADD)

    # Draw main text (crisp)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=center)
    surface.blit(text_surface, text_rect)

    # Add sparkle VFX
    if random.random() < 0.05:
        sparkle_list.append({
            "x": center[0] + random.randint(-80, 80),
            "y": center[1] + random.randint(-30, 30),
            "radius": random.randint(1, 3),
            "life": 255
        })

def update_sparkles(surface):
    for s in sparkle_list[:]:
        s["life"] -= 6
        s["y"] -= 0.2
        if s["life"] <= 0:
            sparkle_list.remove(s)
            continue
        alpha = max(0, min(255, s["life"]))
        pygame.draw.circle(surface, (255, 255, 150, alpha), (int(s["x"]), int(s["y"])), s["radius"])

# store sparkle particles
sparkle_list = []

# === Star Object (with parallax + color by depth) ===
class Star:
    def __init__(self, width, height, depth):
        self.width = width
        self.height = height
        self.depth = depth
        self.reset(randomize_y=True)

    def reset(self, randomize_y=False):
        self.x = random.randint(0, self.width)
        self.y = random.randint(0, self.height) if randomize_y else self.height + random.randint(0, 100)
        self.speed = self.depth * random.uniform(0.4, 1.5)
        self.size = max(1, int(self.depth))
        if self.depth < 1.2:
            self.color = (200, 200, 255)
        elif self.depth < 2.2:
            self.color = (170, 200, 255)
        else:
            self.color = (140, 170, 255)
        self.twinkle_speed = random.uniform(0.002, 0.007)
        self.phase = random.random() * math.pi * 2

    def update(self, dt, cam_dx, cam_dy):
        self.x += cam_dx * (self.depth * 0.4)
        self.y += cam_dy * (self.depth * 0.4)
        self.y -= self.speed * dt * 30
        if self.y < -5:
            self.y = self.height + 5
        if self.x < -5:
            self.x = self.width + 5
        elif self.x > self.width + 5:
            self.x = -5

    def draw(self, surface, time_ms):
        alpha = 150 + int(105 * math.sin(time_ms * self.twinkle_speed + self.phase))
        pygame.draw.circle(surface, (*self.color, alpha), (int(self.x), int(self.y)), self.size)


# === Comet / Shooting Star ===
class Comet:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.reset()

    def reset(self):
        self.x = random.randint(-100, -10)
        self.y = random.randint(0, self.height // 2)
        self.length = random.randint(40, 100)
        self.speed = random.uniform(600, 900)
        self.color = (200, 200, 255)
        self.active = True

    def update(self, dt):
        if not self.active:
            return
        self.x += self.speed * dt
        self.y += self.speed * dt * 0.2
        if self.x > self.width + 100 or self.y > self.height + 100:
            self.active = False

    def draw(self, surface):
        if self.active:
            end_pos = (int(self.x), int(self.y))
            start_pos = (int(self.x - self.length), int(self.y - self.length * 0.2))
            pygame.draw.line(surface, self.color, start_pos, end_pos, 2)
            pygame.draw.circle(surface, self.color, end_pos, 2)


# === Warp Ripple Effect ===
class WarpRipple:
    def __init__(self, position, color=(100, 200, 255)):
        self.x, self.y = position
        self.radius = 0
        self.alpha = 255
        self.color = color
        self.active = True

    def update(self, dt):
        if not self.active:
            return
        self.radius += 800 * dt
        self.alpha -= 250 * dt
        if self.alpha <= 0:
            self.active = False

    def draw(self, surface):
        if not self.active:
            return
        radius = int(self.radius)
        if radius <= 0:
            return
        ripple = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(ripple, (*self.color, int(self.alpha)), (radius, radius), radius, 3)
        surface.blit(ripple, (self.x - radius, self.y - radius), special_flags=pygame.BLEND_ADD)


# === Galaxy Background ===
class GalaxyBackground:
    def __init__(self, width, height, num_stars=150):
        self.width = width
        self.height = height
        self.stars = [Star(width, height, random.uniform(0.5, 3.5)) for _ in range(num_stars)]
        self.comets = []
        self.ripples = []
        self.last_comet_time = 0
        self.comet_interval = 3000
        self.cam_time = 0
        self.drift_speed = 0.0012
        self.amplitude = 60

    def spawn_ripple(self, position):
        self.ripples.append(WarpRipple(position))

    def update(self, dt, time_ms):
        self.cam_time += dt * (1 + random.uniform(-0.1, 0.1))
        cam_dx = math.sin(self.cam_time * 1.5) * self.amplitude * dt
        cam_dy = math.cos(self.cam_time * 2.2) * self.amplitude * dt

        for s in self.stars:
            s.update(dt, cam_dx, cam_dy)

        if time_ms - self.last_comet_time > self.comet_interval:
            self.comets.append(Comet(self.width, self.height))
            self.last_comet_time = time_ms

        for c in self.comets[:]:
            c.update(dt)
            if not c.active:
                self.comets.remove(c)

        for r in self.ripples[:]:
            r.update(dt)
            if not r.active:
                self.ripples.remove(r)

    def draw(self, surface, time_ms):
        for s in self.stars:
            s.draw(surface, time_ms)
        for c in self.comets:
            c.draw(surface)
        for r in self.ripples:
            r.draw(surface)
