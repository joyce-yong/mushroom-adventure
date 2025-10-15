import pygame
import config

from projectiles import Laser

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


        # laser shooting attributes
        self.lasers = pygame.sprite.Group()
        self.laser_cooldown = 100           # milliseconds
        self.laser_shot_time = 0
        



    # create custom draw method for characters
    def draw(self):
        config.game_window.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
        
        
    # update character class objects
    def update(self, player):
        self.check_alive(player)    
        
       





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

        
        # clamp player on screen
        if self.rect.left < 0:
            self.rect.left = 0 # stop from going off to left
        if self.rect.right > config.SCREEN_WIDTH: # check internal not external resolution
            self.rect.right = config.SCREEN_WIDTH
        if self.rect.top < 0:# stop goinng off at right 
            self.rect.top = 0 # stop from going of top screen
        if self.rect.bottom > config.SCREEN_HEIGHT: #internal screen hight not scaled one
            self.rect.bottom = config.SCREEN_HEIGHT # stop going of screen at bottom 
            
        if self.rect.left < -1:
            self.kill()
        if self.rect.right > config.SCREEN_WIDTH + 1:
             self.kill()
        if self.rect.bottom > config.SCREEN_HEIGHT + 1: # internal resolution height
            self.kill()
        if self.rect.top < -1:
            self.kill()
            




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
                
                



    # laser shoot check method for player and enemy
    def shoot_laser(self, target_player=None, target_enemy_group=None):
        current_time = pygame.time.get_ticks() # get time
        if current_time - self.laser_shot_time >= self.laser_cooldown:
            if self.character_type.startswith("enemy"):
                if target_player is None:
                    return
                laser = Laser(self, target_player, target_enemy_group)
            else:
                if target_enemy_group is None:
                    return
                laser = Laser(self, target_player, target_enemy_group)
                
            self.lasers.add(laser)
            self.laser_shot_time = current_time



    # ai check for collision of vision
    def ai_shoot(self, player, enemy_group):
        """Only enemy 3 can shoot this laser for now"""
        
        if self.character_type != "enemy3":
            return # only ai3 shoots
        
        # create a detection rect
        detection_rect = pygame.Rect(
            self.rect.centerx - 25, # offset x by 25 px to top
            self.rect.bottom,      # just below enemy / they are looking down from top screen
            30,                    # width of rect
            700                    # height
            
        )    
        # if player is inside detection rect zone
        if detection_rect.colliderect(player.rect): # check detection rect and player rect overlapping
            # Temporarily override cooldown ( 3 times slower than player)
            original_cooldown = self.laser_cooldown
            self.laser_cooldown = original_cooldown * 3
            
            # Shoot
            self.shoot_laser(
                target_player=player,
                target_enemy_group=enemy_group
            )
            
            # Restore original cooldown
            self.laser_cooldown = original_cooldown



    # update lasers fired by characters
    def update_lasers(self):
        for laser in self.lasers:
            laser.update()
            laser.draw()



    # check if player and ai is dead or alive
    def check_alive(self, player):
        
        if self.health <= 0:
            if self.alive: # we transition from alive to dead
                self.health = 0
                self.velocity = 0
                self.alive = False
                self.kill()