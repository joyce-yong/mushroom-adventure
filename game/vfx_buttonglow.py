# In vfx_buttonglow.py

import pygame
import random
import config 
from vfx_glowparticle import GlowParticle 

class ButtonGlowVFX:
    # --- ADJUSTMENT: INCREASE DEFAULT PARTICLE SPAWN DENSITY ---
    def __init__(self, num_particles_per_spawn=6): # Increased from 3 to 6
    # -----------------------------------------------------------
        self.particles = []
        self.num_particles_per_spawn = num_particles_per_spawn
        self.button_coords = {} 

    def set_button_coords(self, coords_dict):
        self.button_coords = coords_dict
        
    def spawn_particles(self, count=None):
        count = count if count is not None else self.num_particles_per_spawn
        
        # --- ADJUSTMENT: CHANGE GLOW COLORS ---
        glow_colors = {
            "Start": (100, 255, 100),   # Greenish glow for Start
            "Story": (255, 198, 0),   # Bluish glow for Story
            "Controls": (161, 0, 242), # Orangish glow for Controls
            "Quit": (255, 60, 60)       # Retained Red for Quit
        }
        # You can use config.GREEN, config.BLUE etc if you have them defined in config.py
        # For example:
        # glow_colors = {
        #     "Start": config.GREEN,
        #     "Story": config.BLUE,
        #     "Controls": config.ORANGE,
        #     "Quit": config.RED
        # }
        # ------------------------------------

        for name, (x, y) in self.button_coords.items():
            color = glow_colors.get(name, config.WHITE)
            for _ in range(count):
                offset_x = random.uniform(-5, 5)
                offset_y = random.uniform(-5, 5)
                self.particles.append(GlowParticle(x + offset_x, y + offset_y, color)) 

    def update(self):
        # --- ADJUSTMENT: INCREASE SPAWN FREQUENCY ---
        if random.random() < 0.25: # Increased chance from 0.15 to 0.25
             self.spawn_particles(count=random.randint(2, 4)) # Spawn more per burst
        # --------------------------------------------
             
        self.particles = [p for p in self.particles if p.update()]

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)

    def burst_particles(self, button_name, count=50): # Spawn 50 particles on hover
        """Spawns a large burst of particles specifically from a named button."""
        
        # Define bright glow colors (Copy from spawn_particles for consistency)
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
                # Particles in the burst should spread out fast and wide
                # We can temporarily override the particle's inherent speed/life for the burst
                
                # Note: The GlowParticle class must be flexible enough to handle these properties
                # Since GlowParticle uses random speed, the burst will already look dramatic.
                
                offset_x = random.uniform(-10, 10) # Slightly larger spawn area
                offset_y = random.uniform(-10, 10)
                self.particles.append(GlowParticle(x + offset_x, y + offset_y, color))