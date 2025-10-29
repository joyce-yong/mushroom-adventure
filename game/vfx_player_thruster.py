import pygame
import random
import math
import config

class ThrusterParticle(pygame.sprite.Sprite):
    def __init__(self, x, y, color, speed_y_offset):
        super().__init__()
        self.color = color
        self.size = random.randint(1, 5)
        self.lifetime = 30 # frames
        self.age = 0
        self.speed = random.uniform(1.0, 3.0) # Speed away from the ship
        
        # Calculate angle for spread
        angle = math.radians(random.uniform(80, 100))
        
        # Calculate velocity components
        self.vel_x = random.uniform(-2.5, 2.5) 
        self.vel_y = random.uniform(2.0, 4.0) + speed_y_offset 
        
        # Create image as a simple glow circle
        self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        
    def update(self):
        # Movement
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        
        # Age and Fade
        self.age += 1
        if self.age >= self.lifetime:
            self.kill()
            return
            
        # Fading effect: Reduce alpha based on age
        alpha = 255 - int(255 * (self.age / self.lifetime))
        
        # Recolor the particle with fading alpha
        current_color = self.color[:3] + (alpha,)
        self.image.fill((0, 0, 0, 0)) # Clear previous frame
        
        # Draw a subtle glow/flare
        pygame.draw.circle(self.image, current_color, (self.size, self.size), self.size)
    
class ThrusterVFX:
    def __init__(self, player):
        self.player = player
        self.particles = pygame.sprite.Group()
        self.last_spawn_time = 0
        self.spawn_interval = 1 # milliseconds between spawns (for a consistent stream)
        
        # Define the thruster positions relative to the center of the player ship image
        # (x_offset, y_offset, side_modifier)
        # side_modifier: -1 for left-outward, 1 for right-outward
        self.thruster_data = [
            {'offset_x': -15, 'offset_y': 45, 'side': -1}, # Left thruster
            {'offset_x': 15, 'offset_y': 45, 'side': 1}    # Right thruster
        ]

    def update(self, is_moving, scroll_speed):
        now = pygame.time.get_ticks()
        
        # Only spawn if the player is actively moving AND it's time for the next particle
        if is_moving and now - self.last_spawn_time > self.spawn_interval:
            self.spawn_particles(scroll_speed)
            self.last_spawn_time = now
            
        # Update all existing particles
        self.particles.update()

    def spawn_particles(self, scroll_speed):
        base_x = self.player.rect.centerx
        base_y = self.player.rect.centery
        
        speed_y_offset = self.player.velocity * (1 if config.moving_down else -1) - scroll_speed 

        # Loop through each defined thruster
        for thruster_info in self.thruster_data:
            offset_x = thruster_info['offset_x']
            offset_y = thruster_info['offset_y']
            side_modifier = thruster_info['side']
            
            thruster_x = base_x + offset_x
            thruster_y = base_y + offset_y
            
            color_choice = random.choice([
                (255, 100, 0),    # Bright Orange-Red
                (255, 60, 0),     # More fiery Red
                (255, 140, 0),    # Darker Orange
                (255, 200, 150),  # Light Orange (for inner glow)
                config.WHITE      # White (for core intensity)
            ]) 
            
            # Create particle
            particle = ThrusterParticle(thruster_x, thruster_y, color_choice, speed_y_offset)
            
            # Override vel_x to ensure outward spread from each thruster
            # Small random range, but biased by the side_modifier
            particle.vel_x = random.uniform(1.0, 3.0) * side_modifier + random.uniform(-0.5, 0.5) 
            
            self.particles.add(particle)

    def draw(self, surface):
        self.particles.draw(surface)