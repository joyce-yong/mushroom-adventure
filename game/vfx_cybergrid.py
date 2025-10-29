import pygame
import math
import random

class CyberGrid:
    def __init__(self, screen_width, screen_height, spacing=60, base_color=(60, 0, 120), trail_color=(209, 0, 209)):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.spacing = spacing
        self.base_color = base_color
        self.trail_color = trail_color 
        self.time_ms = 0
        self.scan_line_y = 0
        self.line_thickness = 3
        self.trail_length = int(screen_height * 0.15) # Vertical lines stay colored for 15% of screen height after being scanned

    def update(self, dt):
        """Update the internal time and scan line position."""
        self.time_ms += dt * 1000 

        # Update scan line position
        scan_speed = 0.05 * self.screen_height 
        self.scan_line_y += scan_speed * dt
        if self.scan_line_y > self.screen_height + self.trail_length: # Reset after the trail leaves the bottom
            self.scan_line_y = 0

    def _get_pulsing_color(self, base_color, time_ms):
        """Helper to calculate the pulsing color."""
        pulse = (math.sin(time_ms * 0.003) * 0.5) + 0.5 
        r = int(base_color[0] * (0.5 + 0.5 * pulse))
        g = int(base_color[1] * (0.5 + 0.5 * pulse))
        b = int(base_color[2] * (0.5 + 0.5 * pulse))
        return (r, g, b)

    def _draw_grid_lines(self, surface, pulsing_base_color, pulsing_trail_color):
        """Draws the main grid with the trail effect on both horizontal and vertical lines."""
        
        # Determine the scan area (from the current line Y to a point 'trail_length' above it)
        scan_trail_start = self.scan_line_y - self.trail_length
        scan_trail_end = self.scan_line_y

        # Draw vertical lines (affected by the scan area)
        for x in range(0, self.screen_width, self.spacing):
            
            # Draw the "Scanned" portion (within the vertical trail zone)
            start_y = max(0, scan_trail_start)
            end_y = min(self.screen_height, scan_trail_end)
            
            if end_y > start_y:
                pygame.draw.line(surface, pulsing_trail_color, (x, start_y), (x, end_y), self.line_thickness)

            # Draw the "Unscanned" portion (Above and below the trail)
            # Above the trail
            if start_y > 0:
                pygame.draw.line(surface, pulsing_base_color, (x, 0), (x, start_y), self.line_thickness)
            
            # Below the trail
            if end_y < self.screen_height:
                pygame.draw.line(surface, pulsing_base_color, (x, end_y), (x, self.screen_height), self.line_thickness)


        # Draw horizontal lines
        for y in range(0, self.screen_height, self.spacing):
            # Check if line is within the trail zone
            if scan_trail_start <= y < scan_trail_end:
                 # Use the pulsing TRAIL color for lines in the immediate scan zone
                pygame.draw.line(surface, pulsing_trail_color, (0, y), (self.screen_width, y), self.line_thickness)
            else:
                # Use the pulsing BASE color for lines outside the zone
                pygame.draw.line(surface, pulsing_base_color, (0, y), (self.screen_width, y), self.line_thickness)


    def _draw_scan_line(self, surface, line_color=(255, 255, 255, 150)):
        """Draws a bright, semi-transparent line sweeping down the screen with a customizable color."""
        
        line_surface = pygame.Surface((self.screen_width, self.line_thickness)).convert_alpha()
        line_surface.fill(line_color) 
        
        surface.blit(line_surface, (0, int(self.scan_line_y)))

    def _draw_data_noise(self, surface):
        """Draws random, small, flickering dots/squares."""
        
        if random.random() < 0.2: 
            num_dots = 10 
            noise_color = (255, 0, 255, 80)
            
            for _ in range(num_dots):
                x = random.randint(0, self.screen_width)
                y = random.randint(0, self.screen_height)
                dot_size = random.randint(1, 2)
                
                # Draw a small, random rectangle (the noise)
                pygame.draw.rect(surface, noise_color, (x, y, dot_size, dot_size))

    def draw(self, surface):
        """Draw all grid components."""
        
        # Calculate Pulsing Colors
        pulsing_base_color = self._get_pulsing_color(self.base_color, self.time_ms)
        pulsing_trail_color = self._get_pulsing_color(self.trail_color, self.time_ms)
        
        # Draw Main Grid with Trail Effect
        self._draw_grid_lines(surface, pulsing_base_color, pulsing_trail_color)

        # Draw Data Noise
        self._draw_data_noise(surface)

        # Draw Scan Line
        self._draw_scan_line(surface, line_color=(242, 0, 137, 180)) 