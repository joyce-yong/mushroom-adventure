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
        self.shield = 200

        if self.character_type == "player":
            self.health = 200
        if self.character_type == "enemy4":
            self.health = 200
        if self.character_type == "enemy5":
            self.health = 600
        

        self.max_health = self.health # set max health to normal health for overflow
        self.max_shield = self.shield # set max shield to prevent shield from overflowing
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

        # shield hit
        self.prev_shield = self.shield
        self.shield_time = 100 # ms / total shield duration in (ms per frame)
        self.shield_start = 0
        self.shield_original_image = self.image.copy()

        # ___ load flash images  ___
        self.flash_images = []
        for i in range(2): # flash 2 images in folder
            img = pygame.image.load(f'img/{self.character_type}/damage/{i}.png').convert_alpha()
            img = pygame.transform.scale(img, (self.rect.width, self.rect.height))
            self.flash_images.append(img)
            
        self.flash_index = 0

        # ___ Load shield images ___
        self.shield_images = []
        for i in range(2): # 2 pictures to loop
            img = pygame.image.load(f'img/{self.character_type}/shield/{i}.png').convert_alpha()
            img = pygame.transform.scale(img, (self.rect.width, self.rect.height))
            self.shield_images.append(img)
        
        self.shield_index = 0

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
        
    


    # check if player and ai is dead or alive
    def check_alive(self, player):
        
        if self.health <= 0:
            if self.alive: # we transition from alive to dead
                self.health = 0
                self.velocity = 0
                self.alive = False
                self.kill()

                reward = config.enemy_rewards.get(self.character_type, {'score': 70,'shield': 30, 'health':0})
                config.score += reward['score']
                
                # bonuses
                player.shield += reward.get('shield', 0)
                player.health += reward.get('health', 0)
                
                # clamp values added
                player.shield = min(player.shield, player.max_shield)
                player.health = min(player.health, player.max_health)



    # flash damage when hit
    def damage_flash(self):
        # check if currently flashing
        elapsed = pygame.time.get_ticks() - self.flash_start
        flashing = elapsed < self.flash_time * len(self.flash_images)
        
        # only restart flash if health decreased and not already flashing
        if self.health < self.prev_health and not flashing:
            self.flash_start = pygame.time.get_ticks()
            
        self.prev_health = self.health # check for new health as this one to be compared for damage

        # __ shield falshing __
        elapsed_shield = pygame.time.get_ticks() - self.shield_start
        shield_flashing = elapsed_shield < self.shield_time * len(self.shield_images)
        
        if self.shield < self.prev_shield and not shield_flashing:
            config.channel_9.set_volume(0.6)
            config.channel_9.play(config.shield_fx)
            self.shield_start = pygame.time.get_ticks()
        self.prev_shield = self.shield

        # change what to show/ armor/shield damage
        
        # Hanlde flashing/shield animation
        if flashing:
            frame = (elapsed // self.flash_time) % len(self.flash_images)
            self.image = self.flash_images[frame]
        elif shield_flashing:
            frame = (elapsed_shield // self.shield_time) % len(self.shield_images)
            self.image = self.shield_images[frame]
        else: # no damage taken
            self.image = self.original_image







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


        # end of movement method 






    # AI enemies 
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
    def shoot_laser(self, target_player=None, target_enemy_group=None, asteroid_group=None):
        current_time = pygame.time.get_ticks() # get time
        if current_time - self.laser_shot_time >= self.laser_cooldown:
            if self.character_type.startswith("enemy"):
                if target_player is None:
                    return
                laser = Laser(self, target_player, target_enemy_group, asteroid_group)
            else:
                if target_enemy_group is None:
                    return
                laser = Laser(self, target_player, target_enemy_group, asteroid_group)
                
            self.lasers.add(laser)
            self.laser_shot_time = current_time

            config.laser_fx.play()



    # ai check for collision of vision
    def ai_shoot(self, player, enemy_group, asteroid_group):
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
                target_enemy_group=enemy_group,
                asteroid_group=asteroid_group
            )
            
            # Restore original cooldown
            self.laser_cooldown = original_cooldown



    # update lasers fired by characters
    def update_lasers(self):
        for laser in self.lasers:
            laser.update()
            laser.draw()



    # ____ Heavy laser ____

    def shoot_heavy(self, target_player=None, target_enemy_group=None, asteroid_group=None):
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
            heavy = HeavyLaser(self, target_player, target_enemy_group, asteroid_group)  
        else: # player
            if target_enemy_group is None: # if no target for player skip
                return 
            heavy = HeavyLaser(self, target_player, target_enemy_group, asteroid_group)  
            
        self.lasers.add(heavy)
        self.last_heavy_shot = now

        config.channel_3.set_volume(0.3)
        config.channel_3.play(config.heavyLaser_fx)
    

    # ai heavy shot
    def ai_shoot_heavy(self, player, enemy_group, asteroid_group):
        
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
        cooldown = 700
        
        if now - getattr(self, "last_heavy_shot", 0) >= cooldown:
            # call shared heavy shooting method
            self.shoot_heavy(
                target_player=player,
                target_enemy_group=enemy_group,
                asteroid_group=asteroid_group
                )    
            self.last_heavy_shot = now




    # rocket check
    def shoot_rocket(self, target_group, rocket_group, asteroid_group):
        current_time = pygame.time.get_ticks()
        
        # Enemy shoots at 1/3 the speed
        cooldown = self.rocket_cooldown
        if self.character_type == "enemy2":
            cooldown *= 3
            
        if current_time - self.last_rocket_time >= cooldown:
            rocket = Rocket(self, target_group, asteroid_group)
            rocket_group.add(rocket)
            self.last_rocket_time = current_time

            config.channel_4.play(config.rockets_fx)




    # ai shoots
    def ai_shoot_rocket(self, player, rocket_group, asteroid_group):
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
                    rocket_group,
                    asteroid_group
                )
                self.last_rocket_time = current_time





    def ai_shoot_enemy5(self, player, enemy_group, asteroid_group):
        from projectiles import HeavyLaser
        
        # if not enemy 5 skip
        if self.character_type != "enemy5":
            return
                
        # give 1 second delay before firing
        if pygame.time.get_ticks() - self.spawn_time < 1000:
            return
        
        # detection rectangle
        detection_rect = pygame.Rect(
            self.rect.left -100,
            self.rect.top,
            self.rect.width + 100, # size of rect + 100px
            700
        )

        if not detection_rect.colliderect(player.rect):
            return # if not colliding rect vision with player rect
        
        now = pygame.time.get_ticks()
        
        # fire normal lasers
        if now - getattr(self, "last_shot_time", 0) >= self.laser_cooldown:
            left_pos = (self.rect.centerx - 10, self.rect.bottom - 25)
            right_pos = (self.rect.centerx + 10, self.rect.bottom - 25)
            for pos in [left_pos, right_pos]:
                laser = Laser(self, player, enemy_group, asteroid_group)
                laser.rect.midtop = pos
                laser.prev_center = pygame.math.Vector2(laser.rect.center)
                self.lasers.add(laser)
            self.last_shot_time = now # assign time to reset check to current time 
            config.laser_fx.play() # play over this sound this way

            
        # Heavy lasers
        if now - getattr(self, "last_heavy_shot", 0) >= self.heavy_cooldown:
            offset_y = 40
            offset_x = 20
            top_left_pos = (self.rect.left + offset_x, self.rect.top + offset_y) 
            top_right_pos = (self.rect.right - offset_x, self.rect.top + offset_y)
            for pos in [top_left_pos, top_right_pos]:
                heavy = HeavyLaser(self, player, enemy_group, asteroid_group)
                heavy.rect.midtop = pos
                heavy.prev_center = pygame.math.Vector2(heavy.rect.center)
                self.lasers.add(heavy)
                
            self.last_heavy_shot = now # reset time counter
            config.channel_3.play(config.heavyLaser_fx)



    # laser rapid fire for enemy method
    def ai_shoot_laserline(self, player, asteroid_group=None, laserline_group=None):
        from projectiles import LaserLine
        """
        Enemy 4 for now can only shoot laserline and the player to 
        Only create one laserline and keep updating those object
        """
        # check if enemy object is enemy 4
        if self.character_type != "enemy4":
            return # skip logic if not enemy 4
        
        # Remove existing laser line if enemy is dead
        if not self.alive and laserline_group is not None: # if enemy has died and there is a laserline object so not of type None
            for line in list(laserline_group):
                if getattr(line, "character", None) == self:
                    line.trigger(False)
                    line.kill() # remove group
                    
            # make sure sound stops when enemy is dead
            if config.channel_8.get_busy():
                config.channel_8.stop()
            return
        
        # detection area
        detection_rect = pygame.Rect(
            self.rect.centerx -50,
            self.rect.bottom,
            100,
            730
        )
        
        # if player is in detection rect zone so colliding
        if detection_rect.colliderect(player.rect):
            existing_line = None
            if laserline_group is not None: # if laserLine group object is there 
                for line in laserline_group:
                    if getattr(line, "character", None) == self:
                        existing_line = line
                        break
            
            # create if one does not exists
            if existing_line is None:
                 enemy_line = LaserLine(self, is_player=False)
                 laserline_group.add(enemy_line)
                 existing_line = enemy_line
                 
            # Trigger fire while player is in range
            existing_line.trigger(True)
        
        else: # if player is not in the detection zone
            # stop firing
            if laserline_group is not None:
                for line in laserline_group:
                    if getattr(line, "character", None) == self:
                        line.trigger(False)


    


class HealthBar():
    
    def __init__(self, healthBar_x, healthBar_y, health, max_health):
        self.healthBar_x = healthBar_x
        self.healthBar_y = healthBar_y
        self.health = health
        self.max_health = health
        
    def draw(self, health):
        
        from config import game_window, BLACK, CAYAN, WHITE
        self.health = health
        # calculate health ratio
        ratio = self.health / self.max_health
        pygame.draw.rect(game_window, BLACK, (self.healthBar_x -2, self.healthBar_y -2, 274, 9))
        pygame.draw.rect(game_window, WHITE, (self.healthBar_x, self.healthBar_y, 270, 6))
        pygame.draw.rect(game_window, CAYAN, (self.healthBar_x, self.healthBar_y, 270 * ratio, 6))