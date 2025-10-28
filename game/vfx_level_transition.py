import pygame
import random

class LevelTransition: # Renamed from Transition to LevelTransition as per your description
    def __init__(self, surface, outcome_color="green"):
        self.surface = surface
        self.screen_width, self.screen_height = surface.get_size()
        
        # Define transition colors (red for failure, green for success)
        if outcome_color == "green":
            self.base_color = (0, 200, 0) # Green
        else: # "red"
            self.base_color = (200, 0, 0) # Red
            
        self.max_alpha = 255
        self.current_alpha = 0
        self.is_running = True
        
        # Create a persistent overlay surface
        self.overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA) # Use SRCALPHA for transparency
        self.overlay.fill((0,0,0,0)) # Start fully transparent
        
        self.fade_speed = 4 # Control speed here (lower for longer, smoother)

        # --- NEW: Parameters for streaky/warp effect ---
        self.num_streaks = 100 # Number of streaks
        self.streaks = []
        self.streak_speed_factor = 1.5 # How much faster streaks move than alpha fade
        self.initialize_streaks()

    def reset_to_max(self):
        """Prepares the transition object for a fade-in (warp_in) sequence."""
        self.current_alpha = self.max_alpha
        self.is_running = True

    def initialize_streaks(self):
        # Create random streak properties
        for _ in range(self.num_streaks):
            x = random.randint(0, self.screen_width)
            y = random.randint(0, self.screen_height)
            length = random.randint(20, 100) # Length of the streak
            thickness = random.randint(1, 3) # Thickness of the streak
            # Store initial Y and current Y
            self.streaks.append({'x': x, 'y': y, 'length': length, 'thickness': thickness, 'initial_y': y})

    def update_streaks(self):
        # Move and reset streaks
        for streak in self.streaks:
            streak['y'] += self.fade_speed * self.streak_speed_factor # Move based on fade speed
            if streak['y'] > self.screen_height:
                # Reset streak to top, potentially at a new random X
                streak['y'] = -streak['length'] - random.randint(0, self.screen_height // 2) 
                streak['x'] = random.randint(0, self.screen_width)

    def warp_out(self):
        if not self.is_running:
            return False
        
        self.current_alpha += self.fade_speed # Increment alpha
        
        if self.current_alpha >= self.max_alpha:
            self.current_alpha = self.max_alpha
            self.is_running = False
        
        # Update streaks even when not drawing (or just before drawing)
        self.update_streaks() 
        return self.is_running
        
    def draw(self):
        if self.is_running or self.current_alpha > 0:
            # Clear the overlay and redraw everything
            self.overlay.fill((0,0,0,0)) # Clear previous frame's drawings
            
            # Draw the base color with current alpha
            base_overlay_surface = pygame.Surface(self.surface.get_size(), pygame.SRCALPHA)
            base_overlay_surface.fill(self.base_color + (min(self.current_alpha, 200),)) 
            self.overlay.blit(base_overlay_surface, (0,0))

            # Draw the streaks
            streak_alpha_step = max(5, self.current_alpha // 5) 
            for streak in self.streaks:
                bright_color = tuple(min(255, c + 55) for c in self.base_color)
                
                # Draw a rect for the streak
                streak_rect_color = bright_color + (min(self.current_alpha, 255),) # Streaks also fade in
                
                pygame.draw.rect(self.overlay, streak_rect_color, 
                                 (streak['x'], int(streak['y']), streak['thickness'], streak['length']))
            
            self.surface.blit(self.overlay, (0, 0))

    def warp_in(self):
        if not self.is_running:
            return False
            
        self.current_alpha -= self.fade_speed # <--- CHANGE 2: Decrease alpha (fade in)
        
        if self.current_alpha <= 0:
            self.current_alpha = 0
            self.is_running = False
            
        # Update streaks just like warp_out, but now they are moving AWAY
        self.update_streaks() 
        return self.is_running