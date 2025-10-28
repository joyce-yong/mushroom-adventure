import pygame
import math

class GradientHaze:
    def __init__(self, screen_width, screen_height, start_color, end_color, max_alpha=120, fade_speed=0.002):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.max_alpha = max_alpha
        self.fade_speed = fade_speed
        self.alpha_time = 0.0

        self.surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        self.create_gradient(start_color, end_color)

    def create_gradient(self, start_color, end_color):
        """Pre-renders a vertical gradient onto the surface."""
        r1, g1, b1 = start_color
        r2, g2, b2 = end_color
        
        for y in range(self.screen_height):
            # calculate interpolation factor
            f = y / self.screen_height
            
            # linearly interpolate R, G, B values
            r = int(r1 + (r2 - r1) * f)
            g = int(g1 + (g2 - g1) * f)
            b = int(b1 + (b2 - b1) * f)
            
            color = (r, g, b)
            
            pygame.draw.line(self.surface, color, (0, y), (self.screen_width, y))


    def update(self, dt):
        """Updates the transparency of the entire surface to create a pulse."""
        self.alpha_time += dt * self.fade_speed
        
        wave = (math.sin(self.alpha_time) + 1) / 2 
        
        min_alpha = 40
        alpha_range = self.max_alpha - min_alpha
        current_alpha = int(min_alpha + wave * alpha_range)
        
        self.surface.set_alpha(current_alpha)

    def draw(self, screen):
        """Draws the gradient haze to the main screen surface."""
        screen.blit(self.surface, (0, 0))