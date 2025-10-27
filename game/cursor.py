import pygame
import os

from spore_effect import Spore
import random

class Cursor:
    def __init__(self, folder_path="img/cursor", frame_rate=10):
        self.frames = []
        self.load_frames(folder_path)
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = frame_rate
        self.spores = []

        # hide the default system cursor
        pygame.mouse.set_visible(False)

    def load_frames(self, folder_path, scale_factor=1.5):
        for filename in sorted(os.listdir(folder_path)):
            if filename.endswith(('.png', '.jpg')):
                img = pygame.image.load(os.path.join(folder_path, filename)).convert_alpha()

                if scale_factor != 1.0:
                    new_size = (int(img.get_width() * scale_factor), int(img.get_height() * scale_factor))
                    img = pygame.transform.scale(img, new_size)
                
                self.frames.append(img)

        if not self.frames:
            print("Warning: No cursor images found in", folder_path)

    def spawn_spores(self, pos):
        """Create multiple spores at the cursor position."""
        for _ in range(random.randint(10, 20)):
            self.spores.append(Spore(pos[0], pos[1]))

    def update(self):
        """Update cursor animation."""
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.last_update = now

    def draw(self, surface):
        """Draw cursor at mouse position."""
        if not self.frames:
            return
        mouse_pos = pygame.mouse.get_pos()
        current_image = self.frames[self.current_frame]

        # adjust offset
        rect = current_image.get_rect(center=mouse_pos)

        surface.blit(current_image, rect)
