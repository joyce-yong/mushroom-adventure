import pygame
import os

import config


class Laser(pygame.sprite.Sprite):
    def __init__(self, shooter, player, enemy_group, damage=10, velocity=12):
        super().__init__()
        self.shooter = shooter
        self.player = player
        self.enemy_group = enemy_group
        self.damage = damage
        self.velocity = velocity
        
        
        # load the image
        self.image = pygame.image.load("img/laser/laser.png").convert_alpha()
        
        # Dirtection and start Rect
        if shooter.character_type.startswith("enemy"):
            self.image = pygame.transform.flip(self.image, False, True) # Enemy shoots from top downs so need to flip in y
            self.direction = 1
            self.rect = self.image.get_rect(midtop=shooter.rect.midbottom)
        else:
            self.direction = -1 # player shoots up
            self.rect = self.image.get_rect(midbottom=shooter.rect.midtop)
            
            
    # laser update method
    def update(self):
        
        # move laser
        self.rect.y += self.velocity * self.direction
        
        # remove if laser goes of screen in y
        if self.rect.bottom < 0 or self.rect.top > config.SCREEN_HEIGHT:
            self.kill()
            return
        
        # Enemy shot laser: damage player
        if self.shooter.character_type.startswith("enemy"):
            if self.player and self.rect.colliderect(self.player.rect):
                if hasattr(self.player, "health"):
                    self.player.health -= self.damage
                self.kill()
                return
            
        else:
            # if player has shot
            for enemy in self.enemy_group:
                if self.rect.colliderect(enemy.rect):
                    if hasattr(enemy, "health"):
                        enemy.health -= self.damage
                    self.kill()
                    return
                
                
    # draw laser
    def draw(self):
        config.game_window.blit(self.image, self.rect)




class HeavyLaser(Laser):
    def __init__(self, shooter, player, enemy_group, damage=50, velocity=8, image_path="img/heavyLaser/heavylaser.png", size=(18,45)):
        
        # initialize base laser class 
        super().__init__(shooter, player, enemy_group, damage=damage, velocity=velocity)
        
        # OVERRIDE DAMAGE AND SPEED FOR ENEMIES
        if shooter.character_type.startswith("enemy"):
            self.damage = 10 # enemy does 10% health damage or shield damage
            self.velocity = 4
        else:
            self.damage = damage # keep default damage for player
            self.velocity = 14
            
        # load images and scale heavy laser
        img = pygame.image.load(image_path).convert_alpha()
        img = pygame.transform.scale(img, size)
        
        if shooter.character_type.startswith("enemy"):
            img = pygame.transform.flip(img, False, True) # enemy looks down so we flip laser
            self.rect = img.get_rect(midtop=shooter.rect.midbottom)
            self.direction = 1 # facing towards screen bottom
        else:
            self.rect = img.get_rect(midbottom=shooter.rect.midtop)
            self.direction = -1 # facing top screen
            
        self.image = img




# rocket class

class Rocket(pygame.sprite.Sprite):
    def __init__(self, shooter, target_group):
        super().__init__()
        self.shooter = shooter
        self.rocket_images = []
        self.explosion_images = []
        # state
        self.exploding = False
        self.frame_index = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 100 # ms per frame
        
        # References
        self.target_group = target_group
        
        # __load rocket images __
        for filename in sorted(os.listdir("img/rocket")):
            img = pygame.image.load(os.path.join("img/rocket", filename)).convert_alpha()
            img = pygame.transform.scale(img, (20, 50)) # scale the rocket down smaller
            # flip rocket for enemies
            if shooter.character_type.startswith("enemy"):
                img = pygame.transform.flip(img, False, True)
            self.rocket_images.append(img)
            
        # load explosion frames 
        for filename in sorted(os.listdir("img/explosion")):
            img = pygame.image.load(os.path.join("img/explosion", filename)).convert_alpha()
            self.explosion_images.append(img)
            
        # starts with rocket sprite
        self.image = self.rocket_images[0]
        self.rect = self.image.get_rect(center=shooter.rect.center)
        
        # direction enemy or player +/-
        if shooter.character_type.startswith("enemy"):
            self.velocity = 4 # move for down the screen
        else: # player
            self.velocity = -12 # move up the screen
            
            
    # update method
    def update(self):
        if not self.exploding:
            # Move
            self.rect.y += self.velocity
            
            # ___ Animate Rocket ___
            current_time = pygame.time.get_ticks() # track time
            if current_time - self.last_update > self.frame_rate:
                self.last_update = current_time
                self.frame_index = (self.frame_index + 1) % len(self.rocket_images)
                self.image = self.rocket_images[self.frame_index]
                
            # ___ Detection Area ___
            if self.shooter.character_type.startswith("enemy"):
                detection_area = pygame.Rect( # create rectangle
                    self.rect.centerx - 50,
                    self.rect.centery - 50,
                    80, # rocket expmx area
                    30   # rocket exp y area       
                    
                )
            else:  # player rocket
                detection_area = pygame.Rect(
                self.rect.centerx - 50,
                self.rect.centery - 50,
                100,
                40
                )
                
            
            hit_something = False
            
            # ___ Check for enemies or player (ignore the shooter itself)
            for target in self.target_group:
                if target is self.shooter:
                    continue
                if detection_area.colliderect(target.rect):
                    if hasattr(target, "health"):
                        if self.shooter.character_type.startswith("enemy"):
                            target.health -= 50 # from player health
                        else: # player
                            target.health -= 150 # from enemy health
                    hit_something = True
                    
                    
            # Trigger explosion
            if hit_something:
                self.exploding = True # set explosion state
                self.frame_index = 0 # start from first image
                self.image = self.explosion_images[self.frame_index]
                self.rect = self.image.get_rect(center=self.rect.center)
                
            
            # _ Kill rocket off screen _
            if self.rect.bottom < 0 or self.rect.top > config.SCREEN_HEIGHT:
                self.kill() # remove object instance
                
        else:
            # __ Explosion Animation __
            current_time = pygame.time.get_ticks()
            if current_time - self.last_update > self.frame_rate:
                self.last_update = current_time
                self.frame_index += 1
                if self.frame_index < len(self.explosion_images):
                    self.image = self.explosion_images[self.frame_index]
                    self.rect = self.image.get_rect(center=self.rect.center)
                else:
                    self.kill()
                    
                    
    def draw(self):
        config.game_window.blit(self.image, self.rect) 