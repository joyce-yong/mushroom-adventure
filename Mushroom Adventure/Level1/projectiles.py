import pygame
import os, random

import config
import sprite_groups


class Laser(pygame.sprite.Sprite):
    def __init__(self, shooter, player, enemy_group, asteroid_group, damage=10, velocity=12):
        super().__init__()
        self.shooter = shooter
        self.player = player
        self.enemy_group = enemy_group
        self.damage = damage
        self.velocity = velocity
        self.asteroid_group = asteroid_group

        # load the image
        self.image = pygame.image.load("img/laser/laser.png").convert_alpha()

        # Dirtection and start Rect
        if shooter.character_type.startswith("enemy"):
            self.image = pygame.transform.flip(self.image, False,
                                               True)  # Enemy shoots from top downs so we need to flip in y
            self.direction = 1
            self.rect = self.image.get_rect(midtop=shooter.rect.midbottom)
        else:
            self.direction = -1  # player shoots up
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

            # asteroid hit
            for asteroid in self.asteroid_group:
                if self.rect.colliderect(asteroid.rect):
                    asteroid.health -= self.damage
                    self.kill()
                    return

    # draw laser
    def draw(self):
        config.game_window.blit(self.image, self.rect)


class HeavyLaser(Laser):
    def __init__(self, shooter, player, enemy_group, asteroid_group, damage=50, velocity=8,
                 image_path="img/heavyLaser/heavylaser.png", size=(18, 45)):

        # initialize base laser class
        super().__init__(shooter, player, enemy_group, asteroid_group, damage=damage, velocity=velocity)

        # OVERRIDE DAMAGE AND SPEED FOR ENEMIES
        if shooter.character_type.startswith("enemy"):
            self.damage = 10  # enemy does 10% health damage or shield damage
            self.velocity = 6
        else:
            self.damage = damage  # keep default damage for player
            self.velocity = 14

        # load images and scale heavy laser
        img = pygame.image.load(image_path).convert_alpha()
        img = pygame.transform.scale(img, size)

        if shooter.character_type.startswith("enemy"):
            img = pygame.transform.flip(img, False, True)  # enemy looks down so we flip laser
            self.rect = img.get_rect(midtop=shooter.rect.midbottom)
            self.direction = 1  # facing towards screen bottom
        else:
            self.rect = img.get_rect(midbottom=shooter.rect.midtop)
            self.direction = -1  # facing top screen

        self.image = img


# rocket class

class Rocket(pygame.sprite.Sprite):
    def __init__(self, shooter, target_group, asteroid_group):
        super().__init__()
        self.shooter = shooter
        self.rocket_images = []
        self.explosion_images = []
        # state
        self.exploding = False
        self.frame_index = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 100  # ms per frame

        # References
        self.target_group = target_group
        self.asteroid_group = asteroid_group

        # __load rocket images __
        for filename in sorted(os.listdir("img/rocket")):
            img = pygame.image.load(os.path.join("img/rocket", filename)).convert_alpha()
            img = pygame.transform.scale(img, (20, 50))  # scale the rocket down smaller
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
            self.velocity = 4  # move for down the screen
        else:  # player
            self.velocity = -12  # move up the screen

    # update method
    def update(self):
        if not self.exploding:
            # Move
            self.rect.y += self.velocity

            # ___ Animate Rocket ___
            current_time = pygame.time.get_ticks()  # track time
            if current_time - self.last_update > self.frame_rate:
                self.last_update = current_time
                self.frame_index = (self.frame_index + 1) % len(self.rocket_images)
                self.image = self.rocket_images[self.frame_index]

            # ___ Detection Area ___
            if self.shooter.character_type.startswith("enemy"):
                detection_area = pygame.Rect(  # create rectangle
                    self.rect.centerx - 50,
                    self.rect.centery - 50,
                    80,  # rocket expmx area
                    30  # rocket exp y area

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
                            target.health -= 50  ## from player health
                        else:  # player
                            target.health -= 150  # from enemy health
                    hit_something = True

            for asteroid in list(self.asteroid_group):
                if hasattr(asteroid, "rect") and detection_area.colliderect(asteroid.rect):
                    asteroid.health -= 100
                    asteroid.break_apart(self.asteroid_group, rocket_hit=True)

            # Trigger explosion
            if hit_something:
                self.exploding = True  # set explosion state
                self.frame_index = 0  # start from first image
                self.image = self.explosion_images[self.frame_index]
                self.rect = self.image.get_rect(center=self.rect.center)
                config.channel_5.set_volume(0.8)
                config.channel_5.play(config.explode_fx)

            # _ Kill rocket off screen _
            if self.rect.bottom < 0 or self.rect.top > config.SCREEN_HEIGHT:
                self.kill()  # remove object instance

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

    # ___ laser line class ___


class LaserLine(pygame.sprite.Sprite):
    def __init__(self, ship, is_player=True):
        super().__init__()
        self.ship = ship
        self.is_player = is_player
        self.segments = []  # have a list of segments, [x, y , lenght , colour]
        self.active = False
        self.width = 2
        self.speed = 35  # high speed
        self.color_player = [(0, 255, 255), (255, 255, 255), (255, 0, 0)]  # cayan, white, red
        self.color_ai = [(255, 0, 0), (25, 25, 0), (255, 255, 0)]  # red, dark yellow/red , yellow
        self.line_rect = pygame.Rect(0, 0, 0, 0)

        # Fuel system
        self.fuel = 100
        self.max_fuel = self.fuel  # keep track of our fuel limit
        self.last_fuel_update = pygame.time.get_ticks()  # keep track of time
        self.fuel_drain_per_sec = 20  # more than recharge
        self.fuel_recharge_per_sec = 10  # half the drain rate

        # keep track of our sound (rapid fire can cause sound issues if not tracked)
        self.last_shot_sound = 0
        self.shot_sound_delay = 100  # 100 ms between bursts (10 per 1 second)

    # method to check if we are trigger this rapid fire laserLine
    def trigger(self, active):
        self.active = active and self.fuel > 0  # we must have fuel

    # update method
    def update(self, asteroid_group, enemy_group, player):
        # track time in now
        now = pygame.time.get_ticks()
        delta = (now - self.last_fuel_update) / 1000
        self.last_fuel_update = now  # reset time to start tracking event(next) again

        # play fx
        channel_sound = config.channel_8 if self.is_player else config.channel_9

        # stop if the ship is dead
        if not self.ship.alive:
            self.active = False
            if channel_sound.get_busy():
                channel_sound.stop()
            return  # don’t continue update if ship object is dead

        # FUel drain/recharge
        if self.active and self.fuel > 0:  # drain fuel when active
            self.fuel -= self.fuel_drain_per_sec * delta
            if self.fuel > 0.01 * self.max_fuel:
                if not channel_sound.get_busy():  # check if it is not currently playing a sound
                    channel_sound.set_volume(0.3)
                    channel_sound.play(config.rapid_laser_fx, loops=-1)
            else:  # if sound is still playing
                if channel_sound.get_busy():
                    channel_sound.stop()

            if self.fuel <= 0:
                self.fuel = 0
                self.active = False

        else:  # recharge fuel when not active
            self.fuel += self.fuel_recharge_per_sec * delta
            if self.fuel > self.max_fuel:  # stop extra fuel over 100%
                self.fuel = self.max_fuel
            if channel_sound.get_busy():
                channel_sound.stop()

        # Generate new segment only if active
        if self.active:
            x = self.ship.rect.centerx
            y = self.ship.rect.top if self.is_player else self.ship.rect.bottom  # if player we shoot from top rect upwards if ai we shoot from bottom rect downwards
            color = random.choice(self.color_player if self.is_player else self.color_ai)
            lenght = random.randint(30, 50)
            self.segments.append([x, y, lenght, color])

        # Move segments
        for seg in self.segments:
            seg[1] -= self.speed if self.is_player else -self.speed

        # collision check per segment
        surviving_segments = []
        hit_player = set()  # avoid multiple hits per frame

        for seg in self.segments:
            seg_rect = pygame.Rect(seg[0] - self.width // 2, seg[1], self.width, seg[2])
            hit = False

            # asteroid collisions
            for asteroid in asteroid_group:
                if seg_rect.colliderect(asteroid.rect):
                    asteroid.health -= 30
                    hit = True
                    break

            # Enemy collision if it is the player
            if self.is_player:
                for enemy in enemy_group:
                    if seg_rect.colliderect(enemy.rect):
                        enemy.health -= 5
                        hit = True

            else:  # if enemy shoots
                # ai laser hitting the player
                if seg_rect.colliderect(player.rect) and player not in hit_player:
                    # only apply when not already hit
                    player.health -= 1
                    hit_player.add(player)
                    hit = True

            # Keep segments if it does not hit anything
            if not hit and 0 <= seg[1] <= config.SCREEN_HEIGHT:  # within this height
                surviving_segments.append(seg)

        self.segments = surviving_segments

        # update collsision rect for the whole line
        if self.segments:
            top_y = min(seg[1] for seg in self.segments)
            bottom_y = max(seg[1] + seg[2] for seg in self.segments)
            self.line_rect = pygame.Rect(self.segments[0][0] - self.width // 2, top_y, self.width, bottom_y - top_y)

        else:
            self.line_rect = pygame.Rect(0, 0, 0, 0)

    def draw(self, surface):
        for seg in self.segments:
            pygame.draw.rect(surface, seg[3], (seg[0] - self.width // 2, seg[1], self.width, seg[2]))


# ---------------- IceBullet ----------------
class IceBullet:
    """
    IceBullet: simple, player-only projectile.
    - pos : tuple or Vector2 starting position
    - targets: optional iterable/group of enemies to check collisions against.
               If not provided, will use sprite_groups.enemy_group.
    - vel is pixels per second (vector). main loop should call update(dt_seconds).
    - On hit: deals damage and sets enemy.frozen_until (ms since pygame.time.get_ticks()).
    """
    def __init__(self, pos, targets=None, damage=30, freeze_duration_ms=3000):
        # allow pos to be (x,y) or pygame.Rect.center or Vector2
        self.pos = pygame.math.Vector2(pos)
        self.vel = pygame.math.Vector2(0, -400)  # pixels per second upward
        self.radius = 8
        self.damage = damage
        self.freeze_duration_ms = int(freeze_duration_ms)
        self.active = True
        # targets can be a pygame.sprite.Group or list
        self.targets = targets
        # optional image: if you have one use it, otherwise draw primitive shape
        try:
            self.image = pygame.image.load("img/player/freeze_bullet.png").convert_alpha()
            self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))
            self.use_image = True
        except Exception:
            self.image = None
            self.rect = pygame.Rect(int(self.pos.x - self.radius), int(self.pos.y - self.radius),
                                    self.radius * 2, self.radius * 2)
            self.use_image = False

    def update(self, dt):
        """
        dt : seconds (float). main loop should pass frame_time_ms / 1000.0
        """
        if not self.active:
            return
        # move by vel * dt
        self.pos += self.vel * dt
        # update rect for collision checks / drawing
        if self.use_image:
            self.rect.center = (int(self.pos.x), int(self.pos.y))
        else:
            self.rect.topleft = (int(self.pos.x - self.radius), int(self.pos.y - self.radius))

        # kill if out of screen bounds
        if self.pos.y < -50 or self.pos.y > config.SCREEN_HEIGHT + 50 or self.pos.x < -50 or self.pos.x > config.SCREEN_WIDTH + 50:
            self.active = False
            try:
                # if used as sprite in a group that expects kill(), don't crash when not present
                self.kill()
            except Exception:
                pass
            return

        # check collision with targets (prefer provided targets, fallback to global enemy_group)
        targets = self.targets if self.targets is not None else getattr(sprite_groups, "enemy_group", None)
        if not targets:
            return

        # iterate copy to be safe
        for enemy in list(targets):
            if not hasattr(enemy, "rect"):
                continue
            if self.rect.colliderect(enemy.rect) and getattr(enemy, "alive", True):
                # apply damage
                if hasattr(enemy, "shield") and enemy.shield is not None and enemy.shield > 0:
                    # apply to shield first
                    enemy.shield -= self.damage
                    if enemy.shield < 0:
                        leftover = -enemy.shield
                        enemy.shield = 0
                        enemy.health -= leftover
                else:
                    if hasattr(enemy, "health"):
                        enemy.health -= self.damage

                # apply freeze: set frozen_until ms timestamp
                enemy.frozen_until = pygame.time.get_ticks() + self.freeze_duration_ms

                # play optional freeze sound if defined in config
                if hasattr(config, "freeze_fx") and hasattr(config, "channel_11"):
                    try:
                        config.channel_11.play(config.freeze_fx)
                    except Exception:
                        pass

                # deactivate bullet
                self.active = False
                try:
                    self.kill()
                except Exception:
                    pass
                break

    def draw(self, surf):
        if not self.active:
            return
        if self.use_image and self.image:
            surf.blit(self.image, self.rect)
        else:
            # draw cone/triangle as in your earlier design (pointed tip upward)
            tip = (int(self.pos.x), int(self.pos.y - 10))
            left = (int(self.pos.x - 6), int(self.pos.y + 8))
            right = (int(self.pos.x + 6), int(self.pos.y + 8))
            pygame.draw.polygon(surf, (180, 240, 255), [tip, left, right])
            pygame.draw.polygon(surf, (255, 255, 255), [tip, left, right], 1)

            # small snow particles (non-alpha-safe direct draw)
            for _ in range(3):
                offset = pygame.Vector2(random.uniform(-4, 4), random.uniform(-4, 4))
                pos = (int(self.pos.x + offset.x), int(self.pos.y + offset.y))
                # if you want translucency create a small surface with SRCALPHA; keep simple here
                pygame.draw.circle(surf, (200, 240, 255), pos, 2)
