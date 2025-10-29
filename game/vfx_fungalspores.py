import pygame
import random
import math
import os

MUSHROOM_IMAGE_PATH = os.path.join('img', 'mushroom')

class SporeParticle:
    """Represents a single rising or falling spore using an image."""
    def __init__(self, x, y, size, velocity_y, alpha_mod, image):
        self.x = x
        self.y = y
        self.size = size
        self.velocity_y = velocity_y 
        self.alpha_mod = alpha_mod
        self.alpha = random.randint(50, 200)
        self.time_offset = random.uniform(0, 2 * math.pi)
        self.original_image = image
        self.image = pygame.transform.scale(image, (size, size)).convert_alpha()
        self.image.set_alpha(self.alpha)

    def update(self, dt):
        """Updates position, alpha, and returns True if still visible."""
        # vertical movement
        self.y += self.velocity_y * dt * 60 
        
        # subtle horizontal wobble
        self.x += math.sin(pygame.time.get_ticks() * 0.001 + self.time_offset) * 0.1
        
        self.alpha -= self.alpha_mod * dt * 60 * 0.5
        self.alpha = max(0, self.alpha)
        
        if self.alpha <= 0:
            return False 
        
        self.image.set_alpha(int(self.alpha))
        return True

    def draw(self, screen):
        """Draws the spore image to the main screen surface."""
        rect = self.image.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(self.image, rect)


class FungalSporesVFX:
    """Manages a collection of spores for win (rising) or lose (falling) states."""
    def __init__(self, width, height, direction, num_spores=80):
        self.width = width
        self.height = height
        self.spores = []
        self.loaded_images = self.load_images()
        
        min_speed = 0.3
        max_speed = 1.0
        self.size_min = 10
        self.size_max = 20
        self.alpha_fade = 0.5
        
        if direction == "rising":
            self.velocity_y_range = (-max_speed, -min_speed)
        else: # falling
            self.velocity_y_range = (min_speed, max_speed)

        self.max_spores = num_spores
        self.initial_spawn_duration = 2.0
        self.spawn_delay = self.initial_spawn_duration / self.max_spores 
        self.spawn_timer = 0.0
        self.initial_spawning_complete = False

    def load_images(self):
        """Loads all images from the directory."""
        images = []
        if not os.path.exists(MUSHROOM_IMAGE_PATH):
            print(f"Error: Image path not found: {MUSHROOM_IMAGE_PATH}")
            return images

        for filename in os.listdir(MUSHROOM_IMAGE_PATH):
            if filename.endswith(('.png', '.jpg', '.gif')):
                try:
                    path = os.path.join(MUSHROOM_IMAGE_PATH, filename)
                    image = pygame.image.load(path).convert_alpha()
                    images.append(image)
                except pygame.error as e:
                    print(f"Could not load image {filename}: {e}")
        
        if not images:
            print("Warning: No images loaded!")
        
        return images
        
    def _create_new_spore(self):
        """Creates and appends a new spore, or recycles an existing one."""
        if not self.loaded_images:
            return

        x = random.randint(0, self.width)
        margin = self.size_max

        if self.velocity_y_range[0] < 0: # rising spores (spawn below screen)
             y = self.height + random.uniform(0, margin * 2) 
        else: # falling spores (spawn above screen)
             y = 0 - random.uniform(0, margin * 2)

        size = random.randint(self.size_min, self.size_max)
        velocity_y = random.uniform(*self.velocity_y_range)
        image = random.choice(self.loaded_images)
        
        self.spores.append(SporeParticle(x, y, size, velocity_y, self.alpha_fade, image))

    def update(self, dt):
        """Updates and recycles spores."""
        if not self.initial_spawning_complete:
            self.spawn_timer += dt
            
            while self.spawn_timer >= self.spawn_delay and len(self.spores) < self.max_spores:
                self._create_new_spore()
                self.spawn_timer -= self.spawn_delay
                
            if len(self.spores) >= self.max_spores:
                self.initial_spawning_complete = True
        
        for spore in self.spores[:]:
            if not spore.update(dt):
                self.spores.remove(spore)

                if self.initial_spawning_complete:
                    self._create_new_spore()

    def draw(self, screen):
        """Draws all active spores."""
        for spore in self.spores:
            spore.draw(screen)