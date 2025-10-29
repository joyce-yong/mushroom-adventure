import pygame
import random
import config 
from vfx_glowparticle import GlowParticle 

class ButtonGlowVFX:
    def __init__(self, num_particles_per_spawn=6):
        self.particles = []
        self.num_particles_per_spawn = num_particles_per_spawn
        self.button_coords = {} 

    def set_button_coords(self, coords_dict):
        self.button_coords = coords_dict
        
    def spawn_particles(self, count=None):
        count = count if count is not None else self.num_particles_per_spawn
        
        glow_colors = {
            "Start": (100, 255, 100),   # Greenish glow for Start
            "Story": (255, 198, 0),     # Bluish glow for Story
            "Controls": (161, 0, 242),  # Orangish glow for Controls
            "Quit": (255, 60, 60)       # Retained Red for Quit
        }

        for name, (x, y) in self.button_coords.items():
            color = glow_colors.get(name, config.WHITE)
            for _ in range(count):
                offset_x = random.uniform(-5, 5)
                offset_y = random.uniform(-5, 5)
                self.particles.append(GlowParticle(x + offset_x, y + offset_y, color)) 

    def update(self):
        if random.random() < 0.25:
             self.spawn_particles(count=random.randint(2, 4)) # Spawn more per burst
             
        self.particles = [p for p in self.particles if p.update()]

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)

    def burst_particles(self, button_name, count=50): # Spawn 50 particles on hover
        """Spawns a large burst of particles specifically from a named button."""
        
        # Define bright glow colors
        glow_colors = {
            "Start": (183, 228, 199),
            "Story": (250, 229, 136),
            "Controls": (200, 182, 255),
            "Quit": (255, 179, 193) 
        }

        if button_name in self.button_coords:
            x, y = self.button_coords[button_name]
            color = glow_colors.get(button_name, config.WHITE)
            
            for _ in range(count):
                offset_x = random.uniform(-10, 10)
                offset_y = random.uniform(-10, 10)
                self.particles.append(GlowParticle(x + offset_x, y + offset_y, color))