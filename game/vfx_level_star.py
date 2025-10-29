import pygame
import random
import config 

class FastStarVFX:
    
    # Far Layer (Distant depth)
    FAR_COUNT = 180
    FAR_SPEED_MIN = 0.005
    FAR_SPEED_MAX = 0.1
    FAR_COLOR = (150, 150, 150) # Dimmer white/gray
    FAR_SIZE = 1 

    # Near Layer (Passing close, high velocity)
    NEAR_COUNT = 50
    NEAR_SPEED_MIN = 4.0
    NEAR_SPEED_MAX = 6.0
    NEAR_COLOR = config.CAYAN # Brighter/cyanish
    NEAR_SIZE_MAX = 2
    
    def __init__(self, screen_width, screen_height):
        """Initializes the star field with two distinct layers."""
        self.width = screen_width
        self.height = screen_height
        # Store all stars in one unified list, but initialized separately
        self.stars = self._initialize_stars() 

    def _get_star_config(self, layer_type):
        """Returns configuration based on the layer type (for initialization and resetting)."""
        if layer_type == 'far':
            count = self.FAR_COUNT
            speed_min, speed_max = self.FAR_SPEED_MIN, self.FAR_SPEED_MAX
            color = self.FAR_COLOR
            size_max = self.FAR_SIZE
        else: # 'near'
            count = self.NEAR_COUNT
            speed_min, speed_max = self.NEAR_SPEED_MIN, self.NEAR_SPEED_MAX
            color = self.NEAR_COLOR
            size_max = self.NEAR_SIZE_MAX
        
        return count, speed_min, speed_max, color, size_max, layer_type

    def _initialize_stars(self):
        """Creates the initial list of stars for both layers."""
        all_stars = []
        
        # Initialize two distinct groups of stars
        for config_tuple in [self._get_star_config('far'), self._get_star_config('near')]:
            count, speed_min, speed_max, color, size_max, layer_type = config_tuple
            
            for _ in range(count):
                speed_range = speed_max - speed_min
                all_stars.append({
                    'x': random.randint(0, self.width),
                    'y': random.randint(0, self.height),
                    'size': random.randint(1, size_max),
                    # Calculate speed within the layer's range
                    'speed': speed_min + random.random() * speed_range,
                    'color': color,
                    'flicker_timer': random.randint(0, 120), 
                    'is_visible': True,
                    'layer': layer_type # Identify the layer for resetting
                })
                
        return all_stars

    def _reset_star(self, star):
        """Resets a star that has scrolled off the screen."""
        # Get the config for the star's layer
        _, speed_min, speed_max, color, size_max, _ = self._get_star_config(star['layer'])
        speed_range = speed_max - speed_min
        
        star['y'] = -star['size'] # Reset above the screen
        star['x'] = random.randint(0, self.width)
        star['size'] = random.randint(1, size_max)
        star['speed'] = speed_min + random.random() * speed_range
        star['flicker_timer'] = random.randint(0, 120)
        star['is_visible'] = True 

    def update(self):
        """Updates the position and flicker state of all stars in both layers."""
        for star in self.stars:
            star['y'] += star['speed']
            
            # Blinking logic
            star['flicker_timer'] -= 1
            if star['flicker_timer'] <= 0:
                star['is_visible'] = not star['is_visible']
                star['flicker_timer'] = random.randint(10, 120)
            
            # Reset stars that scroll off the bottom
            if star['y'] > self.height:
                self._reset_star(star)

    def draw(self, surface):
        """Draws the visible stars, using lines for the fast 'Near' stars."""
        for star in self.stars:
            if star['is_visible']:
                color = star['color']
                center_x = int(star['x'])
                center_y = int(star['y'])
                
                if star['layer'] == 'near':
                    streak_length = int(star['speed'] * 0.8) 
                    
                    start_point = (center_x, center_y)
                    end_point = (center_x, center_y + streak_length)
                    
                    pygame.draw.line(surface, color, start_point, end_point, star['size'])

                else: # 'far' layer remains a single circle
                    # Draw as a dim, twinkling point
                    pygame.draw.circle(surface, color, (center_x, center_y), star['size'])