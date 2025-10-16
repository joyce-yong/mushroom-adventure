import pygame
import random
import math
import sys

pygame.init()

WIDTH, HEIGHT = 900, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Laser Beam FX (Explosion + Particles)")
FONT = pygame.font.Font("C:/Users/PC/Desktop/school apu/Sem 2/Imaging and Special Effects (082025-MTG)/Mushroom Adventure/SpaceMadness.ttf", 40)

# ---------------- Background ----------------
bg_img = pygame.image.load("C:\\Users\\PC\\Desktop\\school apu\\Sem 2\\Imaging and Special Effects (082025-MTG)\\Mushroom Adventure\\Animated\\Strip And GIF\\space9_4-frames.png").convert()
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
                img = pygame.image.load(f"C:\\Users\\PC\\Desktop\\school apu\\Sem 2\\Imaging and Special Effects (082025-MTG)\\Mushroom Adventure\\character\\mushroom{i}.png").convert_alpha()
                w, h = img.get_size()
                scaled = pygame.transform.scale(img, (int(w * self.scale), int(h * self.scale)))
                self.anim_frames.append(scaled)
        except Exception as e:
            print("Warning: couldn't load player sprites, fallback to circle:", e)
            self.anim_frames = None

    def handle_input(self, dt):
        keys = pygame.key.get_pressed()
        move = pygame.Vector2(0, 0)
        if keys[pygame.K_w]:
            move.y -= 1
        if keys[pygame.K_s]:
            move.y += 1
        if keys[pygame.K_a]:
            move.x -= 1
        if keys[pygame.K_d]:
            move.x += 1
        if move.length_squared() > 0:
            move = move.normalize() * self.speed * dt
        self.pos += move
        self.pos.x = max(30, min(WIDTH - 30, self.pos.x))
        self.pos.y = max(30, min(HEIGHT - 30, self.pos.y))

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
    def __init__(self):
        self.cooldown = 0.15
        self.timer = 0.0
        self.duration = 0.09
        self.active = False
        self.start = pygame.Vector2()
        self.end = pygame.Vector2()
        self.damage = 40

    def try_fire(self, start, mouse_target):
        if self.timer > 0:
            return False
        self.start = start.copy()
        dir = pygame.Vector2(mouse_target - start)
        if dir.length_squared() == 0:
            dir = pygame.Vector2(1, 0)
        else:
            dir = dir.normalize()
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
        pygame.draw.line(glow, (120, 180, 255, 90), self.start, self.end, 22)
        pygame.draw.line(glow, (200, 220, 255, 180), self.start, self.end, 10)
        pygame.draw.line(glow, (255, 255, 255, 230), self.start, self.end, 4)
        pygame.draw.circle(glow, (255, 255, 255, 220), (int(self.start.x), int(self.start.y)), 8)
        surf.blit(glow, (0, 0))


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
            self.particles = [Particle(self.pos) for _ in range(25)]  # 粒子多一点

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


# ---------------- Enemy ----------------
class Enemy:
    def __init__(self, kind="basic"):
        self.kind = kind
        self.pos = pygame.Vector2(random.randint(60, WIDTH - 60), random.randint(-180, -60))
        self.hit_flash = 0.0
        self.dead = False
        self.set_type_stats()
        self.rect = self.image.get_rect(center=(self.pos.x, self.pos.y))

    def set_type_stats(self):
        scale_factor = 0.5
        if self.kind == "basic":
            self.image = pygame.image.load("C:\\Users\\PC\\Desktop\\school apu\\Sem 2\\Imaging and Special Effects (082025-MTG)\\Mushroom Adventure\\character\\mushroom1.png").convert_alpha()
            self.max_hp = 100
            self.speed = 120
            self.score_value = 10
        elif self.kind == "fast":
            self.image = pygame.image.load("C:\\Users\\PC\\Desktop\\school apu\\Sem 2\\Imaging and Special Effects (082025-MTG)\\Mushroom Adventure\\character\\mushroom1.png").convert_alpha()
            self.max_hp = 60
            self.speed = 220
            self.score_value = 18
        elif self.kind == "tank":
            self.image = pygame.image.load("C:\\Users\\PC\\Desktop\\school apu\\Sem 2\\Imaging and Special Effects (082025-MTG)\\Mushroom Adventure\\character\\mushroom1.png").convert_alpha()
            self.max_hp = 220
            self.speed = 70
            self.score_value = 35
        self.hp = self.max_hp
        self.image = pygame.transform.scale(self.image, (int(self.image.get_width() * scale_factor), int(self.image.get_height() * scale_factor)))

    def take_damage(self, dmg):
        if self.dead:
            return None
        self.hp -= dmg
        self.hit_flash = 0.15
        if self.hp <= 0:
            self.hp = 0
            self.dead = True
            return Explosion(self.pos)
        return None

    def update(self, dt):
        if self.dead:
            return
        if self.hit_flash > 0:
            self.hit_flash -= dt
        self.pos.y += self.speed * dt
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def draw(self, surf):
        if self.dead:
            return
        img = self.image.copy()
        if self.hit_flash > 0:
            # ✅ 修正版 tint：只影响非透明像素
            mask = pygame.mask.from_surface(img)
            tint = pygame.Surface(img.get_size(), pygame.SRCALPHA)
            tint.fill((255, 0, 0, 100))
            for y in range(img.get_height()):
                for x in range(img.get_width()):
                    if mask.get_at((x, y)):
                        img.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
                        break
                else:
                    continue
                break
        surf.blit(img, img.get_rect(center=(int(self.pos.x), int(self.pos.y))))


# ---------------- Utility ----------------
def line_segment_rect_intersect(p1, p2, rect):
    return bool(rect.clipline((int(p1.x), int(p1.y), int(p2.x), int(p2.y))))


# ---------------- Game Setup ----------------
player = Player((WIDTH // 2, HEIGHT - 120))
laser = Laser()
enemies = []
explosions = []
spawn_timer = 0.0
score = 0
game_over = False

# ---------------- Main Loop ----------------
running = True
while running:
    dt = clock.tick(60) / 1000.0

    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False
        elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
            running = False
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if not game_over:
                mx, my = pygame.mouse.get_pos()
                if laser.try_fire(player.pos, pygame.Vector2(mx, my)):
                    for en in enemies:
                        if not en.dead and line_segment_rect_intersect(laser.start, laser.end, en.rect):
                            exp = en.take_damage(laser.damage)
                            if exp:
                                explosions.append(exp)
                                score += en.score_value

    if not game_over:
        player.handle_input(dt)
        player.update(dt)
        laser.update(dt)
        spawn_timer += dt
        if spawn_timer > 1.2:
            spawn_timer = 0
            kind = random.choices(["basic", "fast", "tank"], weights=[0.6, 0.3, 0.1])[0]
            enemies.append(Enemy(kind))
        for en in enemies[:]:
            en.update(dt)
            if en.pos.y > HEIGHT + 80:
                enemies.remove(en)
        if score >= 100:
            game_over = True
    else:
        laser.update(dt)
        player.update(dt)

    draw_background(dt)
    player.draw(screen)
    laser.draw(screen)

    for en in enemies:
        en.draw(screen)

    for exp in explosions[:]:
        if not exp.update(dt):
            explosions.remove(exp)
        else:
            exp.draw(screen)

    txt = FONT.render(f"Score: {score}/100", True, (220, 220, 220))
    screen.blit(txt, (12, 10))
    if game_over:
        over = FONT.render("GAME OVER! You reached 100 points!", True, (255, 210, 90))
        screen.blit(over, (WIDTH // 2 - 260, HEIGHT // 2 - 20))

    pygame.display.flip()

pygame.quit()
sys.exit()
