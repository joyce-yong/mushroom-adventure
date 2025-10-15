# laser_fx_full.py
# Run: pip install pygame
# Then: python laser_fx_full.py

import pygame
import random
import math
import sys
import subprocess


pygame.init()

WIDTH, HEIGHT = 900, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Laser Beam")
FONT = pygame.font.SysFont("consolas", 20)


# ---------------- Player & Laser ----------------
class Player:
    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        self.speed = 300

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

    def draw(self, surf):
        pygame.draw.circle(surf, (255, 255, 255), (int(self.pos.x), int(self.pos.y)), 16)


def ray_to_screen_edge(start, direction):
    eps = 1e-6
    candidates = []

    # vertical edges x = 0 and x = WIDTH
    if abs(direction.x) > eps:
        t = (0 - start.x) / direction.x
        if t > 0:
            y = start.y + direction.y * t
            if -1 <= y <= HEIGHT + 1:
                candidates.append(t)
        t = (WIDTH - start.x) / direction.x
        if t > 0:
            y = start.y + direction.y * t
            if -1 <= y <= HEIGHT + 1:
                candidates.append(t)

    # horizontal edges y = 0 and y = HEIGHT
    if abs(direction.y) > eps:
        t = (0 - start.y) / direction.y
        if t > 0:
            x = start.x + direction.x * t
            if -1 <= x <= WIDTH + 1:
                candidates.append(t)
        t = (HEIGHT - start.y) / direction.y
        if t > 0:
            x = start.x + direction.x * t
            if -1 <= x <= WIDTH + 1:
                candidates.append(t)

    if not candidates:
        return start + direction * 2000  # fallback
    t_min = min(candidates)
    return start + direction * t_min


class Laser:
    def __init__(self):
        self.cooldown = 0.18  # 更短冷却
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
        # big glow light
        glow = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.line(glow, (120, 180, 255, 90), (int(self.start.x), int(self.start.y)),
                         (int(self.end.x), int(self.end.y)), 22)
        # inner light (blue)
        pygame.draw.line(glow, (200, 220, 255, 180), (int(self.start.x), int(self.start.y)),
                         (int(self.end.x), int(self.end.y)), 10)
        # middle white
        pygame.draw.line(glow, (255, 255, 255, 230), (int(self.start.x), int(self.start.y)),
                         (int(self.end.x), int(self.end.y)), 4)
        # start light
        pygame.draw.circle(glow, (255, 255, 255, 220), (int(self.start.x), int(self.start.y)), 8)
        surf.blit(glow, (0, 0))


# ---------------- Particles ----------------
class SparkParticle:

    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        angle = random.uniform(-math.pi, math.pi)
        speed = random.uniform(80, 320)
        self.vel = pygame.Vector2(math.cos(angle), math.sin(angle)) * speed
        self.life = random.uniform(0.12, 0.35)
        self.max_life = self.life
        # Blue-yellow mix palette
        self.color = random.choice([(255, 200, 80), (200, 220, 255), (255, 230, 120)])

    def update(self, dt):
        self.life -= dt
        self.pos += self.vel * dt
        # quick damping
        self.vel *= 0.87
        # gravity pull slightly (for yellow sparks)
        self.vel.y += 180 * dt * 0.3

    def draw(self, surf):
        if self.life <= 0:
            return
        a = int(255 * (self.life / self.max_life))
        size = int(2 + 3 * (self.life / self.max_life))
        s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, a), (size, size), size)
        surf.blit(s, (self.pos.x - size, self.pos.y - size))


class ExplosionParticle:

    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        angle = random.uniform(0, math.tau)
        speed = random.uniform(40, 260)
        self.vel = pygame.Vector2(math.cos(angle), math.sin(angle)) * speed
        self.life = random.uniform(0.6, 1.1)
        self.max_life = self.life
        self.color = random.choice([(255, 140, 40), (255, 210, 120), (160, 160, 160)])  # embers + debris

    def update(self, dt):
        self.life -= dt
        self.vel.y += 300 * dt * 0.4  # gravity
        self.pos += self.vel * dt
        self.vel *= 0.96

    def draw(self, surf):
        if self.life <= 0:
            return
        a = int(255 * max(0, self.life / self.max_life))
        size = int(3 + 4 * (self.life / self.max_life))
        s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, a), (size, size), size)
        surf.blit(s, (self.pos.x - size, self.pos.y - size))


# ---------------- Enemy (multi-class) ----------------
class Enemy:
    def __init__(self, kind="basic"):
        self.kind = kind
        self.pos = pygame.Vector2(random.randint(60, WIDTH - 60), random.randint(-180, -60))
        self.hit_flash = 0.0
        self.shake_time = 0.0
        self.dead = False
        self.explode_time = 0.6
        self.set_type_stats()

    def set_type_stats(self):
        if self.kind == "basic":
            self.color = (180, 220, 80)
            self.max_hp = 100
            self.speed = 120
            self.score_value = 10
            self.size = 44
        elif self.kind == "fast":
            self.color = (100, 200, 255)
            self.max_hp = 60
            self.speed = 220
            self.score_value = 18
            self.size = 36
        elif self.kind == "tank":
            self.color = (220, 120, 100)
            self.max_hp = 220
            self.speed = 70
            self.score_value = 35
            self.size = 56
        self.hp = self.max_hp
        self.rect = pygame.Rect(self.pos.x - self.size / 2, self.pos.y - self.size / 2, self.size, self.size)

    def take_damage(self, dmg):
        if self.dead:
            return
        self.hp -= dmg
        self.hit_flash = 0.22
        self.shake_time = 0.16
        if self.hp <= 0:
            self.hp = 0
            self.dead = True

    def update(self, dt):
        if self.dead:
            self.explode_time -= dt
            return
        if self.hit_flash > 0:
            self.hit_flash -= dt
        if self.shake_time > 0:
            self.shake_time -= dt
        self.pos.y += self.speed * dt
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def draw(self, surf):
        if self.dead:
            # draw a quick puff to hint explosion center (visual)
            r = int(self.size * (1.0 + (0.6 - self.explode_time / 0.6)))
            pygame.draw.circle(surf, (180, 120, 60), (int(self.pos.x), int(self.pos.y)), r, 0)
            return

        color = (255, 100, 100) if self.hit_flash > 0 else self.color
        # shake
        offset_x = random.uniform(-3, 3) if self.shake_time > 0 else 0
        offset_y = random.uniform(-3, 3) if self.shake_time > 0 else 0
        r = pygame.Rect(int(self.pos.x - self.size / 2 + offset_x), int(self.pos.y - self.size / 2 + offset_y),
                        int(self.size), int(self.size))
        pygame.draw.rect(surf, color, r)
        # hp bar
        hp_ratio = max(0.0, self.hp / self.max_hp)
        pygame.draw.rect(surf, (0, 0, 0), (r.left, r.top - 8, self.size, 6))
        pygame.draw.rect(surf, (255, 0, 0), (r.left + 1, r.top - 7, int((self.size - 2) * hp_ratio), 4))


# ---------------- Utility ----------------
def line_segment_rect_intersect(p1, p2, rect):
    return bool(rect.clipline((int(p1.x), int(p1.y), int(p2.x), int(p2.y))))


# ---------------- Game Setup ----------------
player = Player((WIDTH // 2, HEIGHT - 120))
laser = Laser()
enemies = []
sparks = []  # spark particles for hit effect
explosions = []  # explosion particles for death
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
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                running = False
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if not game_over:
                mx, my = pygame.mouse.get_pos()
                if laser.try_fire(player.pos, pygame.Vector2(mx, my)):
                    # apply damage and spawn spark effects (blue/yellow)
                    for en in enemies:
                        if not en.dead and line_segment_rect_intersect(laser.start, laser.end, en.rect):
                            # per-hit
                            en.take_damage(laser.damage)
                            # spark burst: several short bright sparks
                            for _ in range(random.randint(8, 18)):
                                sparks.append(SparkParticle(en.pos))
                            # small white flash circle

    # Update
    if not game_over:
        player.handle_input(dt)
        laser.update(dt)
        spawn_timer += dt
        if spawn_timer > 0.9:
            spawn_timer = 0
            kind = random.choices(["basic", "fast", "tank"], weights=[0.6, 0.3, 0.1])[0]
            enemies.append(Enemy(kind))

        for en in enemies[:]:
            en.update(dt)
            if en.dead and en.explode_time <= 0:
                # spawn explosion particles (bigger, mixed debris + fire)
                for _ in range(18 + int(en.size / 4)):
                    explosions.append(ExplosionParticle(en.pos))
                score += en.score_value
                enemies.remove(en)
                if score >= 100:
                    game_over = True
            elif en.pos.y > HEIGHT + 80:
                enemies.remove(en)
    else:
        laser.update(dt)

    # update particles
    for s in sparks[:]:
        s.update(dt)
        if s.life <= 0:
            sparks.remove(s)
    for ex in explosions[:]:
        ex.update(dt)
        if ex.life <= 0:
            explosions.remove(ex)

    # Draw
    screen.fill((12, 14, 20))
    # subtle grid
    for x in range(0, WIDTH, 64):
        pygame.draw.line(screen, (10, 10, 12), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, 64):
        pygame.draw.line(screen, (10, 10, 12), (0, y), (WIDTH, y))

    player.draw(screen)
    laser.draw(screen)
    for en in enemies:
        en.draw(screen)

    # draw sparks and explosions (sparks first so explosion overlays)
    for s in sparks:
        s.draw(screen)
    for ex in explosions:
        ex.draw(screen)

    # UI
    txt = FONT.render(f"Score: {score}/100", True, (210, 210, 210))
    screen.blit(txt, (12, 10))
    if game_over:
        over = FONT.render("GAME OVER! You reached 100 points!", True, (255, 210, 90))
        sub = FONT.render("Press ESC to quit.", True, (180, 180, 180))
        screen.blit(over, (WIDTH // 2 - 170, HEIGHT // 2 - 20))
        screen.blit(sub, (WIDTH // 2 - 70, HEIGHT // 2 + 10))

    pygame.display.flip()

pygame.quit()
sys.exit()
