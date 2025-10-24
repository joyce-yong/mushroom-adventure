import pygame  # type: ignore
import os, random

import config
import sprite_groups


# ---------------- Damage Helper ----------------
def apply_damage(entity, dmg, damage_type="normal"):
    """Apply damage on an entity (Player, AI, or Enemy) considering shields."""
    if hasattr(entity, "character_type") and hasattr(entity, "shield"):
        shield = getattr(entity, "shield", 0)
        if shield > 0:
            dmg_to_shield = dmg * 5 if damage_type == "plasma" else dmg
            entity.shield -= dmg_to_shield
            if entity.shield < 0:
                leftover = -entity.shield
                entity.shield = 0
                entity.health -= leftover
        else:
            entity.health -= dmg
    else:
        entity.health -= dmg


# ---------------- Laser Class ----------------
class Laser(pygame.sprite.Sprite):
    def __init__(self, shooter, player, enemy_group, asteroid_group, damage=10, velocity=12):
        super().__init__()
        self.shooter = shooter
        self.player = player
        self.enemy_group = enemy_group
        self.asteroid_group = asteroid_group
        self.damage = damage
        self.velocity = velocity

        self.image = pygame.image.load("img/laser/laser.png").convert_alpha()
        if shooter.character_type.startswith("enemy"):
            self.image = pygame.transform.flip(self.image, False, True)
            self.direction = 1
            self.rect = self.image.get_rect(midtop=shooter.rect.midbottom)
        else:
            self.direction = -1
            self.rect = self.image.get_rect(midbottom=shooter.rect.midtop)

        self.prev_center = pygame.math.Vector2(self.rect.center)

    def update(self):
        prev = pygame.math.Vector2(self.prev_center)
        move_vector = pygame.math.Vector2(0, self.velocity * self.direction)
        current = prev + move_vector

        # Black hole collision
        bh_group = getattr(sprite_groups, 'blackholes_group', None)
        if bh_group:
            for bh in list(bh_group):
                try:
                    if bh.rect.clipline(int(prev.x), int(prev.y), int(current.x), int(current.y)):
                        self.kill()
                        return
                except Exception:
                    if bh.rect.colliderect(pygame.Rect(int(current.x - self.rect.width / 2),
                                                       int(current.y - self.rect.height / 2),
                                                       self.rect.width, self.rect.height)):
                        self.kill()
                        return

        self.rect.center = (int(current.x), int(current.y))
        self.prev_center = pygame.math.Vector2(self.rect.center)

        # Off-screen removal
        if self.rect.bottom < 0 or self.rect.top > config.SCREEN_HEIGHT:
            self.kill()
            return

        # Collision detection
        if self.shooter.character_type.startswith("enemy"):
            if self.player and self.rect.colliderect(self.player.rect):
                apply_damage(self.player, self.damage)
                self.kill()
        else:
            for enemy in self.enemy_group:
                if self.rect.colliderect(enemy.rect):
                    apply_damage(enemy, self.damage)
                    self.kill()
                    return
            for asteroid in self.asteroid_group:
                if self.rect.colliderect(asteroid.rect):
                    asteroid.health -= self.damage
                    self.kill()
                    return

    def draw(self):
        config.game_window.blit(self.image, self.rect)


# ---------------- HeavyLaser Class ----------------
class HeavyLaser(Laser):
    def __init__(self, shooter, player, enemy_group, asteroid_group, damage=50, velocity=8,
                 image_path="img/heavyLaser/heavylaser.png", size=(18, 45)):
        super().__init__(shooter, player, enemy_group, asteroid_group, damage=damage, velocity=velocity)

        if shooter.character_type.startswith("enemy"):
            self.damage = 10
            self.velocity = 6
        else:
            self.damage = damage
            self.velocity = 14

        img = pygame.image.load(image_path).convert_alpha()
        img = pygame.transform.scale(img, size)
        if shooter.character_type.startswith("enemy"):
            img = pygame.transform.flip(img, False, True)
            self.rect = img.get_rect(midtop=shooter.rect.midbottom)
            self.direction = 1
        else:
            self.rect = img.get_rect(midbottom=shooter.rect.midtop)
            self.direction = -1
        self.image = img
        self.prev_center = pygame.math.Vector2(self.rect.center)


# ---------------- Rocket Class ----------------
class Rocket(pygame.sprite.Sprite):
    def __init__(self, shooter, target_group, asteroid_group):
        super().__init__()
        self.shooter = shooter
        self.damage = 50 if shooter.character_type.startswith("enemy") else 200
        self.rocket_images = []
        self.explosion_images = []
        self.exploding = False
        self.frame_index = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 100

        self.target_group = target_group
        self.asteroid_group = asteroid_group

        # Load rocket images
        for filename in sorted(os.listdir("img/rocket")):
            img = pygame.image.load(os.path.join("img/rocket", filename)).convert_alpha()
            img = pygame.transform.scale(img, (20, 50))
            if shooter.character_type.startswith("enemy"):
                img = pygame.transform.flip(img, False, True)
            self.rocket_images.append(img)

        # Load explosion images
        for filename in sorted(os.listdir("img/explosion")):
            img = pygame.image.load(os.path.join("img/explosion", filename)).convert_alpha()
            self.explosion_images.append(img)

        self.image = self.rocket_images[0]
        self.rect = self.image.get_rect(center=shooter.rect.center)
        self.velocity = 6 if shooter.character_type.startswith("enemy") else -12

    def update(self):
        if not self.exploding:
            self.rect.y += self.velocity
            now = pygame.time.get_ticks()
            if now - self.last_update > self.frame_rate:
                self.last_update = now
                self.frame_index = (self.frame_index + 1) % len(self.rocket_images)
                self.image = self.rocket_images[self.frame_index]

            # Collision detection
            detection_area = pygame.Rect(self.rect.centerx - 50, self.rect.centery - 50,
                                         80 if self.shooter.character_type.startswith("enemy") else 100,
                                         30 if self.shooter.character_type.startswith("enemy") else 40)
            hit_something = False
            for target in self.target_group:
                if target is self.shooter:
                    continue
                if detection_area.colliderect(target.rect):
                    apply_damage(target, self.damage)
                    hit_something = True

            for asteroid in self.asteroid_group:
                if detection_area.colliderect(asteroid.rect):
                    asteroid.health -= 100
                    asteroid.break_apart(self.asteroid_group, rocket_hit=True)
                    hit_something = True

            if hit_something:
                self.exploding = True
                self.frame_index = 0
                config.channel_5.set_volume(0.8)
                config.channel_5.play(config.explode_fx)

            if self.rect.bottom < 0 or self.rect.top > config.SCREEN_HEIGHT:
                self.kill()
        else:
            self.animate_explosion()

    def animate_explosion(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame_index += 1
            if self.frame_index >= len(self.explosion_images):
                self.kill()
            else:
                self.image = self.explosion_images[self.frame_index]

    def draw(self):
        config.game_window.blit(self.image, self.rect)


# ---------------- IceBullet Class ----------------
class IceBullet(pygame.sprite.Sprite):
    def __init__(self, shooter, enemy_group, asteroid_group, damage=15, velocity=10, freeze_duration=3000):
        super().__init__()
        self.shooter = shooter
        self.enemy_group = enemy_group
        self.asteroid_group = asteroid_group
        self.damage = damage
        self.velocity = -velocity
        self.freeze_duration = freeze_duration  # ms
        self.image = pygame.image.load("img/icebullet/icebullet.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (20, 40))
        self.rect = self.image.get_rect(midbottom=shooter.rect.midtop)
        self.active = True

    def update(self):
        if not self.active:
            return

        self.rect.y += self.velocity

        # Remove if out of screen
        if self.rect.bottom < 0:
            self.kill()
            return

        # Collision with enemies only (Player bullet)
        for enemy in list(self.enemy_group):
            if self.rect.colliderect(enemy.rect):
                enemy.health -= self.damage
                enemy.frozen_until = pygame.time.get_ticks() + self.freeze_duration
                config.channel_10.play(config.freeze_fx) if hasattr(config, "freeze_fx") else None
                self.kill()
                return

        # Collision with asteroids
        for asteroid in list(self.asteroid_group):
            if self.rect.colliderect(asteroid.rect):
                asteroid.health -= self.damage
                self.kill()
                return

    def draw(self):
        config.game_window.blit(self.image, self.rect)


# ---------------- Explosion Class ----------------
class Explosion(pygame.sprite.Sprite):
    def __init__(self, pos, frames=None, frame_duration=80):
        super().__init__()
        if frames:
            self.frames = frames
        else:
            self.frames = []
            for filename in sorted(os.listdir("img/explosion")):
                img = pygame.image.load(os.path.join("img/explosion", filename)).convert_alpha()
                self.frames.append(img)

        self.frame_duration = frame_duration
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(center=pos)
        self.last_update = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_duration:
            self.last_update = now
            self.current_frame += 1
            if self.current_frame >= len(self.frames):
                self.kill()
            else:
                self.image = self.frames[self.current_frame]
