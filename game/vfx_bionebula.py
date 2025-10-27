# vfx_bionebula.py
import pygame
import random
import math

class BioNebula:
    def __init__(self, width, height, num_spores=50):
        self.width = int(width)
        self.height = int(height)

        # animation state
        self.haze_timer = 0.0
        self.haze_shift = 0.0

        # camera-like gentle zoom/pan
        self.zoom_offset = 1.0
        self.pan_x = 0.0
        self.pan_y = 0.0

        # spores: [x, y, speed(px/s), size, color]
        self.spores = []
        for _ in range(num_spores):
            x = random.uniform(0, self.width)
            y = random.uniform(0, self.height)
            speed = random.uniform(10.0, 40.0)  # pixels per second
            size = random.randint(2, 6)
            color = random.choice([
                (180, 255, 230),
                (190, 200, 255),
                (255, 190, 255)
            ])
            self.spores.append([x, y, speed, size, color])

    def update(self, dt):
        """
        dt: seconds since last frame (float)
        """
        # update timers and shifts
        self.haze_timer += dt
        self.haze_shift = math.sin(self.haze_timer * 0.4) * 80.0

        # gentle zoom / pan (slow oscillation)
        self.zoom_offset = 1.0 + math.sin(self.haze_timer * 0.12) * 0.03
        self.pan_x = math.sin(self.haze_timer * 0.06) * 20.0
        self.pan_y = math.cos(self.haze_timer * 0.05) * 15.0

        # update spores positions
        for i, s in enumerate(self.spores):
            x, y, speed, size, color = s
            # move upward (negative y). use dt so motion is framerate independent
            y -= speed * dt
            # slight sideways wobble based on time & index
            wobble = math.sin(self.haze_timer * 0.4 + i * 0.13) * 6.0 * dt
            x += wobble

            # wrap when out of bounds
            if y < -10:
                y = self.height + 10
                x = random.uniform(0, self.width)

            # keep x inside range (small wrap)
            if x < -10:
                x = self.width + 10
            elif x > self.width + 10:
                x = -10

            self.spores[i][0] = x
            self.spores[i][1] = y

    def _clamp8(self, v):
        return max(0, min(255, int(v)))

    def draw(self, screen):
        screen.fill((5, 5, 15))
        overscale = 1.02

        # --- 1. gradient background (base surface) ---
        gradient = pygame.Surface((self.width, self.height))
        for y in range(self.height):
            # gentle banded variation using haze_shift
            r = 10 + 10 * math.sin((y + self.haze_shift) * 0.01)
            g = 15 + 25 * math.sin((y + self.haze_shift) * 0.008)
            b = 30 + 30 * math.cos((y + self.haze_shift) * 0.009)
            r = self._clamp8(r)
            g = self._clamp8(g)
            b = self._clamp8(b)
            pygame.draw.line(gradient, (r, g, b), (0, y), (self.width, y))

        # scale for gentle zoom (smoothscale for nicer quality)
        scaled_w = max(1, int(self.width * self.zoom_offset))
        scaled_h = max(1, int(self.height * self.zoom_offset))
        scaled = pygame.transform.smoothscale(gradient, (scaled_w, scaled_h))

        # center the scaled surface and apply pan offset
        blit_x = -(scaled_w - self.width) // 2 + int(self.pan_x)
        blit_y = -(scaled_h - self.height) // 2 + int(self.pan_y)
        screen.blit(scaled, (blit_x, blit_y))

        # --- 2. soft nebula haze layers (alpha) ---
        # Draw a few translucent blobs that slowly change size/position
        for i in range(3):
            haze_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            # radius varies with time
            radius = int(220 + math.sin(self.haze_timer * (0.9 + 0.2 * i) + i) * 80)
            # position shifts a bit
            cx = self.width // 2 + int(math.sin(self.haze_timer * (0.2 + i*0.1)) * (120 + i*30))
            cy = self.height // 2 + int(math.cos(self.haze_timer * (0.15 + i*0.08)) * (80 + i*20))
            alpha = max(10, min(80, 30 + int(math.sin(self.haze_timer * (0.3 + i*0.05)) * 30)))
            # color slightly different per layer
            layer_color = (60, 40 + i*10, 120 + i*10, alpha)
            pygame.draw.circle(haze_surf, layer_color, (cx, cy), abs(radius))
            screen.blit(haze_surf, (0, 0))

        # --- 3. drifting spores (bio-lights) ---
        t = pygame.time.get_ticks()
        for s in self.spores:
            x, y, _, size, color = s
            # alpha pulse per-spore (keeps within 0..255)
            alpha = 180 + int(math.sin((y * 0.05) + (t * 0.001)) * 50)
            alpha = max(0, min(255, alpha))
            spore_surf = pygame.Surface((size*4, size*4), pygame.SRCALPHA)
            pygame.draw.circle(spore_surf, (*color, alpha), (size*2, size*2), size)
            screen.blit(spore_surf, (int(x) - size*2, int(y) - size*2))
