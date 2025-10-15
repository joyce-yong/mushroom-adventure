import pygame


pygame.init()
pygame.display.set_caption('Mushroom Adventure')

#Width and Height of screen
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 800

game_window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

#game time and frames
frameRate = pygame.time.Clock() # get time
FPS = 60 # 60 frames 




#const colours
BLACK = (0, 0, 0)



# background 
scroll_state = {'y': 0}
#background assets
scale_width = 2
scale_height = 1
old_bg_img = pygame.image.load('img/background/space.png').convert_alpha()
bg_img = pygame.transform.scale(old_bg_img, (old_bg_img.get_width() * scale_width * 2, old_bg_img.get_height() * scale_height))
bg_height = bg_img.get_height()
bg_width = bg_img.get_height()
screen_width, screen_height = game_window.get_size()
scale_bg = pygame.transform.scale(bg_img, (screen_width, screen_height))

