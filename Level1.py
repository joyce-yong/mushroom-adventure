# level1.py  — 改造版：三种攻击（A 普通子弹, S 镭射, D 冰冻），敌人子弹，爆炸，HUD
import pygame
import random
import math
import sys
import time

pygame.init()

WIDTH, HEIGHT = 900, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Laser Beam FX + Freeze Beam")
FONT = pygame.font.Font("Mushroom Adventure/SpaceMadness.ttf", 40)

# ---------------- Background ----------------
bg_img = pygame.image.load("Mushroom Adventure/Animated/Strip And GIF/GIF_4FPS/space9_4-frames.png").convert()
bg_w, bg_h = bg_img.get_size()
bg_y = 0
bg_speed = 80

def draw_background(dt):
    global bg_y
    bg_y += bg_speed * dt
    if bg_y >= bg_h:
        bg_y = 0
    y1 = bg_y - bg_h
    y2 = bg_y
    for y in (y1, y2):
        for x in range(0, WIDTH, bg_w):
            screen.blit(bg_img, (x, y))

# ---------------- Player ----------------
class Player:
    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        self.speed = 300
        self.anim_frames = []
        self.anim_index = 0
        self.anim_timer = 0.0
        self.anim_speed = 0.12
        self.scale = 1.8
        self.load_sprites()
        self.health = 100
        self.max_health = 100
        self.invuln_until = 0  # small invuln after hit
        self.score = 0

    def load_sprites(self):
        try:
            for i in range(3):
                img = pygame.image.load(f"Mushroom Adventure/character/mushroom{i}.png").convert_alpha()
                w, h = img.get_size()
                scaled = pygame.transform.scale(img, (int(w * self.scale), int(h * self.scale)))
                self.anim_frames.append(scaled)
        except Exception as e:
            print("Warning: couldn't load player sprites, fallback to circle:", e)
            self.anim_frames = None

    def handle_input(self, dt):
        keys = pygame.key.get_pressed()
        move = pygame.Vector2(0, 0)
        if keys[pygame.K_LEFT] or keys[pygame.K_a and False]:  # keep left/right mapping
            move.x -= 1
        if keys[pygame.K_RIGHT]:
            move.x += 1
        if move.length_squared() > 0:
            move = move.normalize() * self.speed * dt
        self.pos += move
        self.pos.x = max(30, min(WIDTH - 30, self.pos.x))

    def update(self, dt):
        if self.anim_frames:
            self.anim_timer += dt
            if self.anim_timer >= self.anim_speed:
                self.anim_timer = 0
                self.anim_index = (self.anim_index + 1) % len(self.anim_frames)

    def draw(self, surf):
        if self.anim_frames:
            frame = self.anim_frames[self.anim_index]
            rect = frame.get_rect(center=(int(self.pos.x), int(self.pos.y)))
            surf.blit(frame, rect)
        else:
            pygame.draw.circle(surf, (255, 255, 255), (int(self.pos.x), int(self.pos.y)), 16)

    def take_damage(self, dmg):
        now = pygame.time.get_ticks()
        if now < self.invuln_until:
            return
        self.health -= dmg
        self.invuln_until = now + 400  # 400 ms invuln
        if self.health < 0:
            self.health = 0

# ---------------- Projectiles ----------------
class Bullet:
    """普通子弹（玩家）——快速、可连发"""
    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(0, -700)
        self.radius = 5
        self.damage = 25
        self.active = True

    def update(self, dt):
        if not self.active:
            return
        self.pos += self.vel * dt
        if self.pos.y < -20:
            self.active = False

    def draw(self, surf):
        if not self.active:
            return
        pygame.draw.circle(surf, (255, 240, 120), (int(self.pos.x), int(self.pos.y)), self.radius)
        # small glow
        pygame.draw.circle(surf, (255, 200, 80), (int(self.pos.x), int(self.pos.y)), self.radius+2, 1)

class Laser:
    """你原本的雷射（向上瞬发，穿透）"""
    def __init__(self, color_main=(200, 220, 255), color_glow=(120, 180, 255)):
        self.cooldown = 0.25
        self.timer = 0.0
        self.duration = 0.09
        self.active = False
        self.start = pygame.Vector2()
        self.end = pygame.Vector2()
        self.damage = 40
        self.color_main = color_main
        self.color_glow = color_glow

    def try_fire(self, start):
        if self.timer > 0:
            return False
        self.start = start.copy()
        dir = pygame.Vector2(0, -1)
        self.end = ray_to_screen_edge(self.start, dir)
        self.timer = self.cooldown
        self.active = True
        self._life = self.duration
        return True

    def update(self, dt):
        if self.timer > 0:
            self.timer -= dt
        if self.active:
            self._life -= dt
            if self._life <= 0:
                self.active = False

    def draw(self, surf):
        if not self.active:
            return
        glow = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.line(glow, (*self.color_glow, 90), self.start, self.end, 22)
        pygame.draw.line(glow, (*self.color_main, 180), self.start, self.end, 10)
        pygame.draw.line(glow, (255, 255, 255, 230), self.start, self.end, 4)
        pygame.draw.circle(glow, (255, 255, 255, 220), (int(self.start.x), int(self.start.y)), 8)
        surf.blit(glow, (0, 0))

class IceBullet:
    """冰冻子弹（玩家）——命中敌人时触发冻结状态"""
    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(0, -420)
        self.radius = 8
        self.damage = 30
        self.freeze_duration = 3000  # ms
        self.active = True

    def update(self, dt):
        if not self.active:
            return
        self.pos += self.vel * dt
        if self.pos.y < -20:
            self.active = False

    def draw(self, surf):
        if not self.active:
            return
        tip = (int(self.pos.x), int(self.pos.y - 10))
        left = (int(self.pos.x - 6), int(self.pos.y + 8))
        right = (int(self.pos.x + 6), int(self.pos.y + 8))
        pygame.draw.polygon(surf, (180, 240, 255), [tip, left, right])
        pygame.draw.polygon(surf, (255, 255, 255), [tip, left, right], 1)
        for _ in range(3):
            offset = pygame.Vector2(random.uniform(-4, 4), random.uniform(-4, 4))
            # draw tiny translucent dots (use alpha surface)
            dot_s = pygame.Surface((6,6), pygame.SRCALPHA)
            pygame.draw.circle(dot_s, (200,240,255,120), (3,3), 2)
            surf.blit(dot_s, (int(self.pos.x+offset.x)-3, int(self.pos.y+offset.y)-3))

class EnemyBullet:
    """敌人子弹，朝玩家方向发射"""
    def __init__(self, pos, target_pos):
        self.pos = pygame.Vector2(pos)
        dir_vec = (pygame.Vector2(target_pos) - self.pos)
        if dir_vec.length_squared() == 0:
            dir_vec = pygame.Vector2(0,1)
        self.vel = dir_vec.normalize() * 240
        self.radius = 6
        self.damage = 15
        self.active = True

    def update(self, dt):
        if not self.active:
            return
        self.pos += self.vel * dt
        if self.pos.y > HEIGHT + 20 or self.pos.y < -50 or self.pos.x < -50 or self.pos.x > WIDTH + 50:
            self.active = False

    def draw(self, surf):
        if not self.active:
            return
        pygame.draw.circle(surf, (255,80,80), (int(self.pos.x), int(self.pos.y)), self.radius)
        pygame.draw.circle(surf, (255,200,180), (int(self.pos.x), int(self.pos.y)), self.radius, 1)

# ---------------- Explosion + Particles (保留你原实现) ----------------
class Particle:
    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(100, 300)
        self.vel = pygame.Vector2(math.cos(angle), math.sin(angle)) * speed
        self.life = random.uniform(0.4, 0.9)
        self.timer = 0
        self.color = random.choice([(255, 220, 100), (255, 180, 60), (255, 255, 180)])

    def update(self, dt):
        self.timer += dt
        self.pos += self.vel * dt
        self.vel *= 0.9
        return self.timer < self.life

    def draw(self, surf):
        alpha = max(0, 255 * (1 - self.timer / self.life))
        s = pygame.Surface((6,6), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, int(alpha)), (3,3), 3)
        surf.blit(s, (int(self.pos.x)-3, int(self.pos.y)-3))

class Explosion:
    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        self.radius = 10
        self.max_radius = 50
        self.alpha = 255
        self.life = 0.3
        self.timer = 0.0
        self.particles = []
        self.particles_spawned = False

    def update(self, dt):
        self.timer += dt
        t = self.timer / self.life
        self.radius = 10 + (self.max_radius - 10) * t
        self.alpha = max(0, 255 * (1 - t))
        if not self.particles_spawned and t >= 1.0:
            self.particles_spawned = True
            self.particles = [Particle(self.pos) for _ in range(25)]
        if self.particles_spawned:
            self.particles = [p for p in self.particles if p.update(dt)]
        return t < 1.0 or len(self.particles) > 0

    def draw(self, surf):
        if self.alpha > 0:
            glow = pygame.Surface((self.max_radius * 2, self.max_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 200, 80, int(self.alpha)), (self.max_radius, self.max_radius), int(self.radius))
            pygame.draw.circle(glow, (255, 240, 120, int(self.alpha * 0.6)), (self.max_radius, self.max_radius), int(self.radius * 0.6))
            surf.blit(glow, (self.pos.x - self.max_radius, self.pos.y - self.max_radius), special_flags=pygame.BLEND_ADD)
        for p in self.particles:
            p.draw(surf)

# ---------------- Enemy (延伸你原版，加入射击) ----------------
class Enemy:
    def __init__(self, kind="basic"):
        self.kind = kind
        self.hit_flash = 0.0
        self.dead = False
        self.frozen_until = 0
        self.freeze_effect_time = 0
        self.freeze_effect_duration = 4000  # ms
        self.freeze_circle_radius = 0
        self.freeze_circle_max = 50

        # 初始化敌人种类与图像
        self.set_type_stats()

        # 随机出生位置
        margin_x = 60
        self.pos = pygame.Vector2(random.randint(margin_x, WIDTH - margin_x),
                                  -self.image.get_height() - random.randint(20, 120))
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

        # 子弹射击
        self.last_shot = 0
        self.shoot_interval = random.uniform(1.2, 3.0)  # 每个敌人随机冷却

        # 漂浮参数
        self._drift_phase = random.uniform(0, math.pi * 2)
        self._drift_amp = random.uniform(0.0, 18.0)

    def set_type_stats(self):
        base_img = pygame.image.load("Mushroom Adventure/Enemy/eenemy.png").convert_alpha()

        if self.kind == "basic":
            self.scale = 0.9
            self.max_hp = 100
            self.speed = 120
            self.score_value = 10
        elif self.kind == "fast":
            self.scale = 0.6
            self.max_hp = 60
            self.speed = 220
            self.score_value = 18
        elif self.kind == "tank":
            self.scale = 1.3
            self.max_hp = 220
            self.speed = 70
            self.score_value = 35
        else:
            self.scale = 0.7
            self.max_hp = 80
            self.speed = 100
            self.score_value = 8

        new_w = max(4, int(base_img.get_width() * self.scale))
        new_h = max(4, int(base_img.get_height() * self.scale))
        self.image = pygame.transform.scale(base_img, (new_w, new_h))
        self.hp = self.max_hp

    def take_damage(self, dmg, freeze=False):
        if self.dead:
            return None
        self.hp -= dmg
        self.hit_flash = 0.25
        if freeze:
            self.frozen_until = pygame.time.get_ticks() + self.freeze_effect_duration
            self.freeze_effect_time = pygame.time.get_ticks()
            self.freeze_circle_radius = 0
        if self.hp <= 0:
            self.hp = 0
            self.dead = True
            return Explosion(self.pos)
        return None

    def update(self, dt):
        if self.dead:
            return
        current_time = pygame.time.get_ticks()
        if self.hit_flash > 0:
            self.hit_flash -= dt * 2.5
            if self.hit_flash < 0:
                self.hit_flash = 0
        # 冰冻检测
        if current_time < self.frozen_until:
            return
        # 正常移动
        # 加入微幅漂浮
        self._drift_phase += dt
        drift = math.sin(self._drift_phase * 1.2) * self._drift_amp * dt
        self.pos.y += self.speed * dt
        self.pos.x += drift
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def draw(self, surf):
        if self.dead:
            return
        current_time = pygame.time.get_ticks()
        img = self.image.copy()
        frozen = current_time < self.frozen_until
        if frozen:
            ice_layer = pygame.Surface(img.get_size(), pygame.SRCALPHA)
            for x in range(img.get_width()):
                for y in range(img.get_height()):
                    r, g, b, a = img.get_at((x, y))
                    if a > 10:
                        nr = int(r * 0.7 + 40)
                        ng = int(g * 0.8 + 80)
                        nb = int(b * 1.2 + 100)
                        ice_layer.set_at((x, y), (min(nr,255), min(ng,255), min(nb,255), a))
                    else:
                        ice_layer.set_at((x, y), (0,0,0,0))
            img = ice_layer
        if self.hit_flash > 0:
            flash_intensity = int(255 * self.hit_flash)
            img.fill((flash_intensity, 80, 80, 0), None, pygame.BLEND_RGBA_ADD)
        surf.blit(img, img.get_rect(center=(int(self.pos.x), int(self.pos.y))))

    def can_shoot(self):
        now = pygame.time.get_ticks()
        return (now - self.last_shot) >= self.shoot_interval

    def shoot(self, target_pos):
        """返回 EnemyBullet 实例（朝 target_pos 发射）"""
        if not self.can_shoot() or self.dead:
            return None
        self.last_shot = pygame.time.get_ticks()
        # 随机微调射速间隔
        self.shoot_interval = random.uniform(1.0, 3.0)
        return EnemyBullet(self.pos, target_pos)

# ---------------- Utility ----------------
def line_segment_rect_intersect(p1, p2, rect):
    return bool(rect.clipline((int(p1.x), int(p1.y), int(p2.x), int(p2.y))))

def ray_to_screen_edge(start, direction):
    eps = 1e-6
    candidates = []
    if abs(direction.x) > eps:
        for x_edge in (0, WIDTH):
            t = (x_edge - start.x) / direction.x
            if t > 0:
                y = start.y + direction.y * t
                if -1 <= y <= HEIGHT + 1:
                    candidates.append(t)
    if abs(direction.y) > eps:
        for y_edge in (0, HEIGHT):
            t = (y_edge - start.y) / direction.y
            if t > 0:
                x = start.x + direction.x * t
                if -1 <= x <= WIDTH + 1:
                    candidates.append(t)
    if not candidates:
        return start + direction * 2000
    return start + direction * min(candidates)

# ---------------- Game Setup ----------------
player = Player((WIDTH // 2, HEIGHT - 120))
laser = Laser()  # 镭射（S）
bullet_list = []  # A 普通子弹
ice_bullets = []   # D 冰冻
enemy_bullets = [] # 敌人发射
enemies = []
explosions = []
spawn_timer = 0.0
score = 0
game_over = False

# 控制发射冷却（玩家普通子弹连发）
last_player_bullet = 0.0
player_bullet_cooldown = 0.12  # 秒

# ---------------- Main Loop ----------------
running = True
while running:
    dt = clock.tick(60) / 1000.0

    # -------- input --------
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                running = False

            if not game_over:
                # A -> 普通子弹
                if ev.key == pygame.K_a:
                    now = time.time()
                    if now - last_player_bullet >= player_bullet_cooldown:
                        b = Bullet((player.pos.x, player.pos.y - 20))
                        bullet_list.append(b)
                        last_player_bullet = now

                # S -> 镭射（瞬发检测）
                if ev.key == pygame.K_s:
                    fired = laser.try_fire(player.pos)
                    if fired:
                        # 检测命中（穿透所有敌人）
                        for en in list(enemies):
                            if not en.dead and line_segment_rect_intersect(laser.start, laser.end, en.rect):
                                exp = en.take_damage(laser.damage)
                                if exp:
                                    explosions.append(exp)
                                    score += en.score_value
                                    try:
                                        enemies.remove(en)
                                    except ValueError:
                                        pass

                # D -> 冰冻子弹
                if ev.key == pygame.K_d:
                    ice_bullets.append(IceBullet(player.pos))

    # -------- update --------
    if not game_over:
        player.handle_input(dt)
        player.update(dt)
        laser.update(dt)

        # 更新普通子弹并检测碰撞
        for b in bullet_list[:]:
            b.update(dt)
            if not b.active:
                bullet_list.remove(b)
                continue
            hit = False
            for en in list(enemies):
                if not en.dead and en.rect.collidepoint(b.pos.x, b.pos.y):
                    exp = en.take_damage(b.damage)
                    b.active = False
                    hit = True
                    if exp:
                        explosions.append(exp)
                        score += en.score_value
                        try:
                            enemies.remove(en)
                        except ValueError:
                            pass
                    break
            if hit:
                try:
                    bullet_list.remove(b)
                except ValueError:
                    pass

        # 更新冰弹并检测碰撞（freeze=True）
        for bullet in ice_bullets[:]:
            bullet.update(dt)
            if not bullet.active:
                try:
                    ice_bullets.remove(bullet)
                except ValueError:
                    pass
                continue

            collided = False
            for en in list(enemies):
                if not en.dead and en.rect.collidepoint(bullet.pos.x, bullet.pos.y):
                    exp = en.take_damage(bullet.damage, freeze=True)
                    bullet.active = False
                    collided = True
                    if exp:
                        explosions.append(exp)
                        score += en.score_value
                        try:
                            enemies.remove(en)
                        except ValueError:
                            pass
                    break
            if collided:
                try:
                    ice_bullets.remove(bullet)
                except ValueError:
                    pass

        # 敌人 AI 更新与射击
        for en in list(enemies):
            en.update(dt)
            if en.dead:
                try:
                    enemies.remove(en)
                except ValueError:
                    pass
                continue
            # if enemy leaves screen
            if en.pos.y > HEIGHT + 120:
                try:
                    enemies.remove(en)
                except ValueError:
                    pass
                continue
            # 敌人发射子弹（朝玩家）
            if en.can_shoot():
                eb = en.shoot(player.pos)
                if eb:
                    enemy_bullets.append(eb)

        # 更新敌人子弹并检测玩家被击中
        for eb in enemy_bullets[:]:
            eb.update(dt)
            if not eb.active:
                try:
                    enemy_bullets.remove(eb)
                except ValueError:
                    pass
                continue
            # 碰撞玩家
            # 简单圆形碰撞检测
            if pygame.Vector2(eb.pos - player.pos).length() < (eb.radius + 18):
                player.take_damage(eb.damage)
                eb.active = False
                try:
                    enemy_bullets.remove(eb)
                except ValueError:
                    pass
                # 可选择播放受击音效

        # 更新爆炸
        for exp in explosions[:]:
            if not exp.update(dt):
                try:
                    explosions.remove(exp)
                except ValueError:
                    pass

        # 生成新敌人
        spawn_timer += dt
        if spawn_timer > 1.2:
            spawn_timer = 0
            kind = random.choices(["basic", "fast", "tank"], weights=[0.6, 0.3, 0.1])[0]
            enemies.append(Enemy(kind))

        # 分数胜利判定（你原本设 score>=100）
        if score >= 100:
            game_over = True

        # 玩家死亡检测
        if player.health <= 0:
            game_over = True

    else:
        # Game over：仍更新视觉残留（laser, bullets, explosion）
        laser.update(dt)
        for b in bullet_list[:]:
            b.update(dt)
            if not b.active:
                try:
                    bullet_list.remove(b)
                except ValueError:
                    pass
        for bullet in ice_bullets[:]:
            bullet.update(dt)
            if not bullet.active:
                try:
                    ice_bullets.remove(bullet)
                except ValueError:
                    pass
        for exp in explosions[:]:
            if not exp.update(dt):
                try:
                    explosions.remove(exp)
                except ValueError:
                    pass
        player.update(dt)

    # -------- draw --------
    draw_background(dt)
    player.draw(screen)
    laser.draw(screen)

    for b in bullet_list:
        b.draw(screen)
    for bullet in ice_bullets:
        bullet.draw(screen)

    for eb in enemy_bullets:
        eb.draw(screen)

    for en in enemies:
        en.draw(screen)

    for exp in explosions:
        exp.draw(screen)

    # HUD — 保持你原来的风格（Score 在左上）
    txt = FONT.render(f"Score: {score}/100", True, (220, 220, 220))
    screen.blit(txt, (12, 10))

    # 玩家生命条（简易）
    hp_txt = FONT.render(f"HP: {player.health}/{player.max_health}", True, (255, 220, 120))
    screen.blit(hp_txt, (12, 58))

    if game_over:
        over = FONT.render("GAME OVER! You reached 100 points!" if score>=100 else "GAME OVER! You died!", True, (255, 210, 90))
        screen.blit(over, (WIDTH // 2 - 260, HEIGHT // 2 - 20))

    pygame.display.flip()

pygame.quit()
sys.exit()
