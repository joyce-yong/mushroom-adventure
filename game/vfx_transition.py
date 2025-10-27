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
        self.screen_w, self.screen_h = _get_screen_size()
        self.gradient_surface = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)

        # State variables for a non-blocking transition
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
            (80, 200, 255),   # cyan
            (200, 100, 255),  # purple
            (255, 100, 200),  # pink
            (255, 217, 0)     # yellow
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
        # Use the pre-created surface
        # self.gradient_surface.fill((0, 0, 0, 0)) # Not strictly needed if drawing over

        step = 4
        for y in range(0, self.screen_h, step):
            ratio = y / self.screen_h
            grad_color = [
                int(blend[i] * (1 - ratio) + 20 * ratio) for i in range(3)
            ]
            # Draw directly to the persistent surface
            pygame.draw.rect(self.gradient_surface, grad_color + [255], (0, y, self.screen_w, step))

        self.gradient_surface.set_alpha(fade_alpha)
        self.screen.blit(self.gradient_surface, (0, 0))

    # -------------------------------------------------
    # DRAW METHOD - Draw the effect over the already drawn game/menu background
    # -------------------------------------------------
    def draw(self):
        if not self.transition_active:
            return

        if self.mode == "out":
            # Warp Out: Fade is proportional to t
            fade_alpha = int(255 * (self.t ** 1.5))
            
            if self.mode == "out":
                # Warp Out: Fade is proportional to t
                fade_alpha = int(255 * (self.t ** 1.5))
                
                # Draw Particles directly to the screen (FASTEST)
                for p in self.particles:
                    # Note: No need for + (255,) for the color tuple if drawing directly
                    pygame.draw.circle(self.screen, p["color"], (int(p["pos"][0]), int(p["pos"][1])), p["size"])


            # Expanding white ring (warp)
            radius = int(self.t * self.max_radius * 1.2)
            if radius < self.max_radius:
                # This ring will draw over everything
                pygame.draw.circle(self.screen, (255, 255, 255), (int(self.start_pos[0]), int(self.start_pos[1])), radius, 3)

        elif self.mode == "in":
            # Warp In: Fade is proportional to rev_t (1-t)
            rev_t = 1.0 - self.t
            fade_alpha = int(255 * (rev_t ** 2))
            
            # Draw subtle dust (always visible during warp-in)
            for d in self.dust:
                pygame.draw.circle(self.screen, d["color"], (int(d["pos"][0]), int(d["pos"][1])), d["size"])
                
        else: # Transition completed, but somehow draw was called
             return

        # Vibrant gradient overlay (Applies the final fade layer)
        self._draw_gradient(fade_alpha)
        
        # Clock tick and display update is handled by the calling function (main game loop)

    # -------------------------------------------------
    # WARP OUT - NON-BLOCKING METHODS
    # -------------------------------------------------
    def warp_out(self, start_pos=None, duration=800):
        """Initializes and runs one frame of the warp-out transition.
        Call this every frame until it returns False."""
        if not self.transition_active:
             # Initialize state on first call
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

    # -------------------------------------------------
    # WARP IN - NON-BLOCKING METHODS
    # -------------------------------------------------
    def warp_in(self, duration=1000, include_dust=True):
        """Initializes and runs one frame of the warp-in transition.
        Call this every frame until it returns False."""
        if not self.transition_active:
            # Initialize state on first call
            self.mode = "in"
            self.start_time = pygame.time.get_ticks()
            self.duration = duration
            self.transition_active = True
            self.dust = []
            
            # initialize dust particles (only once)
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
            
        return True # Still running