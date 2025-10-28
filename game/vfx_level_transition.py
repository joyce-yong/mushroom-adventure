# vfx_transition.py
import pygame

class LevelTransition:
    def __init__(self, surface, outcome_color="green"):
        self.surface = surface
        # ... (setup self.transition_color based on outcome_color)
        if outcome_color == "green":
            self.transition_color = (0, 200, 0)
        else: # "red"
            self.transition_color = (200, 0, 0)
            
        self.max_alpha = 255
        self.current_alpha = 0
        self.is_running = True
        self.overlay = pygame.Surface(surface.get_size())
        self.overlay.fill(self.transition_color)

    def warp_out(self):
        if not self.is_running:
            return False
        
        fade_speed = 5 
        self.current_alpha += fade_speed
        
        if self.current_alpha >= self.max_alpha:
            self.current_alpha = self.max_alpha
            self.is_running = False
        return self.is_running
        
    def draw(self):
        if self.is_running or self.current_alpha > 0:
            self.overlay.set_alpha(self.current_alpha)
            self.surface.blit(self.overlay, (0, 0))

    def warp_in(self):
        # Must have this method for "transition_in" state to work
        # ... (Your fade-in logic)
        pass