import pygame, random, math

# === Star Object (with parallax + color by depth) ===
class Star:
    def __init__(self, width, height, depth):
        self.width = width
        self.height = height
        self.depth = depth  # smaller = farther, larger = nearer
        self.reset(randomize_y=True)

    def reset(self, randomize_y=False):
        self.x = random.randint(0, self.width)
        self.y = random.randint(0, self.height) if randomize_y else self.height + random.randint(0, 100)
        self.speed = self.depth * random.uniform(0.4, 1.5)
        self.size = max(1, int(self.depth))

        # 🎨 Color by depth (near = bluish, far = white)
        if self.depth < 1.2:      # far, dim white
            self.color = (200, 200, 255)
        elif self.depth < 2.2:    # mid, light blue
            self.color = (170, 200, 255)
        else:                     # near, rich blue glow
            self.color = (140, 170, 255)

        self.twinkle_speed = random.uniform(0.002, 0.007)
        self.phase = random.random() * math.pi * 2

    def update(self, dt, cam_dx, cam_dy):
        # depth-based parallax
        self.x += cam_dx * (self.depth * 0.4)
        self.y += cam_dy * (self.depth * 0.4)
        self.y -= self.speed * dt * 30

        # wrap screen edges
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


# === Galaxy Background (with stronger camera drift) ===
class GalaxyBackground:
    def __init__(self, width, height, num_stars=150):
        self.width = width
        self.height = height
        self.stars = [Star(width, height, random.uniform(0.5, 3.5)) for _ in range(num_stars)]
        self.comets = []
        self.last_comet_time = 0
        self.comet_interval = 3000  # ms

        # stronger camera drift
        self.cam_time = 0
        self.drift_speed = 0.0012   # faster drift (was 0.0004)
        self.amplitude = 60         # larger sway (was 20)

    def update(self, dt, time_ms):
        self.cam_time += dt * (1 + random.uniform(-0.1, 0.1))
        # exaggerated drift pattern
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

    def draw(self, surface, time_ms):
        for s in self.stars:
            s.draw(surface, time_ms)
        for c in self.comets:
            c.draw(surface)
