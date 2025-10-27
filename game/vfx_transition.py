import pygame
import math
import random
import config


def _get_screen_size():
    w = getattr(config, "screen_width", None) or getattr(config, "SCREEN_WIDTH", None)
    h = getattr(config, "screen_height", None) or getattr(config, "SCREEN_HEIGHT", None)
    return int(w), int(h)


def ease_in_out_quad(t):
    """Smooth acceleration and deceleration curve (0 → 1)."""
    return 2 * t * t if t < 0.5 else -1 + (4 - 2 * t) * t


class Transition:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.colors = [
            (80, 200, 255),
            (200, 100, 255),
            (255, 255, 255),
        ]

    def _draw_particles(self, particles):
        for p in particles:
            x, y, r, c, alpha = p
            surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*c, int(alpha)), (r, r), r)
            self.screen.blit(surf, (x - r, y - r))

    def warp_out(self, center=None, duration=1.0):
        """Shrink to a point."""
        w, h = _get_screen_size()
        if center is None:
            center = (w // 2, h // 2)

        start_radius = math.hypot(w, h)
        end_radius = 0
        particles = []
        start_time = pygame.time.get_ticks()

        while True:
            now = pygame.time.get_ticks()
            t = (now - start_time) / (duration * 1000)
            if t >= 1:
                break
            eased = ease_in_out_quad(t)
            radius = start_radius * (1 - eased)

            # background fade
            fade_alpha = min(255, int(eased * 255))
            fade_surface = pygame.Surface((w, h))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(fade_alpha)
            self.screen.blit(fade_surface, (0, 0))

            # update particles
            if random.random() < 0.25:
                px = center[0] + random.uniform(-radius, radius)
                py = center[1] + random.uniform(-radius, radius)
                pr = random.randint(2, 5)
                color = random.choice(self.colors)
                particles.append([px, py, pr, color, 255])

            for p in particles:
                p[4] -= 5  # fade alpha
            particles = [p for p in particles if p[4] > 0]
            self._draw_particles(particles)

            # draw main warp circle
            pygame.draw.circle(self.screen, (0, 0, 0), center, int(radius))
            pygame.display.update()
            self.clock.tick(120)

    def warp_in(self, duration=1.0):
        """Expand from black hole."""
        w, h = _get_screen_size()
        center = (w // 2, h // 2)
        start_radius = 0
        end_radius = math.hypot(w, h)
        particles = []
        start_time = pygame.time.get_ticks()

        while True:
            now = pygame.time.get_ticks()
            t = (now - start_time) / (duration * 1000)
            if t >= 1:
                break
            eased = ease_in_out_quad(t)
            radius = start_radius + (end_radius - start_radius) * eased

            fade_alpha = max(0, 255 - int(eased * 255))
            fade_surface = pygame.Surface((w, h))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(fade_alpha)
            self.screen.blit(fade_surface, (0, 0))

            # particles expand outward
            if random.random() < 0.25:
                angle = random.uniform(0, math.tau)
                dist = random.uniform(radius * 0.8, radius)
                px = center[0] + math.cos(angle) * dist
                py = center[1] + math.sin(angle) * dist
                pr = random.randint(2, 5)
                color = random.choice(self.colors)
                particles.append([px, py, pr, color, 255])

            for p in particles:
                p[4] -= 6
            particles = [p for p in particles if p[4] > 0]
            self._draw_particles(particles)

            # draw black expanding circle
            pygame.draw.circle(self.screen, (0, 0, 0), center, int(radius))
            pygame.display.update()
            self.clock.tick(120)
