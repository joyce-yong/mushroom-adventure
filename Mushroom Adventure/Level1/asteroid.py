import pygame
import random
import config

class Asteroid(pygame.sprite.Sprite):
    def __init__(self, x, y, scale, health=20):
        super().__init__()
        
        # load random asteroid image
        rand = random.randint(1, 5)
        if rand == 1:
            img = pygame.image.load("img/asteroids/asteroid2.png").convert_alpha()
        elif rand == 2:
            img = pygame.image.load("img/asteroids/asteroid3.png").convert_alpha()
        elif rand == 3:
            img = pygame.image.load("img/asteroids/asteroid4.png").convert_alpha()
        elif rand == 4:
            img = pygame.image.load("img/asteroids/asteroid5.png").convert_alpha()
        else:
            img = pygame.image.load("img/asteroids/asteroid.png").convert_alpha()
            
        self.image = pygame.transform.scale(
            img, 
            (int(img.get_width() * scale),
            int(img.get_height() * scale)))
        self.rect = self.image.get_rect(center=(x,y))
        
        #movement
        self.velocity_y = random.randint(2, 5) # random y speed
        self.velocity_x = random.choice([-2, -1, 0, 1, 2]) # pick pseudo-random x direction
        
        # stats
        self.health = health
        self.max_health = health
        self.scale = scale
        
    def update(self, asteroid_group, player):
        
        #move asteroid
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        
        #Collision with player
        if self.rect.colliderect(player.rect):
            player.health -= 10
            self.kill()
            return
        
        #Check health
        if self.health <= 0:
            self.break_apart(asteroid_group, rocket_hit=False)
            
            
    
    
    #create break apart method
    def break_apart(self, asteroid_group, rocket_hit=False):
        
        config.channel_2.set_volume(0.8)
        config.channel_2.play(config.asteroid_fx)
        if rocket_hit: # rocket breaks it into smaller pieces
            new_scale = self.scale * 0.25
            num_pieces = 4
            new_health = max(5, self.max_health // 2)
        else:
            new_scale = self.scale * 0.5
            num_pieces = 2
            new_health = max(5, self.max_health // 2)
        
        #if very small 
        if new_scale < 0.1: # 1px
            self.kill()
            return
        
        #spawn fragments
        for _ in range(num_pieces):
            # create new asteroids in random x and y range of 40
            new_asteroid = Asteroid(
                self.rect.centerx + random.randint(-20, 20),
                self.rect.centery + random.randint(-20, 20),
                new_scale,
                health=new_health
            )
            asteroid_group.add(new_asteroid)
            
        self.kill()
        
        
    def draw(self, internal_surface):
        internal_surface.blit(self.image, self.rect)
        