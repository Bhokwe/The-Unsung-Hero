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
PULSE_COLOR = (50, 200, 250, 100) # Transparent blue for pulse

class RecklessKnight:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 2.5 # Slightly slower than player
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

    def update(self, enemies):
        target = self.find_densest_enemy_cluster(enemies)

        if target:
            self.state = "CHARGING"
            dx, dy = target.x - self.x, target.y - self.y
            dist = math.hypot(dx, dy)
            if dist > 0:
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed
        else:
            self.state = "IDLE"

    def draw(self, surface):
        pygame.draw.circle(surface, KNIGHT_COLOR, (int(self.x), int(self.y)), self.radius)
        # Health bar for the Knight
        pygame.draw.rect(surface, (100, 0, 0), (self.x - 20, self.y - 25, 40, 5))
        pygame.draw.rect(surface, (0, 255, 0), (self.x - 20, self.y - 25, 40 * (self.hp / self.max_hp), 5))

class SupportPlayer:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 6 # Player is fast to dash around
        self.radius = 10
        self.pulse_radius = 150
        self.pulse_cooldown = 0

    def handle_input(self, keys):
        if keys[pygame.K_w] or keys[pygame.K_UP]: self.y -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: self.y += self.speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: self.x -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: self.x += self.speed

        # Keep player on screen
        self.x = max(self.radius, min(WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(HEIGHT - self.radius, self.y))

    def trigger_pulse(self, enemies, knight):
        if self.pulse_cooldown == 0:
            # Risk/Reward: Costs 5% of Knight's CURRENT health
            health_cost = knight.hp * 0.05
            knight.hp -= health_cost
            
            # Knockback physics
            for enemy in enemies:
                dist = math.dist((self.x, self.y), (enemy.x, enemy.y))
                if dist < self.pulse_radius:
                    # Calculate push direction
                    dx, dy = enemy.x - self.x, enemy.y - self.y
                    if dist > 0:
                        enemy.x += (dx / dist) * 80 # Knockback force
                        enemy.y += (dy / dist) * 80
            
            self.pulse_cooldown = 60 # 1 second cooldown at 60 FPS

    def update(self):
        if self.pulse_cooldown > 0:
            self.pulse_cooldown -= 1

    def draw(self, surface):
        pygame.draw.circle(surface, PLAYER_COLOR, (int(self.x), int(self.y)), self.radius)
        # Draw pulse range indicator when ready
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
    pygame.display.set_caption("The Unsung Hero - V2")
    clock = pygame.time.Clock()

    knight = RecklessKnight(WIDTH // 2, HEIGHT // 2)
    player = SupportPlayer(WIDTH // 2 - 50, HEIGHT // 2)
    
    enemies = [DummyEnemy(random.randint(50, 750), random.randint(50, 550)) for _ in range(20)]

    running = True
    while running:
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.trigger_pulse(enemies, knight)

        # Update
        player.handle_input(keys)
        player.update()
        knight.update(enemies)

        # Draw
        screen.fill(BLACK)
        for enemy in enemies: enemy.draw(screen)
        knight.draw(screen)
        player.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()