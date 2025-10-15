import pygame
import config

# create base character class
class Character(pygame.sprite.Sprite):
    def __init__(self, character_type, character_x, character_y, scale, velocity):
        pygame.sprite.Sprite.__init__(self)
        self.character_type = character_type
        self.velocity = velocity
        self.flip = False # if needed to flip in x direction
        self.health = 100 # player and enemy health
        self.max_health = self.health # set max health to normal health for overflow
        self.alive = True
        
        
        #for enemies
        self.spawn_time = pygame.time.get_ticks()
        self.start_delay = 4000
        self.phase = 'enter'
        self.target_y = 50
        
        
        # load object image
        img = pygame.image.load(f'img/{self.character_type}/Idle/0.png').convert_alpha()
        self.image = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
        self.rect = self.image.get_rect()
        self.rect.center = (character_x, character_y)
        
        
    # create custom draw method for characters
    def draw(self):
        config.game_window.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
        
        
        
        
       
        
    # movement method for player or ai if you choose
    def movement(self, moving_left, moving_right, moving_up, moving_down):
        dx = 0
        dy = 0
        
        if moving_left:
            dx = -1
            self.direction = -1
        if moving_right:
            dx = 1
            self.direction = 1
        if moving_up:
            dy = -1
        if moving_down:
            dy = 1    
            
        
        # normalize diagonal speed
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071
            
        
        # apply movement on rect
        self.rect.x += dx * self.velocity
        self.rect.y += dy * self.velocity
        



    #AI enemies 
    def update_enemy(self, window_height):
        if self.phase == "enter":
            if self.rect.y < self.target_y:
                self.rect.y += self.velocity
            else:
                self.phase = "hold"
                self.spawn_time = pygame.time.get_ticks()
                
        elif self.phase == "hold":
            if pygame.time.get_ticks() - self.spawn_time >= self.start_delay:
                self.phase = "move"
                
        elif self.phase == "move":
            self.rect.y += self.velocity
            if self.rect.top > window_height:
                self.kill()
                
                
    