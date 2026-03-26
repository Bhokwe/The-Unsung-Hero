import pygame
import math
import random
import os

# Initialize Pygame and Mixer for Audio
pygame.init()
pygame.font.init()
pygame.mixer.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
KNIGHT_COLOR = (200, 50, 50)  
PLAYER_COLOR = (50, 200, 250) 
BASIC_COLOR = (50, 200, 50)   
TANK_COLOR = (255, 120, 0)
RANGED_COLOR = (150, 50, 200)
ORB_COLOR = (255, 215, 0)
PROJ_COLOR = (255, 100, 100)
BOSS_COLOR = (180, 30, 30)
WARNING_COLOR = (255, 80, 80)
BOSS_BAR_BG = (60, 10, 10)
BOSS_BAR_FILL = (220, 40, 40)
BOSS_BAR_BORDER = (255, 230, 230)

# --- AUDIO LOADER SYSTEM ---
def play_music(filename):
    try:
        pygame.mixer.music.load(filename)
        pygame.mixer.music.set_volume(0.25)  # Master volume for background music
        pygame.mixer.music.play(-1) # -1 makes it loop infinitely
    except (pygame.error, FileNotFoundError):
        # Silently fail if the music files aren't in the folder yet
        pass

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

    def draw(self, surface, ox=0, oy=0):
        pygame.draw.circle(surface, PROJ_COLOR, (int(self.x + ox), int(self.y + oy)), self.radius)

class Enemy:
    def __init__(self, x, y, hp, speed, damage, radius, color, sprite_name):
        self.x = x; self.y = y
        self.hp = hp
        self.base_speed = float(speed)
        self.speed = float(speed)
        self.damage = damage
        self.radius = radius
        self.color = color
        self.hit_flash_until_ticks = 0
        self.sprite = load_sprite(sprite_name, radius)

    def move_towards(self, target_x, target_y):
        dx, dy = target_x - self.x, target_y - self.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed

    def draw(self, surface, ox=0, oy=0, now_ticks=0):
        # Contact-damage VFX: briefly flash when hit.
        draw_color = self.color
        if now_ticks < self.hit_flash_until_ticks:
            draw_color = (200, 80, 255)  # enemy hit flash (vivid purple)
        draw_entity(surface, self.x + ox, self.y + oy, self.radius, draw_color, self.sprite)

class BasicEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, hp=10, speed=1.0, damage=3.0, radius=12, color=BASIC_COLOR, sprite_name="basic.png")

class TankEnemy(Enemy):
    def __init__(self, x, y):
        # Contact damage tuned so Tank Phase isn't instantly lethal.
        super().__init__(x, y, hp=60, speed=0.4, damage=9.6, radius=18, color=TANK_COLOR, sprite_name="tank.png")

class RangedEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, hp=10, speed=0.7, damage=1.5, radius=12, color=RANGED_COLOR, sprite_name="ranged.png")
        self.shoot_cooldown = 0

    def update_ranged(self, knight, projectiles, on_shot=None):
        self.move_towards(knight.x, knight.y)
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        elif math.dist((self.x, self.y), (knight.x, knight.y)) < 300:
            projectiles.append(Projectile(self.x, self.y, knight.x, knight.y))
            self.shoot_cooldown = 45 
            if on_shot:
                on_shot()

class BossEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, hp=350, speed=0.55, damage=10.0, radius=35, color=BOSS_COLOR, sprite_name="boss.png")
        self.max_hp = self.hp
        self.stunned_until_ticks = 0
        self.stun_knockback_pending = False

class RagePickup:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 12
        self.color = (255, 70, 70)

    def draw(self, surface, ox=0, oy=0):
        points = [
            (self.x + ox, self.y + oy - self.radius),
            (self.x + ox + self.radius, self.y + oy),
            (self.x + ox, self.y + oy + self.radius),
            (self.x + ox - self.radius, self.y + oy),
        ]
        pygame.draw.polygon(surface, self.color, points)
        pygame.draw.polygon(surface, (255, 180, 180), points, 2)

class StunPickup:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 12
        self.color = (70, 170, 255)

    def draw(self, surface, ox=0, oy=0):
        points = [
            (self.x + ox, self.y + oy - self.radius),
            (self.x + ox + self.radius, self.y + oy),
            (self.x + ox, self.y + oy + self.radius),
            (self.x + ox - self.radius, self.y + oy),
        ]
        pygame.draw.polygon(surface, self.color, points)
        pygame.draw.polygon(surface, (180, 220, 255), points, 2)

class SplashPickup:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 12
        self.color = (255, 160, 40)

    def draw(self, surface, ox=0, oy=0):
        # Orange triangle/diamond pickup.
        points = [
            (self.x + ox, self.y + oy - self.radius),
            (self.x + ox + self.radius, self.y + oy),
            (self.x + ox, self.y + oy + self.radius),
            (self.x + ox - self.radius, self.y + oy),
        ]
        pygame.draw.polygon(surface, self.color, points)
        pygame.draw.polygon(surface, (255, 220, 160), points, 2)

class RecklessKnight:
    def __init__(self, x, y):
        self.x = x; self.y = y
        self.base_speed = 2.5
        self.speed = 2.5 
        self.radius = 18 # Scaled up slightly for the sprite
        self.max_hp = 100.0
        self.hp = self.max_hp
        self.combat_focus_radius = 130
        self.base_color = KNIGHT_COLOR
        self.color = KNIGHT_COLOR
        self.hit_flash_until_ticks = 0
        self.last_hit_sfx_ticks = 0
        self.splash_damage_end_ticks = 0
        self.splash_ring_until_ticks = 0
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

    def update(
        self,
        enemies,
        orbs,
        projectiles,
        speed_mult=1.0,
        contact_damage_mult=1.0,
        knight_phase_speed_mult=1.0,
        on_kill=None,
        now_ticks=0,
        orb_drop_chance=1.0,
        on_contact_damage_sfx=None,
    ):
        self.speed = self.base_speed * float(knight_phase_speed_mult) * float(speed_mult)
        for proj in projectiles[:]:
            if math.dist((self.x, self.y), (proj.x, proj.y)) < self.radius + proj.radius:
                self.hp -= proj.damage
                projectiles.remove(proj)

        engaged_enemies = []
        splash_active = now_ticks < self.splash_damage_end_ticks
        contact_deal_damage = 10.0
        splash_radius = 90.0
        splash_secondary_damage = contact_deal_damage * 0.7
        # +10% LifeOrb sustain on the normal baseline drops.
        # When `orb_drop_chance` is reduced (Boss Phase), we keep the original reduction.
        orb_extra_chance = 0.1 if float(orb_drop_chance) >= 0.999 else 0.0

        def try_kill_enemy(victim, apply_knockback=False):
            # Guard: victim might already be removed by earlier splash checks.
            if victim not in enemies:
                return
            if on_kill:
                on_kill(victim)
            enemies.remove(victim)
            if random.random() < orb_drop_chance:
                orbs.append(LifeOrb(victim.x, victim.y))
                if random.random() < orb_extra_chance:
                    orbs.append(LifeOrb(victim.x, victim.y))
            if apply_knockback:
                self.x += (self.x - victim.x) * 0.5
                self.y += (self.y - victim.y) * 0.5

        for enemy in enemies[:]:
            if enemy not in enemies:
                continue
            enemy_dist = math.dist((self.x, self.y), (enemy.x, enemy.y))
            if enemy_dist <= self.combat_focus_radius:
                engaged_enemies.append(enemy)
            if enemy_dist < self.radius + enemy.radius:
                can_deal_damage = not (isinstance(enemy, BossEnemy) and now_ticks < enemy.stunned_until_ticks)
                if can_deal_damage:
                    self.hp -= enemy.damage * float(contact_damage_mult)
                    # Contact-damage SFX: throttle so it doesn't spam while touching enemies.
                    if on_contact_damage_sfx and (now_ticks - self.last_hit_sfx_ticks) > 120:
                        on_contact_damage_sfx()
                        self.last_hit_sfx_ticks = now_ticks
                enemy.hp -= contact_deal_damage
                # Contact-damage VFX: flash the Knight and the struck enemy.
                self.hit_flash_until_ticks = max(self.hit_flash_until_ticks, now_ticks + 90)
                enemy.hit_flash_until_ticks = max(enemy.hit_flash_until_ticks, now_ticks + 90)

                if splash_active:
                    # Splash Damage: apply secondary contact damage around the primary target.
                    self.splash_ring_until_ticks = max(self.splash_ring_until_ticks, now_ticks + 18)  # ~1 frame at 60 FPS
                    for other in enemies[:]:
                        if other is enemy:
                            continue
                        if other not in enemies:
                            continue
                        if math.dist((other.x, other.y), (enemy.x, enemy.y)) <= splash_radius:
                            other.hp -= splash_secondary_damage
                            other.hit_flash_until_ticks = max(other.hit_flash_until_ticks, now_ticks + 90)
                            # Chaos polish: splash also "shoves" nearby enemies away from the primary target.
                            dx2, dy2 = other.x - enemy.x, other.y - enemy.y
                            d2 = math.hypot(dx2, dy2)
                            if d2 > 0:
                                shove_dist = 55
                                other.x += (dx2 / d2) * shove_dist
                                other.y += (dy2 / d2) * shove_dist
                                other.x = max(other.radius, min(WIDTH - other.radius, other.x))
                                other.y = max(other.radius, min(HEIGHT - other.radius, other.y))
                            if other.hp <= 0:
                                try_kill_enemy(other, apply_knockback=False)

                if enemy.hp <= 0:
                    try_kill_enemy(enemy, apply_knockback=True)

        target = self.find_closest_enemy(engaged_enemies) if engaged_enemies else self.find_densest_enemy_cluster(enemies)
        if target and self.hp > 0:
            dx, dy = target.x - self.x, target.y - self.y
            dist = math.hypot(dx, dy)
            if dist > 0:
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed

    def draw(self, surface, rage_active=False, now_ticks=0, ox=0, oy=0):
        if self.hp > 0:
            if now_ticks < self.hit_flash_until_ticks:
                # Contact-damage VFX: brief white-hot flash on the Knight.
                draw_entity(surface, self.x + ox, self.y + oy, self.radius, (80, 255, 255), self.sprite)  # bright cyan
            elif rage_active:
                # Rage Mode aura pulses bright red to signal power.
                pulse = 0.5 + 0.5 * math.sin(now_ticks / 85.0)
                rage_color = (255, int(40 + 60 * (1.0 - pulse)), int(40 + 60 * (1.0 - pulse)))
                draw_entity(surface, self.x + ox, self.y + oy, self.radius, rage_color, self.sprite)
            else:
                draw_entity(surface, self.x + ox, self.y + oy, self.radius, self.base_color, self.sprite)
            if now_ticks < self.splash_ring_until_ticks:
                # Splash Damage VFX: hollow orange circles expand for one quick strike cue.
                cx, cy = int(self.x + ox), int(self.y + oy)
                remaining = max(0, int(self.splash_ring_until_ticks - now_ticks))
                total = 18  # keep in sync with the ~1 frame timing in `update()`
                factor = 1.0 - (remaining / float(total))
                r1 = int(40 + 20 * factor)
                r2 = int(60 + 20 * factor)
                pygame.draw.circle(surface, (255, 170, 60), (cx, cy), r1, 2)
                pygame.draw.circle(surface, (255, 120, 0), (cx, cy), r2, 2)
        pygame.draw.rect(surface, (100, 0, 0), (self.x + ox - 20, self.y + oy - 30, 40, 5))
        pygame.draw.rect(surface, (0, 255, 0), (self.x + ox - 20, self.y + oy - 30, 40 * max(0, self.hp) / self.max_hp, 5))

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

    def trigger_pulse(self, enemies, knight, projectiles, on_pulse_sfx=None):
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
            if on_pulse_sfx:
                on_pulse_sfx()

    def update(self, orbs, knight, on_orb_collected=None):
        if self.pulse_cooldown > 0: self.pulse_cooldown -= 1
        for orb in orbs[:]:
            if math.dist((self.x, self.y), (orb.x, orb.y)) < self.radius + orb.radius:
                orbs.remove(orb)
                knight.hp = min(knight.max_hp, knight.hp + orb.heal_amount)
                if on_orb_collected:
                    on_orb_collected()

    def draw(self, surface, ox=0, oy=0):
        draw_entity(surface, self.x + ox, self.y + oy, self.radius, self.color, self.sprite)
        if self.pulse_cooldown == 0:
            pygame.draw.circle(surface, WHITE, (int(self.x + ox), int(self.y + oy)), self.pulse_radius, 1)

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("The Unsung Hero - Full Integration")
    clock = pygame.time.Clock()
    warning_font = pygame.font.SysFont("Arial Black", 64, bold=True)
    ui_font = pygame.font.SysFont("Arial", 24, bold=True)
    game_over_font = pygame.font.SysFont("Arial Black", 48, bold=True)
    sub_font = pygame.font.SysFont("Arial", 26, bold=True)
    title_font = pygame.font.SysFont("Arial Black", 56, bold=True)
    menu_font = pygame.font.SysFont("Arial", 32, bold=True)

    # --- NEW: LOAD BACKGROUND ---
    try:
        bg_img = pygame.image.load("background.jpg").convert() # Change to .png if needed
        bg_img = pygame.transform.smoothscale(bg_img, (WIDTH, HEIGHT))
        
        # Create a dimming overlay so your sprites and auras still pop
        bg_dimmer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        bg_dimmer.fill((0, 0, 0, 140)) # 140 is the darkness level (0-255)
    except FileNotFoundError:
        bg_img = None
    # ----------------------------

    ORB_DECAY_MS = 12000
    TANK_PHASE_SECONDS = 45
    BOSS_SPAWN_SECONDS = 150
    WARNING_DURATION_SECONDS = 3

    # Core loop systems (persist across restarts)
    high_score = 0

    def safe_sound(filename, volume=1.0):
        try:
            snd = pygame.mixer.Sound(filename)
            snd.set_volume(volume)
            return snd
        except (pygame.error, FileNotFoundError):
            return None

    def safe_sound_fallback(mp3_filename, wav_filename, volume=1.0):
        # Try MP3 first (your newer assets), then WAV as fallback.
        snd = safe_sound(mp3_filename, volume)
        if snd is None:
            snd = safe_sound(wav_filename, volume)
        return snd

    sfx = {
        "sword": safe_sound("sword.mp3", 0.55),
        "arrow": safe_sound("arrow.mp3", 0.45),
        "death": safe_sound_fallback("death.mp3", "death.wav", 0.65),
        "pulse": safe_sound("pulse.mp3", 0.6),
        "rage": safe_sound("rage.mp3", 0.65),
        "stun": safe_sound("stun.mp3", 0.65),
        "orb": safe_sound_fallback("orb.mp3", "orb.wav", 0.3),
        "hit": safe_sound_fallback("hit.mp3", "hit.wav", 0.3),
    }
    # Master SFX volume (30%).
    for snd in sfx.values():
        if snd:
            snd.set_volume(0.3)

    def play_sfx(name):
        sound = sfx.get(name)
        if sound:
            sound.play()

    current_music = None

    def set_music(tag, filename):
        nonlocal current_music
        if current_music != tag:
            current_music = tag
            play_music(filename)

    def reset_run():
        knight = RecklessKnight(WIDTH // 2, HEIGHT // 2)
        player = SupportPlayer(WIDTH // 2 - 50, HEIGHT // 2)
        enemies = []
        orbs = []
        projectiles = []
        rage_pickups = []
        stun_pickups = []
        splash_pickups = []
        start_ticks = pygame.time.get_ticks()
        spawn_timer = 0
        boss_spawned = False

        score = 0.0
        rage_end_ticks = 0
        tank_phase_kills = 0
        last_rage_drop_ticks = -10000
        rage_pickup_cooldown_ms = 10000
        next_stun_spawn_ticks = 0
        next_splash_spawn_ticks = 0

        # Small combat polish: brief screen-shake on kills for extra impact/chaos.
        shake_until_ticks = 0
        shake_mag = 0.0
        last_sword_sfx_ticks = 0
        death_sfx_played = False

        return {
            "knight": knight,
            "player": player,
            "enemies": enemies,
            "orbs": orbs,
            "projectiles": projectiles,
            "rage_pickups": rage_pickups,
            "stun_pickups": stun_pickups,
            "splash_pickups": splash_pickups,
            "start_ticks": start_ticks,
            "spawn_timer": spawn_timer,
            "boss_spawned": boss_spawned,
            "score": score,
            "rage_end_ticks": rage_end_ticks,
            "tank_phase_kills": tank_phase_kills,
            "last_rage_drop_ticks": last_rage_drop_ticks,
            "rage_pickup_cooldown_ms": rage_pickup_cooldown_ms,
            "next_stun_spawn_ticks": next_stun_spawn_ticks,
            "next_splash_spawn_ticks": next_splash_spawn_ticks,
            "shake_until_ticks": shake_until_ticks,
            "shake_mag": shake_mag,
            "last_sword_sfx_ticks": last_sword_sfx_ticks,
            "death_sfx_played": death_sfx_played,
        }

    run = reset_run()
    game_state = "MAIN_MENU"  # MAIN_MENU | RULES | RUNNING | PAUSED | GAME_OVER
    set_music("menu", "menu.mp3")

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        now_ticks = pygame.time.get_ticks()
        seconds_survived = (now_ticks - run["start_ticks"]) / 1000.0
        tank_phase_active = seconds_survived >= TANK_PHASE_SECONDS

        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game_state == "MAIN_MENU":
                        run = reset_run()
                        game_state = "RUNNING"
                        set_music("run", "triumphant.mp3")
                    elif game_state == "RUNNING":
                        run["player"].trigger_pulse(
                            run["enemies"],
                            run["knight"],
                            run["projectiles"],
                            on_pulse_sfx=lambda: play_sfx("pulse"),
                        )
                if event.key == pygame.K_r and game_state == "MAIN_MENU":
                    game_state = "RULES"
                if event.key == pygame.K_r:
                    if game_state == "GAME_OVER":
                        run = reset_run()
                        game_state = "RUNNING"
                        set_music("run", "triumphant.mp3")
                if event.key == pygame.K_m and game_state == "RULES":
                    game_state = "MAIN_MENU"
                    set_music("menu", "menu.mp3")
                if event.key == pygame.K_ESCAPE and game_state == "RUNNING":
                    game_state = "PAUSED"
                elif event.key == pygame.K_ESCAPE and game_state == "PAUSED":
                    game_state = "RUNNING"

        if game_state == "RUNNING":
            # Score ramps with steeper scaling over survival time.
            SURVIVAL_SCORE_PER_SEC = 60.0
            run["score"] += SURVIVAL_SCORE_PER_SEC * (1.0 + seconds_survived * 0.05) * dt

            rage_active = now_ticks < run["rage_end_ticks"]
            speed_mult = 1.5 if rage_active else 1.0
            contact_damage_mult = 0.5 if rage_active else 1.0
            knight_phase_speed_mult = 1.15 if tank_phase_active else 1.0

            def on_kill(enemy):
                # Kill bonus points (bigger threats grant more).
                bonus = 250
                if isinstance(enemy, TankEnemy):
                    bonus = 650
                elif isinstance(enemy, RangedEnemy):
                    bonus = 400
                elif isinstance(enemy, BossEnemy):
                    bonus = 4000
                run["score"] += bonus

                # Combat polish: add a quick screen-shake burst on kills.
                run["shake_until_ticks"] = now_ticks + 140
                run["shake_mag"] = min(10.0, 3.0 + enemy.radius * 0.22)

                if tank_phase_active:
                    run["tank_phase_kills"] += 1

                if (run["tank_phase_kills"] >= 20
                    and now_ticks - run["last_rage_drop_ticks"] >= run["rage_pickup_cooldown_ms"]):
                    run["rage_pickups"].append(RagePickup(enemy.x, enemy.y))
                    run["tank_phase_kills"] -= 20
                    run["last_rage_drop_ticks"] = now_ticks

            # ESCALATING WAVE SPAWNER
            run["spawn_timer"] += 1
            current_spawn_rate = max(15, 60 - int(seconds_survived * 0.5))
            if run["spawn_timer"] > current_spawn_rate:
                spawn_x = random.choice([random.randint(-50, 0), random.randint(WIDTH, WIDTH + 50)])
                spawn_y = random.randint(0, HEIGHT)

                rand_val = random.random()
                if seconds_survived > 45 and rand_val < 0.15:
                    run["enemies"].append(TankEnemy(spawn_x, spawn_y))
                elif seconds_survived > 20 and rand_val < 0.35:
                    run["enemies"].append(RangedEnemy(spawn_x, spawn_y))
                else:
                    run["enemies"].append(BasicEnemy(spawn_x, spawn_y))
                run["spawn_timer"] = 0

            # Spawn a boss once
            if not run["boss_spawned"] and seconds_survived >= BOSS_SPAWN_SECONDS:
                run["enemies"].append(BossEnemy(WIDTH // 2, -40))
                run["boss_spawned"] = True
                set_music("boss", "boss.mp3")

            current_boss = next((enemy for enemy in run["enemies"] if isinstance(enemy, BossEnemy) and enemy.hp > 0), None)
            boss_alive = current_boss is not None

            # Boss phase stun pickup spawner: every 15-20 sec while boss is alive.
            if boss_alive:
                if run["next_stun_spawn_ticks"] == 0:
                    run["next_stun_spawn_ticks"] = now_ticks + random.randint(15000, 20000)
                elif now_ticks >= run["next_stun_spawn_ticks"]:
                    run["stun_pickups"].append(StunPickup(random.randint(60, WIDTH - 60), random.randint(80, HEIGHT - 60)))
                    run["next_stun_spawn_ticks"] = now_ticks + random.randint(15000, 20000)
            else:
                run["next_stun_spawn_ticks"] = 0

            # Tank phase SplashPickup spawner: periodic support during the hardest phase.
            if tank_phase_active:
                if run["next_splash_spawn_ticks"] == 0:
                    run["next_splash_spawn_ticks"] = now_ticks + random.randint(6000, 9000)
                elif now_ticks >= run["next_splash_spawn_ticks"]:
                    run["splash_pickups"].append(
                        SplashPickup(
                            random.randint(60, WIDTH - 60),
                            random.randint(80, HEIGHT - 60),
                        )
                    )
                    run["next_splash_spawn_ticks"] = now_ticks + random.randint(9000, 14000)
            else:
                run["next_splash_spawn_ticks"] = 0

            # Enemy speed escalation (Basic + Tank only), slightly stronger ramp.
            basic_mult = min(2.40, 1.0 + seconds_survived * 0.012)
            tank_mult = min(2.55, 1.0 + seconds_survived * 0.010)

            # Update Entities
            run["player"].handle_input(keys)
            run["player"].update(run["orbs"], run["knight"], on_orb_collected=lambda: play_sfx("orb"))

            for pickup in run["rage_pickups"][:]:
                if math.dist((run["player"].x, run["player"].y), (pickup.x, pickup.y)) < run["player"].radius + pickup.radius:
                    run["rage_pickups"].remove(pickup)
                    run["rage_end_ticks"] = max(run["rage_end_ticks"], now_ticks + 5000)
                    play_sfx("rage")

            for pickup in run["stun_pickups"][:]:
                if math.dist((run["player"].x, run["player"].y), (pickup.x, pickup.y)) < run["player"].radius + pickup.radius:
                    run["stun_pickups"].remove(pickup)
                    boss = next((enemy for enemy in run["enemies"] if isinstance(enemy, BossEnemy) and enemy.hp > 0), None)
                    if boss:
                        boss.stunned_until_ticks = max(boss.stunned_until_ticks, now_ticks + 4000)
                        boss.stun_knockback_pending = True
                        play_sfx("stun")

            for pickup in run["splash_pickups"][:]:
                if math.dist((run["player"].x, run["player"].y), (pickup.x, pickup.y)) < run["player"].radius + pickup.radius:
                    run["splash_pickups"].remove(pickup)
                    run["knight"].splash_damage_end_ticks = max(
                        run["knight"].splash_damage_end_ticks,
                        now_ticks + 12000,  # longer uptime during Tank Phase
                    )

            for enemy in run["enemies"]:
                if isinstance(enemy, BasicEnemy):
                    enemy.speed = min(enemy.base_speed * basic_mult, 2.4)
                elif isinstance(enemy, TankEnemy):
                    enemy.speed = min(enemy.base_speed * tank_mult, 1.25)

                if isinstance(enemy, BossEnemy):
                    if now_ticks < enemy.stunned_until_ticks:
                        continue
                    if enemy.stun_knockback_pending:
                        enemy.stun_knockback_pending = False
                        dx = enemy.x - run["knight"].x
                        dy = enemy.y - run["knight"].y
                        dist = math.hypot(dx, dy)
                        if dist > 0:
                            enemy.x += (dx / dist) * 280
                            enemy.y += (dy / dist) * 280
                        enemy.x = max(enemy.radius, min(WIDTH - enemy.radius, enemy.x))
                        enemy.y = max(enemy.radius, min(HEIGHT - enemy.radius, enemy.y))
                    enemy.move_towards(run["knight"].x, run["knight"].y)
                elif isinstance(enemy, RangedEnemy):
                    enemy.update_ranged(run["knight"], run["projectiles"], on_shot=lambda: play_sfx("arrow"))
                else:
                    enemy.move_towards(run["knight"].x, run["knight"].y)

            for proj in run["projectiles"][:]:
                proj.update()
                if proj.x < 0 or proj.x > WIDTH or proj.y < 0 or proj.y > HEIGHT:
                    run["projectiles"].remove(proj)

            if tank_phase_active:
                for orb in run["orbs"][:]:
                    if orb.decay_start_ms is None:
                        orb.decay_start_ms = now_ticks
                    elif now_ticks - orb.decay_start_ms >= ORB_DECAY_MS:
                        run["orbs"].remove(orb)

            run["knight"].update(
                run["enemies"],
                run["orbs"],
                run["projectiles"],
                speed_mult=speed_mult,
                contact_damage_mult=contact_damage_mult,
                knight_phase_speed_mult=knight_phase_speed_mult,
                on_kill=on_kill,
                now_ticks=now_ticks,
                orb_drop_chance=0.5 if boss_alive else 1.0,
                on_contact_damage_sfx=lambda: play_sfx("hit"),
            )

            # Sword SFX on contact damage (throttled to avoid audio spam).
            if run["knight"].hit_flash_until_ticks > now_ticks and now_ticks - run["last_sword_sfx_ticks"] > 80:
                play_sfx("sword")
                run["last_sword_sfx_ticks"] = now_ticks

            # Death Sound Fix: play exactly once at the moment we transition.
            if run["knight"].hp <= 0 and game_state != "GAME_OVER":
                game_state = "GAME_OVER"
                if not run["death_sfx_played"]:
                    run["death_sfx_played"] = True
                    play_sfx("death")

        current_boss = next((enemy for enemy in run["enemies"] if isinstance(enemy, BossEnemy) and enemy.hp > 0), None)
        score_int = int(run["score"])
        high_score = max(high_score, score_int)

        # Compute draw-only screen shake offset
        if now_ticks < run["shake_until_ticks"]:
            mag = run["shake_mag"]
            ox = random.uniform(-mag, mag)
            oy = random.uniform(-mag, mag)
        else:
            ox = 0.0
            oy = 0.0

        # Draw
        # --- DRAW BACKGROUND ---
        if bg_img:
            screen.blit(bg_img, (0, 0))
            screen.blit(bg_dimmer, (0, 0)) # Dims the background
        else:
            screen.fill(BLACK)
        # -----------------------

        if game_state in ("RUNNING", "PAUSED", "GAME_OVER"):
            for orb in run["orbs"]:
                draw_entity(screen, orb.x + ox, orb.y + oy, orb.radius, orb.color, orb.sprite)
            for pickup in run["rage_pickups"]:
                pickup.draw(screen, ox=ox, oy=oy)
            for pickup in run["stun_pickups"]:
                pickup.draw(screen, ox=ox, oy=oy)
            for pickup in run["splash_pickups"]:
                pickup.draw(screen, ox=ox, oy=oy)
            for proj in run["projectiles"]:
                proj.draw(screen, ox=ox, oy=oy)
            for enemy in run["enemies"]:
                enemy.draw(screen, ox=ox, oy=oy, now_ticks=now_ticks)

            rage_active = now_ticks < run["rage_end_ticks"]
            run["knight"].draw(screen, rage_active=rage_active, now_ticks=now_ticks, ox=ox, oy=oy)
            run["player"].draw(screen, ox=ox, oy=oy)

            if current_boss:
                draw_boss_health_bar(screen, current_boss)

            # Top-left score HUD
            score_surf = ui_font.render(f"Score: {score_int}", True, WHITE)
            hs_surf = ui_font.render(f"High Score: {high_score}", True, WHITE)
            screen.blit(score_surf, (12, 10))
            screen.blit(hs_surf, (12, 36))

            # Bottom-left fixed Knight HP HUD
            hp_bar_x, hp_bar_y = 18, HEIGHT - 50
            hp_bar_w, hp_bar_h = 260, 24
            pygame.draw.rect(screen, (70, 20, 20), (hp_bar_x, hp_bar_y, hp_bar_w, hp_bar_h))
            hp_fill = int(hp_bar_w * max(0.0, run["knight"].hp / run["knight"].max_hp))
            pygame.draw.rect(screen, (30, 220, 80), (hp_bar_x, hp_bar_y, hp_fill, hp_bar_h))
            pygame.draw.rect(screen, WHITE, (hp_bar_x, hp_bar_y, hp_bar_w, hp_bar_h), 2)
            hp_text = ui_font.render(f"KNIGHT HP: {int(max(0, run['knight'].hp))}/{int(run['knight'].max_hp)}", True, WHITE)
            screen.blit(hp_text, (hp_bar_x, hp_bar_y - 28))

            if rage_active and game_state == "RUNNING":
                remaining = max(0.0, (run["rage_end_ticks"] - now_ticks) / 1000.0)
                rage_text = ui_font.render(f"RAGE MODE ({remaining:.1f}s)", True, (255, 80, 80))
                screen.blit(rage_text, (12, 62))

            # Flash warnings
            tank_warning_active = TANK_PHASE_SECONDS <= seconds_survived < (TANK_PHASE_SECONDS + WARNING_DURATION_SECONDS)
            boss_warning_active = BOSS_SPAWN_SECONDS <= seconds_survived < (BOSS_SPAWN_SECONDS + WARNING_DURATION_SECONDS)
            if game_state == "RUNNING" and (tank_warning_active or boss_warning_active) and int(seconds_survived * 6) % 2 == 0:
                if boss_warning_active:
                    draw_center_warning(screen, warning_font, "BOSS INCOMING")
                else:
                    draw_center_warning(screen, warning_font, "TANK PHASE")

        if game_state == "MAIN_MENU":
            title = title_font.render("THE UNSUNG HERO", True, WHITE)
            p1 = menu_font.render("Press SPACE to Start", True, (240, 240, 255))
            p2 = menu_font.render("Press R for Rules", True, (210, 210, 255))
            screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80)))
            screen.blit(p1, p1.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
            screen.blit(p2, p2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 45)))

        elif game_state == "RULES":
            title = sub_font.render("THE UNSUNG HERO - FIELD MANUAL", True, WHITE)
            screen.blit(title, title.get_rect(center=(WIDTH // 2, 125)))

            rules_lines = [
                "WASD / Arrows: Move the Support Wisp",
                "SPACE: Pulse (Pushes enemies & clears projectiles. Costs 5% Knight HP!)",
                "Keep the Arrogant Knight alive! He fights on his own.",
                "Collect Golden Orbs to heal the Knight.",
                "Red Diamonds trigger Rage Mode. Blue Diamonds stun the Boss.",
                "Press M to Return to Menu",
            ]
            start_y = 200
            line_gap = 42
            for idx, line in enumerate(rules_lines):
                txt = ui_font.render(line, True, (230, 230, 240))
                y = start_y + idx * line_gap
                screen.blit(txt, txt.get_rect(center=(WIDTH // 2, y)))

        elif game_state == "PAUSED":
            dim = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            dim.fill((0, 0, 0, 165))
            screen.blit(dim, (0, 0))
            paused_txt = game_over_font.render("PAUSED", True, WHITE)
            resume_txt = ui_font.render("Press ESC to Resume", True, (230, 230, 255))
            screen.blit(paused_txt, paused_txt.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 18)))
            screen.blit(resume_txt, resume_txt.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 36)))

        elif game_state == "GAME_OVER":
            # Freeze state: entities stop updating; draw a dim overlay + end screen.
            dim = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            dim.fill((0, 0, 0, 175))
            screen.blit(dim, (0, 0))

            title = game_over_font.render("THE UNSUNG HERO HAS FALLEN", True, (255, 230, 230))
            title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 70))
            screen.blit(title, title_rect)

            final_score = sub_font.render(f"Final Score: {score_int}", True, WHITE)
            final_rect = final_score.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(final_score, final_rect)

            prompt = sub_font.render("Press R to Restart", True, (230, 230, 255))
            prompt_rect = prompt.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 48))
            screen.blit(prompt, prompt_rect)

        if game_state not in ("MAIN_MENU", "RULES") and current_music == "menu":
            set_music("run", "triumphant.mp3")
        if game_state in ("MAIN_MENU", "RULES") and current_music != "menu":
            set_music("menu", "menu.mp3")

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()