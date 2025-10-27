import pygame
import math
import random
import config


def _get_screen_size():
    # support both naming conventions in your repo
    w = getattr(config, "screen_width", None) or getattr(config, "SCREEN_WIDTH", None)
    h = getattr(config, "screen_height", None) or getattr(config, "SCREEN_HEIGHT", None)
    return int(w), int(h)


class Transition:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()

        # vibrant galaxy palette
        self.colors = [
            (80, 200, 255),   # cyan
            (200, 100, 255),  # purple
            (255, 100, 200),  # pink
            (255, 217, 0)    # yellow
        ]

    def _blend_colors(self, t):
        c1 = self.colors[int(t * len(self.colors)) % len(self.colors)]
        c2 = self.colors[(int(t * len(self.colors)) + 1) % len(self.colors)]
        return [
            int(c1[i] + (c2[i] - c1[i]) * (math.sin(t * math.pi)))
            for i in range(3)
        ]

    def _draw_gradient(self, t, fade_alpha):
        screen_w, screen_h = _get_screen_size()
        blend = self._blend_colors(t)
        fade_surface = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)

        step = 4
        for y in range(0, screen_h, step):
            ratio = y / screen_h
            grad_color = [
                int(blend[i] * (1 - ratio) + 20 * ratio) for i in range(3)
            ]
            pygame.draw.rect(fade_surface, grad_color + [255], (0, y, screen_w, step))

        fade_surface.set_alpha(fade_alpha)
        self.screen.blit(fade_surface, (0, 0))

    # -------------------------------------------------
    # Warp OUT (leave the scene). Accepts start_pos tuple.
    # If start_pos is None, center of screen is used.
    # -------------------------------------------------
    def warp_out(self, start_pos=None, duration=800):
        screen_w, screen_h = _get_screen_size()
        if start_pos is None:
            start_pos = (screen_w // 2, screen_h // 2)

        start_time = pygame.time.get_ticks()
        particles = []
        max_radius = math.hypot(screen_w, screen_h)

        while True:
            elapsed = pygame.time.get_ticks() - start_time
            t = min(elapsed / float(duration), 1.0)
            fade_alpha = int(255 * (t ** 1.5))

            # spawn burst particles radiating from start_pos
            if elapsed % 30 < 16:
                for _ in range(8):
                    angle = random.uniform(0, math.pi * 2)
                    speed = random.uniform(2.5, 8.0) * (0.8 + t)
                    color = random.choice(self.colors)
                    particles.append({
                        "pos": [float(start_pos[0]), float(start_pos[1])],
                        "vel": [math.cos(angle) * speed, math.sin(angle) * speed],
                        "color": color,
                        "life": random.randint(18, 40),
                        "size": random.randint(1, 4)
                    })

            # update particles
            for p in particles:
                p["pos"][0] += p["vel"][0]
                p["pos"][1] += p["vel"][1]
                p["vel"][0] *= 0.98
                p["vel"][1] *= 0.98
                p["life"] -= 1

            particles = [p for p in particles if p["life"] > 0]

            # clear / dark base
            self.screen.fill((6, 8, 20))

            # draw particles
            for p in particles:
                pygame.draw.circle(self.screen, p["color"], (int(p["pos"][0]), int(p["pos"][1])), p["size"])

            # expanding white ring (warp)
            radius = int(t * max_radius * 1.2)
            if radius < max_radius:
                pygame.draw.circle(self.screen, (255, 255, 255), (int(start_pos[0]), int(start_pos[1])), radius, 3)

            # vibrant gradient overlay
            self._draw_gradient(t, fade_alpha)

            pygame.display.flip()
            self.clock.tick(60)

            if t >= 1.0:
                break

    # -------------------------------------------------
    # Warp IN (enter the scene). Keeps subtle drifting dust.
    # -------------------------------------------------
    def warp_in(self, duration=1000, include_dust=True):
        screen_w, screen_h = _get_screen_size()
        start_time = pygame.time.get_ticks()

        # optional slow cosmic dust particles
        dust = []
        if include_dust:
            for _ in range(40):
                dust.append({
                    "pos": [random.uniform(0, screen_w), random.uniform(0, screen_h)],
                    "vel": [random.uniform(-0.2, 0.2), random.uniform(-0.2, 0.2)],
                    "color": random.choice(self.colors),
                    "size": random.randint(1, 3)
                })

        while True:
            elapsed = pygame.time.get_ticks() - start_time
            t = min(elapsed / float(duration), 1.0)
            rev_t = 1.0 - t
            fade_alpha = int(255 * (rev_t ** 2))

            # update dust
            if include_dust:
                for d in dust:
                    d["pos"][0] += d["vel"][0]
                    d["pos"][1] += d["vel"][1]
                    # wrap
                    if d["pos"][0] < -10: d["pos"][0] = screen_w + 10
                    if d["pos"][0] > screen_w + 10: d["pos"][0] = -10
                    if d["pos"][1] < -10: d["pos"][1] = screen_h + 10
                    if d["pos"][1] > screen_h + 10: d["pos"][1] = -10

            # clear previous frame
            self.screen.fill((6, 8, 20))

            # draw subtle dust
            if include_dust:
                for d in dust:
                    pygame.draw.circle(self.screen, d["color"], (int(d["pos"][0]), int(d["pos"][1])), d["size"])

            # vibrant gradient overlay
            self._draw_gradient(t, fade_alpha)

            pygame.display.flip()
            self.clock.tick(60)

            if t >= 1.0:
                break
