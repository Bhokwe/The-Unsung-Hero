import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
KNIGHT_COLOR = (200, 50, 50)  
PLAYER_COLOR = (50, 200, 250) 
ENEMY_COLOR = (50, 200, 50)   
ORB_COLOR = (255, 215, 0) # Gold for Life Orbs

class LifeOrb:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 6
        self.heal_amount = 10.0

    def draw(self, surface):
        pygame.draw.circle(surface, ORB_COLOR, (int(self.x), int(self.y)), self.radius)

class RecklessKnight:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 2.5 
        self.radius = 15
        self.state = "IDLE"
        self.max_hp = 100.0
        self.hp = self.max_hp

    def find_densest_enemy_cluster(self, enemies):
        if not enemies: return None
        best_target = None
        max_neighbors = -1
        cluster_radius = 120 

        for enemy in enemies:
            neighbors = sum(1 for e in enemies if math.dist((enemy.x, enemy.y), (e.x, e.y)) < cluster_radius)
            if neighbors > max_neighbors:
                max_neighbors = neighbors
                best_target = enemy
        return best_target

    def update(self, enemies, orbs):
        # 1. Combat & Collision
        for enemy in enemies[:]:
            if math.dist((self.x, self.y), (enemy.x, enemy.y)) < self.radius + enemy.radius:
                enemies.remove(enemy)
                orbs.append(LifeOrb(enemy.x, enemy.y)) # Drop orb on kill
                self.hp -= 2.0 # Knight takes minor damage for being reckless

        # 2. Movement
        target = self.find_densest_enemy_cluster(enemies)
        if target and self.hp > 0:
            self.state = "CHARGING"
            dx, dy = target.x - self.x, target.y - self.y
            dist = math.hypot(dx, dy)
            if dist > 0:
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed
        else:
            self.state = "IDLE"

    def draw(self, surface):
        if self.hp > 0:
            pygame.draw.circle(surface, KNIGHT_COLOR, (int(self.x), int(self.y)), self.radius)
        # Health bar
        pygame.draw.rect(surface, (100, 0, 0), (self.x - 20, self.y - 25, 40, 5))
        pygame.draw.rect(surface, (0, 255, 0), (self.x - 20, self.y - 25, 40 * max(0, self.hp) / self.max_hp, 5))

class SupportPlayer:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 6 
        self.radius = 10
        self.pulse_radius = 150
        self.pulse_cooldown = 0

    def handle_input(self, keys):
        if keys[pygame.K_w] or keys[pygame.K_UP]: self.y -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: self.y += self.speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: self.x -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: self.x += self.speed

        self.x = max(self.radius, min(WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(HEIGHT - self.radius, self.y))

    def trigger_pulse(self, enemies, knight):
        if self.pulse_cooldown == 0 and knight.hp > 0:
            health_cost = knight.hp * 0.05
            knight.hp -= health_cost
            
            for enemy in enemies:
                dist = math.dist((self.x, self.y), (enemy.x, enemy.y))
                if dist < self.pulse_radius:
                    dx, dy = enemy.x - self.x, enemy.y - self.y
                    if dist > 0:
                        enemy.x += (dx / dist) * 80 
                        enemy.y += (dy / dist) * 80
            
            self.pulse_cooldown = 60 

    def update(self, orbs, knight):
        # Cooldown management
        if self.pulse_cooldown > 0:
            self.pulse_cooldown -= 1

        # Orb Collection
        for orb in orbs[:]:
            if math.dist((self.x, self.y), (orb.x, orb.y)) < self.radius + orb.radius:
                orbs.remove(orb)
                knight.hp = min(knight.max_hp, knight.hp + orb.heal_amount) # Heal but don't exceed max HP

    def draw(self, surface):
        pygame.draw.circle(surface, PLAYER_COLOR, (int(self.x), int(self.y)), self.radius)
        if self.pulse_cooldown == 0:
            pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.pulse_radius, 1)

class DummyEnemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10

    def draw(self, surface):
        pygame.draw.circle(surface, ENEMY_COLOR, (int(self.x), int(self.y)), self.radius)

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("The Unsung Hero - Core Loop")
    clock = pygame.time.Clock()

    knight = RecklessKnight(WIDTH // 2, HEIGHT // 2)
    player = SupportPlayer(WIDTH // 2 - 50, HEIGHT // 2)
    
    enemies = []
    orbs = []
    spawn_timer = 0

    running = True
    while running:
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.trigger_pulse(enemies, knight)

        # Basic Enemy Spawner to keep the Knight busy
        spawn_timer += 1
        if spawn_timer > 30: # Spawn an enemy every half second
            enemies.append(DummyEnemy(random.randint(50, 750), random.randint(50, 550)))
            spawn_timer = 0

        # Update
        player.handle_input(keys)
        player.update(orbs, knight)
        knight.update(enemies, orbs)

        # Draw
        screen.fill(BLACK)
        for orb in orbs: orb.draw(screen)
        for enemy in enemies: enemy.draw(screen)
        knight.draw(screen)
        player.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()