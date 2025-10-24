import pygame
import random
import config
from projectiles import Laser, Rocket, Explosion
from sprite_groups import explosion_group, enemy_group


# ---------------- FreezeBullet ----------------
class FreezeBullet(pygame.sprite.Sprite):
    """Player's ice bullet: causes damage + freezes enemy for 3 sec"""
    def __init__(self, ship, target_group, damage=20, freeze_time=3000):
        super().__init__()
        self.ship = ship
        self.damage = damage
        self.freeze_time = freeze_time
        self.image = pygame.image.load("img/player/freeze_bullet.png").convert_alpha()
        self.rect = self.image.get_rect(center=ship.rect.center)
        self.speed = 10
        self.target_group = target_group

    def update(self):
        self.rect.y -= self.speed

        # check collision with enemies
        for enemy in self.target_group:
            if self.rect.colliderect(enemy.rect) and getattr(enemy, "alive", True):
                enemy.health -= self.damage
                enemy.frozen_until = pygame.time.get_ticks() + self.freeze_time
                if hasattr(config, 'freeze_fx'):
                    config.channel_11.play(config.freeze_fx)
                self.kill()
                break

        # remove if out of screen
        if self.rect.bottom < 0:
            self.kill()

    def draw(self, surf):
        surf.blit(self.image, self.rect)


# ---------------- Ship ----------------
class Ship(pygame.sprite.Sprite):
    def __init__(self, character_type, ship_x, ship_y, scale, velocity):
        super().__init__()
        self.character_type = character_type
        self.velocity = velocity
        self.flip = False

        stats = config.ship_stats.get(self.character_type, {'health': 100, 'shield': -1})
        self.health = stats.get('health', 100)
        self.shield = stats.get('shield', -1)
        self.max_health = self.health
        self.max_shield = self.shield
        self.alive = True
        self.frozen_until = 0  # ✅ track freeze effect

        # enemy behavior
        self.phase = 'enter'
        self.target_y = 50
        self.spawn_time = pygame.time.get_ticks()
        self.start_delay = 4000

        # load sprite
        img = pygame.image.load(f'img/{self.character_type}/Idle/0.png').convert_alpha()
        self.image = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
        self.rect = self.image.get_rect(center=(ship_x, ship_y))
        self.original_image = self.image.copy()

        # attack systems
        self.lasers = pygame.sprite.Group()
        self.laser_cooldown = 100
        self.last_laser_time = 0

        self.heavy_cooldown = 300
        self.last_heavy_time = 0

        self.freeze_cooldown = 800
        self.last_freeze_time = 0

        self.rocket_cooldown = 1000
        self.last_rocket_time = 0

        self.plasma_cooldown = 400
        self.last_plasma_time = 0

        # flash effects
        self.prev_health = self.health
        self.flash_time = 100
        self.flash_start = 0
        self.flash_images = [
            pygame.transform.scale(
                pygame.image.load(f'img/{self.character_type}/damage/{i}.png').convert_alpha(),
                (self.rect.width, self.rect.height)
            ) for i in range(2)
        ]
        self.prev_shield = self.shield
        self.shield_time = 100
        self.shield_start = 0
        self.shield_images = [
            pygame.transform.scale(
                pygame.image.load(f'img/{self.character_type}/shield/{i}.png').convert_alpha(),
                (self.rect.width, self.rect.height)
            ) for i in range(2)
        ]

    # ---------------- draw ----------------
    def draw(self):
        config.game_window.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

    # ---------------- update ----------------
    def update(self, player):
        self.check_alive(player)
        self.damage_flash()

        # skip all actions if frozen
        if pygame.time.get_ticks() < self.frozen_until:
            return

    # ---------------- shoot freeze ----------------
    def shoot_freeze(self, target_enemy_group):
        """Player-only freeze bullet"""
        if not self.character_type.startswith("player"):
            return
        now = pygame.time.get_ticks()
        if now - self.last_freeze_time >= self.freeze_cooldown:
            bullet = FreezeBullet(self, target_enemy_group)
            self.lasers.add(bullet)
            self.last_freeze_time = now
            if hasattr(config, 'freeze_fx'):
                config.channel_11.play(config.freeze_fx)

    # ---------------- check alive ----------------
    def check_alive(self, player):
        if self.health <= 0 and self.alive:
            self.health = 0
            self.velocity = 0
            self.alive = False
            self.kill()

            # explosion animation
            explosion = Explosion(self.rect.center, config.explosion_frames, frame_duration=80)
            explosion_group.add(explosion)

            config.channel_10.set_volume(1)
            config.channel_10.play(config.death_fx)

            # rewards
            reward = config.enemy_rewards.get(self.character_type, {'score': 70, 'shield': 30, 'health': 0})
            config.score += reward['score']
            player.shield = min(player.max_shield, player.shield + reward.get('shield', 0))
            player.health = min(player.max_health, player.health + reward.get('health', 0))

    # ---------------- damage flash ----------------
    def damage_flash(self):
        elapsed = pygame.time.get_ticks() - self.flash_start
        flashing = elapsed < self.flash_time * len(self.flash_images)
        if self.health < self.prev_health and not flashing:
            self.flash_start = pygame.time.get_ticks()
        self.prev_health = self.health

        elapsed_shield = pygame.time.get_ticks() - self.shield_start
        shield_flashing = elapsed_shield < self.shield_time * len(self.shield_images)
        if self.shield < self.prev_shield and not shield_flashing:
            config.channel_9.set_volume(0.6)
            config.channel_9.play(config.shield_fx)
            self.shield_start = pygame.time.get_ticks()
        self.prev_shield = self.shield

        if flashing:
            frame = (elapsed // self.flash_time) % len(self.flash_images)
            self.image = self.flash_images[frame]
        elif shield_flashing:
            frame = (elapsed_shield // self.shield_time) % len(self.shield_images)
            self.image = self.shield_images[frame]
        else:
            self.image = self.original_image

    # ---------------- player movement ----------------
    def movement(self, moving_left, moving_right, moving_up, moving_down):
        if pygame.time.get_ticks() < self.frozen_until:
            return

        dx = dy = 0
        if moving_left: dx = -1
        if moving_right: dx = 1
        if moving_up: dy = -1
        if moving_down: dy = 1

        if dx and dy:
            dx *= 0.7071
            dy *= 0.7071

        self.rect.x += dx * self.velocity
        self.rect.y += dy * self.velocity
        self.rect.clamp_ip(pygame.Rect(0, 0, config.SCREEN_WIDTH, config.SCREEN_HEIGHT))

    # ---------------- enemy movement ----------------
    def update_enemy(self, window_height):
        if pygame.time.get_ticks() < self.frozen_until:
            return
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

    # ---------------- update lasers ----------------
    def update_lasers(self):
        for laser in list(self.lasers):
            laser.update()
            laser.draw(config.game_window)
