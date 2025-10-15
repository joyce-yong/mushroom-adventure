import pygame
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