import pygame
import config

from projectiles import Laser, Rocket

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
        self.laser_cooldown = 100 # milliseconds
        self.laser_shot_time = 0

        # heavy lasers
        self.heavy_cooldown = 300
        self.last_heavy_shot = 0
        

        # flash hit
        self.prev_health = self.health
        self.flash_time = 100 # in ms
        self.flash_start = 0
        self.original_image = self.image.copy()

        # ___ load flash images  ___
        self.flash_images = []
        for i in range(2): # flash 2 images in folder
            img = pygame.image.load(f'img/{self.character_type}/damage/{i}.png').convert_alpha()
            img = pygame.transform.scale(img, (self.rect.width, self.rect.height))
            self.flash_images.append(img)
            
        self.flash_index = 0

        # rockets
        self.last_rocket_time = 0
        self.rocket_cooldown = 1000






    # create custom draw method for characters
    def draw(self):
        config.game_window.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
        
        
    # update character class objects
    def update(self, player):
        self.check_alive(player)
        self.damage_flash()  
        
       





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
                
                

    ##### basic laser #####

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



    # ____ Heavy laser ____

    def shoot_heavy(self, target_player=None, target_enemy_group=None):
        from projectiles import HeavyLaser
        
        """Fire heavy lasers """ 
        now = pygame.time.get_ticks()
        if now - getattr(self, "last_heavy_shot", 0) < self.heavy_cooldown:
            return
        
        # create heavy laser
        if self.character_type.startswith("enemy"):
            # force enemy to get target or skip logic
            if target_player is None:
                return
            heavy = HeavyLaser(self, target_player, target_enemy_group)  
        else: # player
            if target_enemy_group is None: # if no target for player skip
                return 
            heavy = HeavyLaser(self, target_player, target_enemy_group)  
            
        self.lasers.add(heavy)
        self.last_heavy_shot = now
    

    # ai heavy shot
    def ai_shoot_heavy(self, player, enemy_group):
        
        if self.character_type != "enemy1":
            return
        
        
        detection_rect = pygame.Rect(
            self.rect.centerx - 25, # offset x by 25 px to left so we center based on our picture 
            self.rect.bottom,      # just below enemy / they are looking down from top screen
            40,                    # width of rect
            720                    # height
            
        )  
        if not detection_rect.colliderect(player.rect): # if we do not collide with player we skip
            return
        
        now = pygame.time.get_ticks()
        cooldown = 1000 # 1 second
        
        if now - getattr(self, "last_heavy_shot", 0) >= cooldown:
            # call shared heavy shooting method
            self.shoot_heavy(
                target_player=player,
                target_enemy_group=enemy_group,
                )    
            self.last_heavy_shot = now




    # rocket check
    def shoot_rocket(self, target_group, rocket_group):
        current_time = pygame.time.get_ticks()
        
        # Enemy shoots at 1/3 the speed
        cooldown = self.rocket_cooldown
        if self.character_type == "enemy2":
            cooldown *= 3
            
        if current_time - self.last_rocket_time >= cooldown:
            rocket = Rocket(self, target_group)
            rocket_group.add(rocket)
            self.last_rocket_time = current_time




    # ai shoots
    def ai_shoot_rocket(self, player, rocket_group):
        """Only enemy 2 can shoot rockets"""
        if self.character_type not in "enemy2":
            return
        
        # detection area rectangle
        detection_rect = pygame.Rect(
            self.rect.centerx - 25, # check image and center in x  -25px (left)
            self.rect.bottom,
            50,
            760
        )            

        # fire only if player is in detection range 
        if detection_rect.colliderect(player.rect):
            current_time = pygame.time.get_ticks()
            
            # diffrent cooldown types
            if self.character_type == "enemy2":
                rocket_cooldown = 3000 # 3 sec
            else: # other enemies
                rocket_cooldown = 2000 # 2 sec 1 faster  
                
            if current_time - getattr(self, "last_rocket_time", 0) >= rocket_cooldown:
                self.shoot_rocket(
                    pygame.sprite.Group([player]),
                    rocket_group
                )
                self.last_rocket_time = current_time


























    # check if player and ai is dead or alive
    def check_alive(self, player):
        
        if self.health <= 0:
            if self.alive: # we transition from alive to dead
                self.health = 0
                self.velocity = 0
                self.alive = False
                self.kill()


    # flash damage when hit
    def damage_flash(self):
        # check if currently flashing
        elapsed = pygame.time.get_ticks() - self.flash_start
        flashing = elapsed < self.flash_time * len(self.flash_images)
        
        # only restart flash if health decreased and not already flashing
        if self.health < self.prev_health and not flashing:
            self.flash_start = pygame.time.get_ticks()
            
        self.prev_health = self.health # check for new health as this one to be compared for damage
        
        # Hanlde flashing animation
        if flashing:
            frame = (elapsed // self.flash_time) % len(self.flash_images)
            self.image = self.flash_images[frame]
        else:
            self.image = self.original_image