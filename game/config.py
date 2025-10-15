import pygame


pygame.init()
pygame.display.set_caption('Mushroom Adventure')

# Width and Height of screen
INTERNAL_WIDTH = 1400
INTERNAL_HEIGHT = 700
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



# background 
scroll_state = {'y': 0}
# background assets
scale_width = 2
scale_height = 1
old_bg_img = pygame.image.load('img/background/space.png').convert_alpha()
bg_img = pygame.transform.scale(old_bg_img, (old_bg_img.get_width() * scale_width * 2, old_bg_img.get_height() * scale_height))
bg_height = bg_img.get_height()
bg_width = bg_img.get_height()
screen_width, screen_height = game_window.get_size()
scale_bg = pygame.transform.scale(bg_img, (screen_width, screen_height))



# action state var
moving_left = False
moving_right = False
moving_up = False
moving_down = False
shooting = False
heavy_shooting = False
rocket = False