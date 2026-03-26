import pygame
import math
import random
import os

# Initialize Pygame
pygame.init()
pygame.font.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
KNIGHT_COLOR = (200, 50, 50)  
PLAYER_COLOR = (50, 200, 250) 
BASIC_COLOR = (50, 200, 50)   
TANK_COLOR = (20, 100, 20)
RANGED_COLOR = (150, 50, 200)
ORB_COLOR = (255, 215, 0)
PROJ_COLOR = (255, 100, 100)
BOSS_COLOR = (180, 30, 30)
WARNING_COLOR = (255, 80, 80)
BOSS_BAR_BG = (60, 10, 10)
BOSS_BAR_FILL = (220, 40, 40)
BOSS_BAR_BORDER = (255, 230, 230)

# --- IMAGE LOADER SYSTEM ---
def load_sprite(filename, radius):
    try:
        img = pygame.image.load(filename).convert_alpha()
        return pygame.transform.smoothscale(img, (int(radius * 2), int(radius * 2)))
    except FileNotFoundError:
        return None

# --- SHARED DRAW FUNCTION FOR AURAS ---
def draw_entity(surface, x, y, radius, color, sprite):
    # 1. Draw the glowing aura 
    aura_radius = int(radius + 8)
    aura_surface = pygame.Surface((aura_radius * 2, aura_radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(aura_surface, (*color, 90), (aura_radius, aura_radius), aura_radius) 
    surface.blit(aura_surface, (x - aura_radius, y - aura_radius))
    
    # 2. Draw the Leonardo AI Sprite (or fallback circle)
    if sprite:
        surface.blit(sprite, (x - radius, y - radius))
    else:
        pygame.draw.circle(surface, color, (int(x), int(y)), radius)

# --- UI FUNCTIONS ---
def draw_center_warning(screen, font, text):
    warning_surface = font.render(text, True, WARNING_COLOR)
    warning_rect = warning_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(warning_surface, warning_rect)

def draw_boss_health_bar(screen, boss):
    if not boss or boss.hp <= 0:
        return
    bar_width = 420
    bar_height = 24
    bar_x = (WIDTH - bar_width) // 2
    bar_y = 20
    hp_ratio = max(0.0, boss.hp / boss.max_hp)
    fill_width = int(bar_width * hp_ratio)

    pygame.draw.rect(screen, BOSS_BAR_BG, (bar_x, bar_y, bar_width, bar_height))
    pygame.draw.rect(screen, BOSS_BAR_FILL, (bar_x, bar_y, fill_width, bar_height))
    pygame.draw.rect(screen, BOSS_BAR_BORDER, (bar_x, bar_y, bar_width, bar_height), 3)

# --- CORE CLASSES ---
class LifeOrb:
    def __init__(self, x, y):
        self.x = x; self.y = y
        self.radius = 8 # Slightly bigger for the sprite
        self.heal_amount = 10.0
        self.decay_start_ms = None
        self.color = ORB_COLOR
        self.sprite = load_sprite("orb.png", self.radius)

    def draw(self, surface):
        draw_entity(surface, self.x, self.y, self.radius, self.color, self.sprite)

class Projectile:
    def __init__(self, x, y, target_x, target_y):
        self.x = x; self.y = y
        self.speed = 5
        self.radius = 4
        self.damage = 1.0 
        dx, dy = target_x - x, target_y - y
        dist = math.hypot(dx, dy)
        self.vx = (dx / dist) * self.speed if dist > 0 else 0
        self.vy = (dy / dist) * self.speed if dist > 0 else 0

    def update(self):
        self.x += self.vx
        self.y += self.vy

    def draw(self, surface):
        pygame.draw.circle(surface, PROJ_COLOR, (int(self.x), int(self.y)), self.radius)

class Enemy:
    def __init__(self, x, y, hp, speed, damage, radius, color, sprite_name):
        self.x = x; self.y = y
        self.hp = hp
        self.speed = speed
        self.damage = damage
        self.radius = radius
        self.color = color
        self.sprite = load_sprite(sprite_name, radius)

    def move_towards(self, target_x, target_y):
        dx, dy = target_x - self.x, target_y - self.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed

    def draw(self, surface):
        draw_entity(surface, self.x, self.y, self.radius, self.color, self.sprite)

class BasicEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, hp=10, speed=1.0, damage=3.0, radius=12, color=BASIC_COLOR, sprite_name="basic.png")

class TankEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, hp=30, speed=0.4, damage=6.0, radius=18, color=TANK_COLOR, sprite_name="tank.png")

class RangedEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, hp=10, speed=0.7, damage=1.5, radius=12, color=RANGED_COLOR, sprite_name="ranged.png")
        self.shoot_cooldown = 0

    def update_ranged(self, knight, projectiles):
        self.move_towards(knight.x, knight.y)
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        elif math.dist((self.x, self.y), (knight.x, knight.y)) < 300:
            projectiles.append(Projectile(self.x, self.y, knight.x, knight.y))
            self.shoot_cooldown = 45 

class BossEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, hp=350, speed=0.55, damage=10.0, radius=35, color=BOSS_COLOR, sprite_name="boss.png")
        self.max_hp = self.hp

class RecklessKnight:
    def __init__(self, x, y):
        self.x = x; self.y = y
        self.speed = 2.5 
        self.radius = 18 # Scaled up slightly for the sprite
        self.max_hp = 100.0
        self.hp = self.max_hp
        self.combat_focus_radius = 130
        self.color = KNIGHT_COLOR
        self.sprite = load_sprite("knight.png", self.radius)

    def find_closest_enemy(self, enemies):
        if not enemies: return None
        return min(enemies, key=lambda e: math.dist((self.x, self.y), (e.x, e.y)))

    def find_densest_enemy_cluster(self, enemies):
        if not enemies: return None
        best_target = None
        max_neighbors = -1
        for enemy in enemies:
            neighbors = sum(1 for e in enemies if math.dist((enemy.x, enemy.y), (e.x, e.y)) < 150)
            if neighbors > max_neighbors:
                max_neighbors = neighbors
                best_target = enemy
        return best_target

    def update(self, enemies, orbs, projectiles):
        for proj in projectiles[:]:
            if math.dist((self.x, self.y), (proj.x, proj.y)) < self.radius + proj.radius:
                self.hp -= proj.damage
                projectiles.remove(proj)

        engaged_enemies = []
        for enemy in enemies[:]:
            enemy_dist = math.dist((self.x, self.y), (enemy.x, enemy.y))
            if enemy_dist <= self.combat_focus_radius:
                engaged_enemies.append(enemy)
            if enemy_dist < self.radius + enemy.radius:
                self.hp -= enemy.damage 
                enemy.hp -= 10 
                if enemy.hp <= 0:
                    enemies.remove(enemy)
                    orbs.append(LifeOrb(enemy.x, enemy.y)) 
                    self.x += (self.x - enemy.x) * 0.5 
                    self.y += (self.y - enemy.y) * 0.5

        target = self.find_closest_enemy(engaged_enemies) if engaged_enemies else self.find_densest_enemy_cluster(enemies)
        if target and self.hp > 0:
            dx, dy = target.x - self.x, target.y - self.y
            dist = math.hypot(dx, dy)
            if dist > 0:
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed

    def draw(self, surface):
        if self.hp > 0:
            draw_entity(surface, self.x, self.y, self.radius, self.color, self.sprite)
        pygame.draw.rect(surface, (100, 0, 0), (self.x - 20, self.y - 30, 40, 5))
        pygame.draw.rect(surface, (0, 255, 0), (self.x - 20, self.y - 30, 40 * max(0, self.hp) / self.max_hp, 5))

class SupportPlayer:
    def __init__(self, x, y):
        self.x = x; self.y = y
        self.speed = 6 
        self.radius = 12
        self.pulse_radius = 150
        self.pulse_cooldown = 0
        self.color = PLAYER_COLOR
        self.sprite = load_sprite("player.png", self.radius)

    def handle_input(self, keys):
        if keys[pygame.K_w] or keys[pygame.K_UP]: self.y -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: self.y += self.speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: self.x -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: self.x += self.speed
        self.x = max(self.radius, min(WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(HEIGHT - self.radius, self.y))

    def trigger_pulse(self, enemies, knight, projectiles):
        if self.pulse_cooldown == 0 and knight.hp > 0:
            knight.hp -= knight.hp * 0.05
            for enemy in enemies:
                dist = math.dist((self.x, self.y), (enemy.x, enemy.y))
                if dist < self.pulse_radius:
                    dx, dy = enemy.x - self.x, enemy.y - self.y
                    if dist > 0:
                        enemy.x += (dx / dist) * 100 
                        enemy.y += (dy / dist) * 100
            
            for proj in projectiles[:]:
                if math.dist((self.x, self.y), (proj.x, proj.y)) < self.pulse_radius:
                    projectiles.remove(proj)
            self.pulse_cooldown = 60 

    def update(self, orbs, knight):
        if self.pulse_cooldown > 0: self.pulse_cooldown -= 1
        for orb in orbs[:]:
            if math.dist((self.x, self.y), (orb.x, orb.y)) < self.radius + orb.radius:
                orbs.remove(orb)
                knight.hp = min(knight.max_hp, knight.hp + orb.heal_amount)

    def draw(self, surface):
        draw_entity(surface, self.x, self.y, self.radius, self.color, self.sprite)
        if self.pulse_cooldown == 0:
            pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.pulse_radius, 1)

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("The Unsung Hero - Full Integration")
    clock = pygame.time.Clock()
    warning_font = pygame.font.SysFont("Arial Black", 64, bold=True)

    knight = RecklessKnight(WIDTH // 2, HEIGHT // 2)
    player = SupportPlayer(WIDTH // 2 - 50, HEIGHT // 2)
    
    enemies = []
    orbs = []
    projectiles = []
    
    start_ticks = pygame.time.get_ticks()
    spawn_timer = 0
    ORB_DECAY_MS = 12000
    TANK_PHASE_SECONDS = 45
    BOSS_SPAWN_SECONDS = 150
    WARNING_DURATION_SECONDS = 3
    boss_spawned = False

    running = True
    while running:
        now_ticks = pygame.time.get_ticks()
        seconds_survived = (now_ticks - start_ticks) / 1000.0
        tank_phase_active = seconds_survived >= TANK_PHASE_SECONDS

        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.trigger_pulse(enemies, knight, projectiles)

        # ESCALATING WAVE SPAWNER
        spawn_timer += 1
        current_spawn_rate = max(15, 60 - int(seconds_survived * 0.5)) 
        
        if spawn_timer > current_spawn_rate:
            spawn_x = random.choice([random.randint(-50, 0), random.randint(WIDTH, WIDTH + 50)])
            spawn_y = random.randint(0, HEIGHT)
            
            rand_val = random.random()
            if seconds_survived > 45 and rand_val < 0.15: 
                enemies.append(TankEnemy(spawn_x, spawn_y))
            elif seconds_survived > 20 and rand_val < 0.35:
                enemies.append(RangedEnemy(spawn_x, spawn_y))
            else:
                enemies.append(BasicEnemy(spawn_x, spawn_y))
            
            spawn_timer = 0
        
        # Spawn a boss once
        if not boss_spawned and seconds_survived >= BOSS_SPAWN_SECONDS:
            enemies.append(BossEnemy(WIDTH // 2, -40))
            boss_spawned = True

        # Update Entities
        player.handle_input(keys)
        player.update(orbs, knight)
        
        for enemy in enemies:
            if isinstance(enemy, RangedEnemy):
                enemy.update_ranged(knight, projectiles)
            else:
                enemy.move_towards(knight.x, knight.y)
                
        for proj in projectiles[:]:
            proj.update()
            if proj.x < 0 or proj.x > WIDTH or proj.y < 0 or proj.y > HEIGHT:
                projectiles.remove(proj)

        if tank_phase_active:
            for orb in orbs[:]:
                if orb.decay_start_ms is None:
                    orb.decay_start_ms = now_ticks
                elif now_ticks - orb.decay_start_ms >= ORB_DECAY_MS:
                    orbs.remove(orb)

        knight.update(enemies, orbs, projectiles)
        current_boss = next((enemy for enemy in enemies if isinstance(enemy, BossEnemy) and enemy.hp > 0), None)

        # Draw
        screen.fill(BLACK)
        for orb in orbs: orb.draw(screen)
        for proj in projectiles: proj.draw(screen)
        for enemy in enemies: enemy.draw(screen)
        knight.draw(screen)
        player.draw(screen)

        if current_boss:
            draw_boss_health_bar(screen, current_boss)

        # Flash warnings
        tank_warning_active = TANK_PHASE_SECONDS <= seconds_survived < (TANK_PHASE_SECONDS + WARNING_DURATION_SECONDS)
        boss_warning_active = BOSS_SPAWN_SECONDS <= seconds_survived < (BOSS_SPAWN_SECONDS + WARNING_DURATION_SECONDS)
        if (tank_warning_active or boss_warning_active) and int(seconds_survived * 6) % 2 == 0:
            if boss_warning_active:
                draw_center_warning(screen, warning_font, "BOSS INCOMING")
            else:
                draw_center_warning(screen, warning_font, "TANK PHASE")

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()