import pygame
from pygame import mixer
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




# const colours
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CAYAN = (0, 255, 255)




# action state var
moving_left = False
moving_right = False
moving_up = False
moving_down = False
shooting = False
heavy_shooting = False
rocket = False
laserLine_fire = False



# Audio

score = 0

# audio
laser_fx = pygame.mixer.Sound(os.path.join('audio', 'burst_fire.mp3'))
heavyLaser_fx = pygame.mixer.Sound(os.path.join('audio', 'laserLarge.ogg'))
rockets_fx = pygame.mixer.Sound(os.path.join('audio', 'tir.mp3'))
explode_fx = pygame.mixer.Sound(os.path.join('audio', 'snd_bomb.ogg'))
asteroid_fx = pygame.mixer.Sound(os.path.join('audio', 'breaPower.wav'))
rapid_laser_fx = pygame.mixer.Sound(os.path.join('audio','explosion4.ogg'))
shield_fx = pygame.mixer.Sound(os.path.join('audio', "teleport_01.ogg"))
death_fx = pygame.mixer.Sound(os.path.join('audio', 'explosion3.ogg'))

laser_fx.set_volume(0.2)

channel_1 = pygame.mixer.Channel(0)  # intros
channel_2 = pygame.mixer.Channel(1)  # EMPTY()
channel_3 = pygame.mixer.Channel(2)  # laser
channel_4 = pygame.mixer.Channel(3)  # Heavylaser
channel_5 = pygame.mixer.Channel(4)  # rocket
channel_6 = pygame.mixer.Channel(5)  # explosion
channel_7 = pygame.mixer.Channel(6)  # rapid fire
channel_8 = pygame.mixer.Channel(7)  # rapid fire ai
channel_9 = pygame.mixer.Channel(8)  # shield fx
channel_10 = pygame.mixer.Channel(9)  # death explosion
channel_11 = pygame.mixer.Channel(9)  # rapid fire
channel_12 = pygame.mixer.Channel(10)  # rapid fire
channel_13 = pygame.mixer.Channel(11)  # rapid fire

channel_2.set_volume(0.3)




# enemy deat rewards
enemy_rewards = {
    'enemy1': {'score': 50, 'shield': 20,'health': 0},
    'enemy2': {'score': 50, 'shield': 30,'health': 0},
    'enemy3': {'score': 50, 'shield': 10,'health': 0},
    'enemy4': {'score': 150, 'shield': 40,'health': 0},
    'enemy5': {'score': 350, 'shield': 60,'health': 5},
    'enemy6': {'score': 250, 'shield': 80,'health': 0}
}




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