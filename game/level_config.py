import os

# Level configurations
LEVELS = {
    1: {
        'name': 'Level 1',
        
        # weapon availability
        'weapons': {
            'laser': True,           # A key
            'heavy_laser': True,     # D key  
            'rocket': True,          # S key
            'laser_line': False,     # W key
            'plasma': False          # Q key
        },
        
        # enemy types that can spawn
        'enemy_types': ['enemy1', 'enemy2', 'enemy3'],
        'enemy_weights': [3, 3, 3],
        
        # spawn rates
        'enemy_spawn_interval': 13000,  # 13 seconds
        'asteroid_spawn_rate': 0.002,   # Lower rate
        
        # special objects
        'blackholes_enabled': False,
        'mothership_enabled': False,
        
        # background
        'background_files': [
            'img/background/space.png'
        ],
        
        # wave configuration
        'wave_size_multiplier': 1,

        # target score
        'target_score': 500,
    },
    
    2: {
        'name': 'Level 2',
        
        # weapon availability
        'weapons': {
            'laser': True,           # A key
            'heavy_laser': True,     # D key
            'rocket': True,          # S key
            'laser_line': True,      # W key
            'plasma': True           # Q key
        },
        
        # enemy types that can spawn
        'enemy_types': ['enemy1', 'enemy2', 'enemy3', 'enemy4', 'enemy5', 'enemy6', 'enemy7'],
        'enemy_weights': [6, 6, 6, 4, 2, 4, 1],
        
        # spawn rates
        'enemy_spawn_interval': 11000,  # 11 seconds
        'asteroid_spawn_rate': 0.005,
        
        # special objects
        'blackholes_enabled': True,
        'mothership_enabled': True,
        
        # background
        'background_files': [
            'img/background/sd3.png',
            'img/background/sd2.png', 
            'img/background/sd4.png',
            'img/background/sd5.png',
            'img/background/sd1.png'
        ],
        
        # wave configuration
        'wave_size_multiplier': 1,

        # target score
        'target_score': 1000,
    }
}

def get_level_config(level_number):
    """Get configuration for a specific level"""
    if level_number not in LEVELS:
        raise ValueError(f"Level {level_number} not found. Available levels: {list(LEVELS.keys())}")
    return LEVELS[level_number]

def get_available_levels():
    """Get list of available level numbers"""
    return list(LEVELS.keys())

def load_background_images(level_config):
    """Load and scale background images for a level"""
    import pygame
    
    background_list = []
    screen_width, screen_height = pygame.display.get_surface().get_size()
    
    for file in level_config['background_files']:
        if os.path.exists(file):
            old_bg = pygame.image.load(file).convert_alpha()
            
            # Scale to fit screen
            scaled_bg = pygame.transform.scale(old_bg, (screen_width, screen_height))
            background_list.append(scaled_bg)
        else:
            print(f"Warning: Background file {file} not found")
    
    return background_list
