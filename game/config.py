import pygame # type: ignore
from pygame import mixer # type: ignore
import os


pygame.init()
pygame.mixer.init()
pygame.mixer.set_num_channels(16) # have 16 channels to play sound

pygame.display.set_caption('MushMush')

# Width and Height of screen
INTERNAL_WIDTH = 1600
INTERNAL_HEIGHT = 800
internal_surface = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT))

# Fullscreen mode
display_info = pygame.display.Info()
SCREEN_WIDTH = display_info.current_w
SCREEN_HEIGHT = display_info.current_h

game_window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)

# game time and frames
frameRate = pygame.time.Clock() # get time
FPS = 60 # 60 frames 

# fonts
button_font = pygame.font.SysFont(None, 70)
font = pygame.font.SysFont('', 25)
fontLarge = pygame.font.SysFont('', 45)


# const colours
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CAYAN = (0, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)






# action state var
moving_left = False
moving_right = False
moving_up = False
moving_down = False
shooting = False
heavy_shooting = False
rocket = False
laserLine_fire = False
plasma_shooting = False


# audio
laser_fx = pygame.mixer.Sound(os.path.join('audio', 'burst_fire.mp3'))
heavyLaser_fx = pygame.mixer.Sound(os.path.join('audio', 'laserLarge.ogg'))
rockets_fx = pygame.mixer.Sound(os.path.join('audio', 'tir.mp3'))
explode_fx = pygame.mixer.Sound(os.path.join('audio', 'snd_bomb.ogg'))
asteroid_fx = pygame.mixer.Sound(os.path.join('audio', 'breaPower.wav'))
rapid_laser_fx = pygame.mixer.Sound(os.path.join('audio','explosion4.ogg'))
shield_fx = pygame.mixer.Sound(os.path.join('audio', "teleport_01.ogg"))
death_fx = pygame.mixer.Sound(os.path.join('audio', 'explosion3.ogg'))
plasma_explode_fx = pygame.mixer.Sound(os.path.join('audio', 'buzz.ogg'))
plasma_fx = pygame.mixer.Sound(os.path.join('audio', 'misc_01.ogg'))
mothership_fx = pygame.mixer.Sound(os.path.join('audio', 'boss.mp3'))
laser_fx.set_volume(0.2)

channel_1 = pygame.mixer.Channel(0)  # intros
channel_2 = pygame.mixer.Channel(1)  # Asteroid
channel_3 = pygame.mixer.Channel(2)  # laser
channel_4 = pygame.mixer.Channel(3)  # Heavylaser
channel_5 = pygame.mixer.Channel(4)  # rocket
channel_6 = pygame.mixer.Channel(5)  # explosion
channel_7 = pygame.mixer.Channel(6)  # rapid fire
channel_8 = pygame.mixer.Channel(7)  # rapid fire ai
channel_9 = pygame.mixer.Channel(8)  # shield fx
channel_10 = pygame.mixer.Channel(9)  # death explosion
channel_11 = pygame.mixer.Channel(10)  # plasma explode
channel_12 = pygame.mixer.Channel(11)  # plasma
channel_13 = pygame.mixer.Channel(12)  # Long range strike
channel_14 = pygame.mixer.Channel(13)  # rapid fire
channel_15 = pygame.mixer.Channel(14)  # rapid fire

channel_2.set_volume(0.3)

# sound flags
long_strike_sound_played = False


# Stats
score = 0
# Dictionaries

# enemy deat rewards
enemy_rewards = {
    'enemy1': {'score': 50, 'shield': 20,'health': 0},
    'enemy2': {'score': 50, 'shield': 30,'health': 0},
    'enemy3': {'score': 50, 'shield': 10,'health': 0},
    'enemy4': {'score': 150, 'shield': 40,'health': 0}, # laserline enemy
    'enemy5': {'score': 350, 'shield': 60,'health': 5}, # battleship
    'enemy6': {'score': 250, 'shield': 80,'health': 0}, # plasma ship
    'enemy7': {'score': 750, 'shield': 120,'health': 50}, # pwer battleship
    'enemy8': {'score': 2750, 'shield': 200,'health': 100}, # mothership
    'enemy9': {'score': 20, 'shield': 0,'health': 0} # mothership strike craft
}
ship_stats = {
    'player': {'health': 200, 'shield': 200},
    'enemy1': {'health': 110, 'shield': -1},
    'enemy2': {'health': 120, 'shield': -1},
    'enemy3': {'health': 150, 'shield': -1},
    'enemy4': {'health': 200, 'shield': -1},
    'enemy5': {'health': 800, 'shield': -1},
    'enemy6': {'health': 100, 'shield': 550},
    'enemy7': {'health': 500, 'shield': 1350},
    'enemy8': {'health': 1500, 'shield': 4550},
    'enemy9': {'health': 60, 'shield': -1}
}

motherShip_boss_waves = [5, 15, 25, 35, 45, 55, 60, 65, 70, 77, 79, 81, 89, 100]
motherShip_boss_active = False
mothership_wave = 0 # keep track of current wave and mothership wave to spawn only once per wave level





# Background 
scroll_state = {'y': 0}

# background assets
# list of background images and their file paths
bg_files = [
    'img/background/sd3.png',
    'img/background/sd2.png',
    'img/background/sd4.png',
    'img/background/sd5.png',
    'img/background/sd1.png'
]

# list to store scaled pygame.Surface objects
background_list = []

screen_width, screen_height = game_window.get_size()

for file in bg_files:
    old_bg = pygame.image.load(file).convert_alpha()
    
    # image scale factors
    scale_width = 1
    scale_height = 1
    
    # initial scaling
    bg_img = pygame.transform.scale(
        old_bg,
        (old_bg.get_width() * scale_width,
        old_bg.get_height() * scale_height))
    
    # new scaled image to fit screen
    scaled_bg = pygame.transform.scale(bg_img, (screen_width, screen_height))
    
    # add to list
    background_list.append(scaled_bg)