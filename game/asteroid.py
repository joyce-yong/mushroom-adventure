import pygame
import random, os
import config

class Asteroid(pygame.sprite.Sprite):
    def __init__(self, x, y, scale, health=20, is_fragment=False, ice=None, junk=None, fragment_count=1):
        super().__init__()
        """ - x, y spawn position for object
            - scale: size of multiplier
            - health: damage object can take before breaking
            - is_fragment: if True so we track same object types objects break into their types
            - ice: force ice type fragments
            - junk: force junk fragments
        """
        self.character_type = "asteroid" # use to check if it is our object asteroid/comet/junk
        # load random asteroid image
        
        # check object types ice, junk, rock
        if junk is None and not is_fragment:
            junk = random.randint(1, 3) == 1
        self.space_junk = junk
        # if ice type chance 
        # ice has a higher chance then junk even with the same (1,3), because code is executed top down so if both are true in same case ice gets created over junk
        if ice is None and not is_fragment:
            ice = random.randint(1, 3) == 1  
        self.ice = ice
        
        folder = "img/spaceJunk" if self.space_junk else "img/ice" if self.ice else "img/asteroids"
        files = sorted([f for f in os.listdir(folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
        
        if not files:
            s = pygame.Surface((100, 100). pygame.SRCALPHA)
            img = s
        else:
            img_path = os.path.join(folder, random.choice(files))
            img = pygame.image.load(img_path).convert_alpha()
            
        self.image = pygame.transform.scale(
            img, (int(img.get_width() * scale), int(img.get_height() * scale))
        )
        self.rect = self.image.get_rect(center=(x, y))
        
        
        # movement
        self.velocity_y = random.randint(2, 5) # random y speed
        self.velocity_x = random.choice([-2, -1, 0, 1, 2]) # pick pseudo-random x direction
        
        # stats
        self.health = health
        self.max_health = health
        self.scale = scale
        
        # fragment damge
        self.fragment_count = fragment_count
        self.base_damage = 80
        self.damage = int(self.base_damage/ fragment_count)
        
    def update(self, asteroid_group, player):
        
        # move asteroid
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        
        # Collision with player
        if self.rect.colliderect(player.rect):

            if player.shield > 0:
                player.shield -= self.damage
            else:
                player.health -= self.damage
            self.kill()
            print("Health: ", player.health, ", Shield: ", player.shield )
            return
        
        # Check health
        if self.health <= 0:
            self.break_apart(asteroid_group, rocket_hit=False)
            # add points to score 
            config.score += 10

        # kill object off screen to save memory and computation
        if (self.rect.top > config.SCREEN_HEIGHT or
            self.rect.right < -1000 or
            self.rect.left > config.SCREEN_WIDTH):
            self.kill()
            return
            
            
    
    
    # create break apart method
    def break_apart(self, asteroid_group, rocket_hit=False):

        config.channel_2.set_volume(0.8)
        config.channel_2.play(config.asteroid_fx)
        if rocket_hit: # rocket breaks it into smaller pieces
            new_scale = self.scale * 0.125
            num_pieces = 8
            new_health = max(5, self.max_health // 4)
        else:
            new_scale = self.scale * 0.5
            num_pieces = 2
            new_health = max(5, self.max_health // 2)
        
        # if very small 
        if new_scale < 0.1: # 1px
            self.kill()
            return
        
        folder = "img/spaceJunk" if self.space_junk else "img/ice" if self.ice else "img/asteroids"
        files = sorted([f for f in os.listdir(folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
        
        # spawn fragments
        for _ in range(num_pieces):
            if files:
                img_path = os.path.join(folder, random.choice(files))
            else:
                img_path = None
            # create new asteroids in random x and y range of 40
            new_asteroid = Asteroid(
                self.rect.centerx + random.randint(-20, 20),
                self.rect.centery + random.randint(-20, 20),
                new_scale,
                health=new_health,
                is_fragment=True,
                ice=self.ice,
                junk=self.space_junk,
                fragment_count=num_pieces * self.fragment_count # track total division
            )
            asteroid_group.add(new_asteroid)
            
        self.kill()
        
        
    def draw(self, internal_surface):
        internal_surface.blit(self.image, self.rect)
        