import pygame # type: ignore
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





# _____ Black hole / quark star ____
class BlackHole(pygame.sprite.Sprite):
    """ - Spinning dense stars blackhole/quarkStar
        - These dense stars must have rotation and spin
        - Gravity pull effect 
        - When enemy or player enters close to center of object we kill it (fallen in)
        - when objects get closer the scale down and are pulled stronger each pixel they are closer to center
    """
    # globals
    PLAYER_ATTRACCTION_RANGE = 110
    PLAYER_ATTRACCTION_STRENGTH = 1.5 # multiplies distance
    AI_ATTRACTION_RANGE = 260
    AI_ATTRACTION_STRENGTH = 0.001
    ASTEROID_ATTRACTION_RANGE = 290
    ASTEROID_ATTRACTION_STRENGTH = 0.005
    
    CENTER_KILL_DISTANCE = 2
    MIN_SCALE = 0.05
    ASTEROID_SCALE = 0.95
    
    def __init__(self, x=None, y=None, initial_size=160, rotation_speed=0.15, frame_rate_ms=100):
        super().__init__()
        
        self.last_break_time = 0 # track cooldown
        self.break_cooldown = 50.0
        
        # quark neutron star
        self.quark_star = False
        self.quark_chance = random.randint(1, 3) # 3 times less chance than blackhole
        if self.quark_chance == 1:
            self.quark_star = True
            
        # -- load frames from folder, create exception
        self.frames = []
        folder = "img/quarkstar" if self.quark_star else "img/blackhole" 
        if os.path.isdir(folder):
            files = sorted([f for f in os.listdir(folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
            for f in files:
                try:
                    img = pygame.image.load(os.path.join(folder, f)).convert_alpha()
                    img = pygame.transform.scale(img, (initial_size, initial_size))
                    self.frames.append(img)
                except Exception:
                    pass
                
        if not self.frames: # if no image load one image as default
            try:
                img = pygame.image.load("img/blackhole/0.png").convert_alpha() # load basic static image
                img = pygame.transform.scale(img, (initial_size, initial_size))
                self.frames = [img]
            except Exception:
                # if still no image 0 first one in blackhole folder we create blank alpha
                blank_alpha = pygame.Surface((initial_size , initial_size), pygame.SRCALPHA)
                self.frames = [blank_alpha]
                
        
        # animation state
        self.frame_index = 0
        if self.quark_star:
            self.frame_rate_ms = 20 # quark star has a faster animation for spin effect
        else:
            self.frame_rate_ms = frame_rate_ms
        self.last_frame_time = pygame.time.get_ticks() # keep track of time for animation
        
        # start with base frame
        self.base_frame = self.frames[self.frame_index]
        self.image = self.base_frame.copy() # create a copy of original image
        self.rect = self.image.get_rect()
        
        # spawn off top of the screen by defualt
        if x is None:
            x = random.randint(50, config.SCREEN_WIDTH - 50)
        if y is None:
            y = -50 # 50 px off screen
        self.rect.center = (x,y)
        self.bh_pos = pygame.math.Vector2(self.rect.center)
        
        # movement : mimic the same effect as asteroid drift
        self.velocity_y = float(random.randint(1,4))
        self.velocity_x = float(random.choice([-2, -1, 0, 1, 2]))
        # rotation
        self.angle = 0.0
        self.rotation_speed = rotation_speed
        # center vector (update each frame)
        self.center = pygame.math.Vector2(self.rect.center)
        
    def advance_frame(self):
        now = pygame.time.get_ticks()
        if now - self.last_frame_time >= self.frame_rate_ms:
            self.last_frame_time = now
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.base_frame = self.frames[self.frame_index]
            
    
    def update(self, groups_map=None):
        # animate frames
        self.advance_frame()
        
        # rotate chosen frame and preserve center
        self.angle = (self.angle + self.rotation_speed) % 360 # full circle
        old_center = self.rect.center
        rotated = pygame.transform.rotate(self.base_frame, self.angle)
        self.image = rotated
        self.rect = self.image.get_rect(center=old_center)
        
        # move down and drift using those float positions
        self.bh_pos.x += self.velocity_x
        self.bh_pos.y += self.velocity_y
        self.rect.center = (int(self.bh_pos.x), int(self.bh_pos.y))
        self.center = (pygame.math.Vector2(self.rect.center))
        
        
        # kill object if it is off screen
        if (self.rect.top > config.SCREEN_HEIGHT * 1.3 or
            self.rect.right < -300 or 
            self.rect.left > config.SCREEN_WIDTH * 1.1):
            try:
                self.kill()
            except Exception:
                pass
                print("Could not kill heavy mass star")
            return

        # apply attraction to groups if provided
        if groups_map:
            player = groups_map.get('player')
            if player:
                self.apply_to_sprite(player)
            
            
            for key in ('enemy_group', 'asteroids', 'player_lasers', 'enemy_lasers', 'rockets_group'):
                group = groups_map.get(key)
                if group:
                    for spr in list(group):
                        self.apply_to_sprite(spr)
                        
                        
    def in_attraction_range(self, sprite):
        sprite_x, sprite_y = sprite.rect.center
        dx = self.center.x - sprite_x
        dy = self.center.y - sprite_y
        
        char_type = getattr(sprite, 'character_type', None) 
        
        
        if char_type == 'player':
            range_limit = self.PLAYER_ATTRACCTION_RANGE
        elif char_type == 'asteroid':
            range_limit = self.ASTEROID_ATTRACTION_RANGE
        else:
            range_limit = self.AI_ATTRACTION_RANGE
            
        return (abs(dx) <= range_limit) and (abs(dy) <= range_limit)
                
                
    def apply_to_sprite(self, sprite, group=None):
        
        # enemy 8 has anti black hole tech so we skip it
        if getattr(sprite, 'character_type', None) == 'enemy8':
            return # skip logic for enemy 8
        
        # ignore dead sprites 
        if hasattr(sprite, 'alive') and not sprite.alive:
            return
        
        # apply attraction to correct groups
        if not self.in_attraction_range(sprite):
            return
        
        # ensure float position exists 
        if not hasattr(sprite, 'bh_pos'):
            sprite.bh_pos = pygame.math.Vector2(sprite.rect.center)
            
        
            
        spr_center = pygame.math.Vector2(sprite.bh_pos)
        vector = self.center - spr_center
        distance = vector.length()
        
        # create fall in kill zone
        if distance <= self.CENTER_KILL_DISTANCE:
            if getattr(sprite, 'character_type', None) == 'player':
                # instantly kill player when sucked into blackhole
                sprite.health = 0
                sprite.alive = False
                print("Player sucked into blackhole")
            else:
                # for enemies and other sprites, use normal kill
                try:
                    sprite.kill()
                except Exception:
                    pass
                    print("Blackhole: Could not kill target")
            return
        
        # Attraction strength
        char_type = getattr(sprite, 'character_type', None)
        if char_type == 'player':
            strength_multiplier = 1.8 # strong player attraction
            range_limit = self.PLAYER_ATTRACCTION_RANGE
        elif char_type == 'asteroid':
            strength_multiplier = 0.04
            range_limit = self.ASTEROID_ATTRACTION_RANGE
        else:
            strength_multiplier = 0.02
            range_limit = self.AI_ATTRACTION_RANGE
            
        # apply gravity pull
        pull_strength = max(2.5, min(13.0, distance * strength_multiplier))
        move_vector = vector.normalize() * pull_strength if distance != 0 else pygame.math.Vector2(0, 0)
        sprite.bh_pos += move_vector
        sprite.rect.center = (int(sprite.bh_pos.x), int(sprite.bh_pos.y))
        
        # scaling for time and space warp
        rel = min(1.0, distance / float(range_limit))
        shrink_factor = max(self.ASTEROID_SCALE, rel) if char_type == 'asteroid' else max(self.MIN_SCALE, rel)
        try:
            base_img = getattr(sprite, 'original_image', sprite.image)
            current_w, current_h = base_img.get_size()
            target_w = max(2, int(current_w * shrink_factor))
            target_h = max(2, int(current_h * shrink_factor))
            if target_w < current_w or target_h < current_h:
                old_center = sprite.rect.center
                sprite.image = pygame.transform.smoothscale(base_img, (target_w, target_h))
                sprite.rect = sprite.image.get_rect(center=old_center)
                
        except Exception:
            pass
        
        
        
        
        
    def draw(self, surface):
        surface.blit(self.image, self.rect)