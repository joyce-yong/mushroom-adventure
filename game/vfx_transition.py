import pygame
import math
import random
import config


def _get_screen_size():
    w = getattr(config, "screen_width", None) or getattr(config, "SCREEN_WIDTH", None)
    h = getattr(config, "screen_height", None) or getattr(config, "SCREEN_HEIGHT", None)
    return int(w), int(h)


class Transition:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.screen_w, self.screen_h = _get_screen_size()
        self.gradient_surface = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)

        self.transition_active = False
        self.mode = None # "in" or "out"
        self.start_time = 0
        self.duration = 0
        self.t = 0.0
        
        # Warp Out state
        self.particles = []
        self.start_pos = (self.screen_w // 2, self.screen_h // 2)
        self.max_radius = math.hypot(self.screen_w, self.screen_h)

        # Warp In state
        self.dust = [] # Persistent dust particles for warp-in effect

        # vibrant galaxy palette
        self.colors = [
            (173, 248, 255),   # cyan
            (205, 137, 250),  # purple
            (255, 214, 255),  # pink
            (255, 238, 50)      # yellow
        ]

    def _blend_colors(self, t):
        c1 = self.colors[int(t * len(self.colors)) % len(self.colors)]
        c2 = self.colors[(int(t * len(self.colors)) + 1) % len(self.colors)]
        return [
            int(c1[i] + (c2[i] - c1[i]) * (math.sin(t * math.pi)))
            for i in range(3)
        ]

    def _draw_gradient(self, fade_alpha):
        blend = self._blend_colors(self.t)

        step = 4
        for y in range(0, self.screen_h, step):
            ratio = y / self.screen_h
            grad_color = [
                int(blend[i] * (1 - ratio) + 20 * ratio) for i in range(3)
            ]
            pygame.draw.rect(self.gradient_surface, grad_color + [255], (0, y, self.screen_w, step))

        self.gradient_surface.set_alpha(fade_alpha)
        self.screen.blit(self.gradient_surface, (0, 0))


    # Draw effect over the already drawn game/menu background
    def draw(self):
        if not self.transition_active:
            return

        if self.mode == "out":
            fade_alpha = int(255 * (self.t ** 1.5))
            
            if self.mode == "out":
                fade_alpha = int(255 * (self.t ** 1.5))
                
                for p in self.particles:
                    pygame.draw.circle(self.screen, p["color"], (int(p["pos"][0]), int(p["pos"][1])), p["size"])

            # ring
            radius = int(self.t * self.max_radius * 1.2)
            if radius < self.max_radius:
                pygame.draw.circle(self.screen, (255, 255, 255), (int(self.start_pos[0]), int(self.start_pos[1])), radius, 3)

        elif self.mode == "in":
            rev_t = 1.0 - self.t
            fade_alpha = int(255 * (rev_t ** 2))
            
            # dust
            for d in self.dust:
                pygame.draw.circle(self.screen, d["color"], (int(d["pos"][0]), int(d["pos"][1])), d["size"])
                
        else: 
             return

        self._draw_gradient(fade_alpha)


    # WARP OUT - NON-BLOCKING METHODS
    def warp_out(self, start_pos=None, duration=800):
        """Initializes and runs one frame of the warp-out transition.
        Call this every frame until it returns False."""
        if not self.transition_active:
            self.mode = "out"
            self.start_time = pygame.time.get_ticks()
            self.duration = duration
            self.start_pos = start_pos if start_pos is not None else (self.screen_w // 2, self.screen_h // 2)
            self.particles = []
            self.transition_active = True
            
        return self._warp_out_update()


    def _warp_out_update(self):
        if not self.transition_active or self.mode != "out":
            return False
            
        elapsed = pygame.time.get_ticks() - self.start_time
        self.t = min(elapsed / float(self.duration), 1.0)
        
        # spawn burst particles radiating from start_pos
        if elapsed % 30 < 16:
            for _ in range(8):
                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(2.5, 8.0) * (0.8 + self.t)
                color = random.choice(self.colors)
                self.particles.append({
                    "pos": [float(self.start_pos[0]), float(self.start_pos[1])],
                    "vel": [math.cos(angle) * speed, math.sin(angle) * speed],
                    "color": color,
                    "life": random.randint(18, 40),
                    "size": random.randint(1, 4)
                })

        # update particles
        for p in self.particles:
            p["pos"][0] += p["vel"][0]
            p["pos"][1] += p["vel"][1]
            p["vel"][0] *= 0.98
            p["vel"][1] *= 0.98
            p["life"] -= 1

        self.particles = [p for p in self.particles if p["life"] > 0]

        # Check if finished
        if self.t >= 1.0:
            self.transition_active = False
            return False # Finished
            
        return True # Still running


    # WARP IN - NON-BLOCKING METHODS
    def warp_in(self, duration=1000, include_dust=True):
        """Initializes and runs one frame of the warp-in transition.
        Call this every frame until it returns False."""
        if not self.transition_active:
            self.mode = "in"
            self.start_time = pygame.time.get_ticks()
            self.duration = duration
            self.transition_active = True
            self.dust = []
            
            if include_dust:
                for _ in range(40):
                    self.dust.append({
                        "pos": [random.uniform(0, self.screen_w), random.uniform(0, self.screen_h)],
                        "vel": [random.uniform(-0.2, 0.2), random.uniform(-0.2, 0.2)],
                        "color": random.choice(self.colors),
                        "size": random.randint(1, 3)
                    })
        
        return self._warp_in_update()


    def _warp_in_update(self):
        if not self.transition_active or self.mode != "in":
            return False
            
        elapsed = pygame.time.get_ticks() - self.start_time
        self.t = min(elapsed / float(self.duration), 1.0)
        
        # update dust
        for d in self.dust:
            d["pos"][0] += d["vel"][0]
            d["pos"][1] += d["vel"][1]
            # wrap
            if d["pos"][0] < -10: d["pos"][0] = self.screen_w + 10
            if d["pos"][0] > self.screen_w + 10: d["pos"][0] = -10
            if d["pos"][1] < -10: d["pos"][1] = self.screen_h + 10
            if d["pos"][1] > self.screen_h + 10: d["pos"][1] = -10

        # Check if finished
        if self.t >= 1.0:
            self.transition_active = False
            return False # Finished
            
        return True 