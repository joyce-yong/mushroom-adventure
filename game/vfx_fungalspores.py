import pygame
import random
import math

class SporeParticle:
    """Represents a single rising or falling spore."""
    def __init__(self, x, y, size, color, velocity_y, alpha_mod):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.velocity_y = velocity_y
        self.alpha_mod = alpha_mod
        self.alpha = random.randint(50, 200)
        self.original_color = color
        self.current_color = list(color) + [self.alpha]
        self.time_offset = random.uniform(0, 2 * math.pi)

    def update(self, dt):
        """Updates position, alpha, and returns True if still visible."""
        self.y += self.velocity_y * dt * 60
        self.x += math.sin(pygame.time.get_ticks() * 0.001 + self.time_offset) * 0.1
        
        self.alpha -= self.alpha_mod * dt * 60
        self.alpha = max(0, self.alpha)
        
        if self.alpha <= 0:
            return False
    
        self.current_color[3] = int(self.alpha)
        return True

    def draw(self, screen):
        """Draws the spore as a filled circle with alpha blending."""
        temp_surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        temp_surf.set_colorkey((0,0,0))

        for i in range(1, 3):
            fade_color = (self.original_color[0], self.original_color[1], self.original_color[2], int(self.alpha * (0.8 - i * 0.2)))
            pygame.draw.circle(temp_surf, fade_color, (self.size, self.size), self.size - i)

        main_color = (self.original_color[0], self.original_color[1], self.original_color[2], int(self.alpha))
        pygame.draw.circle(temp_surf, main_color, (self.size, self.size), self.size // 2)

        screen.blit(temp_surf, (int(self.x) - self.size, int(self.y) - self.size))


class FungalSporesVFX:
    """Manages a collection of spores for win (rising) or lose (falling) states."""
    def __init__(self, width, height, direction, color_theme, num_spores=100):
        self.width = width
        self.height = height
        self.spores = []
        
        min_speed = 0.5
        max_speed = 1.5
        size_min = 2
        size_max = 5
        alpha_fade = 0.5
        
        if direction == "rising":
            velocity_y_range = (-max_speed, -min_speed) # negative Y is UP
            alpha_fade = 0.6
        else: # falling
            velocity_y_range = (min_speed, max_speed) # positive Y is DOWN
            alpha_fade = 0.4

        for _ in range(num_spores):
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(size_min, size_max)
            velocity_y = random.uniform(*velocity_y_range)
            
            # random color
            color = random.choice(color_theme)
            
            self.spores.append(SporeParticle(x, y, size, color, velocity_y, alpha_fade))

    def update(self, dt):
        """Updates and recycles spores."""
        for spore in self.spores[:]:
            if not spore.update(dt):
                x = random.randint(0, self.width)
                y = self.height if spore.velocity_y < 0 else 0
                size = random.randint(2, 5)
                velocity_y = spore.velocity_y
                color = random.choice(self.spores[0].original_color_theme) if hasattr(self.spores[0], 'original_color_theme') else spore.original_color
                alpha_mod = spore.alpha_mod

                # re-initialize
                spore.__init__(x, y, size, color, velocity_y, alpha_mod)

    def draw(self, screen):
        """Draws all active spores."""
        for spore in self.spores:
            spore.draw(screen)