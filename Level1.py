import pygame
import random
import math
import sys

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
        if keys[pygame.K_LEFT]:
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

# ---------------- Laser ----------------
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

class Laser:
    def __init__(self, color_main=(200, 220, 255), color_glow=(120, 180, 255)):
        self.cooldown = 0.15
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

# ---------------- Ice Bullet ----------------
class IceBullet:
    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(0, -400)  # 向上飞
        self.radius = 8
        self.damage = 30
        self.freeze_duration = 3000  # 毫秒
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
        # 绘制冰锥形子弹（尖头）
        tip = (int(self.pos.x), int(self.pos.y - 10))
        left = (int(self.pos.x - 6), int(self.pos.y + 8))
        right = (int(self.pos.x + 6), int(self.pos.y + 8))
        pygame.draw.polygon(surf, (180, 240, 255), [tip, left, right])
        pygame.draw.polygon(surf, (255, 255, 255), [tip, left, right], 1)

        # 雪花粒子光晕
        for _ in range(3):
            offset = pygame.Vector2(random.uniform(-4, 4), random.uniform(-4, 4))
            pygame.draw.circle(surf, (200, 240, 255, 100), (int(self.pos.x + offset.x), int(self.pos.y + offset.y)), 2)

# ---------------- Explosion + Particles ----------------
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
        pygame.draw.circle(surf, (*self.color, int(alpha)), (int(self.pos.x), int(self.pos.y)), 3)

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
#Enemy---------------------------------------------------------------------------
class Enemy:
    def __init__(self, kind="basic"):
        self.kind = kind
        self.hit_flash = 0.0
        self.dead = False
        self.frozen_until = 0
        self.freeze_effect_time = 0
        self.freeze_effect_duration = 4000  # 冰冻持续4秒（毫秒）
        self.freeze_circle_radius = 0
        self.freeze_circle_max = 50

        # 初始化敌人种类与图像
        self.set_type_stats()

        # 随机出生位置
        margin_x = 60
        self.pos = pygame.Vector2(random.randint(margin_x, WIDTH - margin_x),
                                  -self.image.get_height() - random.randint(20, 120))
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

        # 可选漂浮参数
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
        """处理受到攻击逻辑"""
        if self.dead:
            return None

        # 扣血
        self.hp -= dmg
        self.hit_flash = 0.25

        # 冰冻逻辑
        if freeze:
            self.frozen_until = pygame.time.get_ticks() + self.freeze_effect_duration
            self.freeze_effect_time = pygame.time.get_ticks()
            self.freeze_circle_radius = 0

        # 判断是否死亡
        if self.hp <= 0:
            self.hp = 0
            self.dead = True
            # 立即返回一个爆炸对象（主循环应接收并加入 explosion 列表）
            return Explosion(self.pos)
        return None

    def update(self, dt):
        if self.dead:
            return

        current_time = pygame.time.get_ticks()

        # 减少受击闪烁时间
        if self.hit_flash > 0:
            self.hit_flash -= dt * 2.5
            if self.hit_flash < 0:
                self.hit_flash = 0

        # 冰冻状态检测（冻结期间不动）
        if current_time < self.frozen_until:
            return  # 被冻住，不更新位置

        # 正常移动
        self.pos.y += self.speed * dt
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def draw(self, surf):
        if self.dead:
            return

        current_time = pygame.time.get_ticks()
        img = self.image.copy()

        frozen = current_time < self.frozen_until

        # --- 冰冻状态（冰蓝滤色，保留形状） ---
        if frozen:
            # 创建一个完全透明的同尺寸图层
            ice_layer = pygame.Surface(img.get_size(), pygame.SRCALPHA)

            # 在冰层上画一层蓝色，但不影响透明像素
            for x in range(img.get_width()):
                for y in range(img.get_height()):
                    r, g, b, a = img.get_at((x, y))
                    if a > 10:  # 只处理非透明区域
                        # 模拟结冰的颜色（保留原色但偏蓝）
                        nr = int(r * 0.7 + 40)
                        ng = int(g * 0.8 + 80)
                        nb = int(b * 1.2 + 100)
                        ice_layer.set_at((x, y), (min(nr, 255), min(ng, 255), min(nb, 255), a))
                    else:
                        ice_layer.set_at((x, y), (0, 0, 0, 0))
            img = ice_layer

        # --- 受击闪烁（红色） ---
        if self.hit_flash > 0:
            flash_intensity = int(255 * self.hit_flash)
            img.fill((flash_intensity, 80, 80, 0), None, pygame.BLEND_RGBA_ADD)

        # --- 绘制敌人 ---
        surf.blit(img, img.get_rect(center=(int(self.pos.x), int(self.pos.y))))


# ---------------- Utility ----------------
def line_segment_rect_intersect(p1, p2, rect):
    return bool(rect.clipline((int(p1.x), int(p1.y), int(p2.x), int(p2.y))))

# ---------------- Game Setup ----------------
player = Player((WIDTH // 2, HEIGHT - 120))
laser = Laser()  # 普通雷射
ice_bullets = []
enemies = []
explosions = []
spawn_timer = 0.0
score = 0
game_over = False


# ---------------- Main Loop ----------------
running = True

while running:
    dt = clock.tick(60) / 1000.0

    # -------- input (只处理按键触发：发射/退出等) --------
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                running = False

            # 发射冰冻弹 (A) —— 只负责创建子弹
            if ev.key == pygame.K_a and not game_over:
                ice_bullets.append(IceBullet(player.pos))

            # 普通雷射（W） —— 发射并立即检测直线命中（会调用 take_damage 并可能返回 Explosion）
            if ev.key == pygame.K_w and not game_over:
                fired = laser.try_fire(player.pos)
                # debug: print("Pressed W -> try_fire returned", fired)
                if fired:
                    for en in enemies:
                        if not en.dead and line_segment_rect_intersect(laser.start, laser.end, en.rect):
                            exp = en.take_damage(laser.damage)
                            if exp:
                                explosions.append(exp)
                                score += en.score_value

    # -------- update (每帧更新：子弹、敌人、碰撞、爆炸) --------
    if not game_over:
        # player / laser update
        player.handle_input(dt)
        player.update(dt)
        laser.update(dt)

        # 更新冰弹位置并检测子弹碰撞（在这里统一处理）
        for bullet in ice_bullets[:]:
            bullet.update(dt)
            if not bullet.active:
                ice_bullets.remove(bullet)
                continue

            # 碰撞检测：如果子弹碰到敌人，调用 take_damage(..., freeze=True)
            for en in enemies:
                if not en.dead and en.rect.collidepoint(bullet.pos):
                    exp = en.take_damage(bullet.damage, freeze=True)
                    # 标记子弹失效
                    bullet.active = False
                    if exp:
                        explosions.append(exp)
                        score += en.score_value
                    break  # 该子弹已处理，跳出对敌人的检测

        # 更新敌人（移动/冻结逻辑/hit_flash 等）
        for en in enemies[:]:
            en.update(dt)
            # 如果敌人死亡（dead==True），我们可以立刻从敌人列表移除，或者让其在场景中保留一帧再移除。
            # 我们选择：立即移除（因为 Explosion 已经被加入 explosions 列表）
            if en.dead:
                # 已经在 take_damage 里创建了 Explosion 并加入了 explosions（如果有的话）
                try:
                    enemies.remove(en)
                except ValueError:
                    pass
                continue
            # 如果敌人掉出画面也移除
            if en.pos.y > HEIGHT + 120:
                enemies.remove(en)

        # 更新爆炸特效（并在列表中移除已经结束的爆炸）
        for exp in explosions[:]:
            if not exp.update(dt):
                explosions.remove(exp)

        # 生成新敌人
        spawn_timer += dt
        if spawn_timer > 1.2:
            spawn_timer = 0
            kind = random.choices(["basic", "fast", "tank"], weights=[0.6, 0.3, 0.1])[0]
            enemies.append(Enemy(kind))

        # 胜利判定
        if score >= 100:
            game_over = True

    else:
        # 游戏结束时仍更新激光和冰弹（用于残留显示），以及角色动画
        laser.update(dt)
        for bullet in ice_bullets[:]:
            bullet.update(dt)
            if not bullet.active:
                ice_bullets.remove(bullet)
        for exp in explosions[:]:
            if not exp.update(dt):
                explosions.remove(exp)
        player.update(dt)

    # -------- draw --------
    draw_background(dt)
    player.draw(screen)
    laser.draw(screen)

    # 绘制冰弹
    for bullet in ice_bullets:
        bullet.draw(screen)

    # 绘制敌人
    for en in enemies:
        en.draw(screen)

    # 绘制爆炸（爆炸的 draw 不在 update 中）
    for exp in explosions:
        exp.draw(screen)

    # HUD
    txt = FONT.render(f"Score: {score}/100", True, (220, 220, 220))
    screen.blit(txt, (12, 10))
    if game_over:
        over = FONT.render("GAME OVER! You reached 100 points!", True, (255, 210, 90))
        screen.blit(over, (WIDTH // 2 - 260, HEIGHT // 2 - 20))

    pygame.display.flip()

pygame.quit()
sys.exit()
