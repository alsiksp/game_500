import pygame
import sys
import random
import time
from enum import Enum
import math

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

SPEED = 100
MAX_SPEED = 30
SPEED_INCREMENT = 2

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
DARK_GREEN = (0, 100, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
GRAY = (169, 169, 169)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)

class Direction(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

# Режимы игры (сложность)
class GameMode(Enum):
    CLASSIC = 0     # Классический режим с переходом через края
    WALLS = 1       # Режим проигрыш при столкновении со стеной
    OBSTACLES = 2   # Режим с препятствиями

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Змейка - Python Game")
font_large = pygame.font.SysFont('Arial', 72)
font_medium = pygame.font.SysFont('Arial', 36)
font_small = pygame.font.SysFont('Arial', 24)
clock = pygame.time.Clock()

class Particle:
    def __init__(self, x, y, color, size=5, lifetime=60):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.age = 0
        # случайное направление
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1, 4)
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed
    
    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.age += 1
        return self.age < self.lifetime

    def draw(self, surface):
        alpha = max(0, 255 * (1 - self.age / self.lifetime))
        s = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, int(alpha)), (self.size, self.size), self.size)
        surface.blit(s, (self.x - self.size, self.y - self.size))

class Obstacle:
    def __init__(self, position):
        self.position = position
        self.color = GRAY
        self.pulse_counter = 0

    def update(self):
        # Медленная пульсация препятствия
        self.pulse_counter = (self.pulse_counter + 0.05) % (2 * math.pi)
        
    def draw(self, surface):
        # Пульсирующий эффект для препятствия
        pulse = math.sin(self.pulse_counter) * 0.2 + 0.8
        color = tuple(min(255, int(c * pulse)) for c in self.color)

        rect = pygame.Rect(
            self.position[0] * GRID_SIZE, 
            self.position[1] * GRID_SIZE, 
            GRID_SIZE, 
            GRID_SIZE
        )
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, BLACK, rect, 1)

        line_color = (40, 40, 40)
        x, y = self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE
        pygame.draw.line(surface, line_color, 
                        (x + 3, y + 3), 
                        (x + GRID_SIZE - 3, y + GRID_SIZE - 3), 2)
        pygame.draw.line(surface, line_color, 
                        (x + GRID_SIZE - 3, y + 3), 
                        (x + 3, y + GRID_SIZE - 3), 2)

class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        self.length = 3
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        for i in range(1, self.length):
            self.positions.append((self.positions[0][0], self.positions[0][1] + i))

        self.direction = Direction.UP
        self.next_direction = Direction.UP
        self.score = 0
        self.speed = SPEED
        self.is_alive = True
        self.death_time = 0
        self.particles = []
        self.death_reason = ""

    def get_head_position(self):
        return self.positions[0]

    def update_direction(self, direction):
        if (direction == Direction.UP and self.direction != Direction.DOWN) or \
           (direction == Direction.DOWN and self.direction != Direction.UP) or \
           (direction == Direction.LEFT and self.direction != Direction.RIGHT) or \
           (direction == Direction.RIGHT and self.direction != Direction.LEFT):
            self.next_direction = direction

    def move(self):
        if not self.is_alive:
            return
        self.direction = self.next_direction
        head_x, head_y = self.get_head_position()        

        if self.direction == Direction.UP:
            head_y -= 1
        elif self.direction == Direction.DOWN:
            head_y += 1
        elif self.direction == Direction.LEFT:
            head_x -= 1
        elif self.direction == Direction.RIGHT:
            head_x += 1

        if game.mode == GameMode.CLASSIC:
            head_x %= GRID_WIDTH
            head_y %= GRID_HEIGHT
        elif game.mode == GameMode.WALLS or game.mode == GameMode.OBSTACLES:
            if head_x < 0 or head_x >= GRID_WIDTH or head_y < 0 or head_y >= GRID_HEIGHT:
                self.die("Столкновение со стеной!")
                return

        #Новая позиция головы
        new_head = (head_x, head_y)
        if new_head in self.positions:
            self.die("Столкновение с хвостом!")
            return

        if game.mode == GameMode.OBSTACLES:
            for obstacle in game.obstacles:
                if new_head == obstacle.position:
                    self.die("Столкновение с препятствием!")
                    return

        self.positions.insert(0, new_head)
        
        if len(self.positions) > self.length:
            self.positions.pop()
            
    def grow(self):
        self.length += 1
        self.score += 10

        if self.score % 50 == 0 and self.speed > MAX_SPEED:
            self.speed -= SPEED_INCREMENT

    def die(self, reason=""):
        if self.is_alive:
            self.is_alive = False
            self.death_time = pygame.time.get_ticks()
            self.death_reason = reason
            
            for _ in range(80):
                hx = self.positions[0][0] * GRID_SIZE + GRID_SIZE/2
                hy = self.positions[0][1] * GRID_SIZE + GRID_SIZE/2
                color = random.choice([RED, YELLOW, GREEN, BLUE, PURPLE])
                self.particles.append(Particle(hx, hy, color))

            for pos in self.positions:
                for _ in range(5):
                    px = pos[0] * GRID_SIZE + GRID_SIZE/2
                    py = pos[1] * GRID_SIZE + GRID_SIZE/2
                    color = random.choice([RED, ORANGE, YELLOW])
                    self.particles.append(Particle(px, py, color, size=3, lifetime=45))

    def update_particles(self):
        self.particles = [p for p in self.particles if p.update()]

    def draw_particles(self, surface):
        for p in self.particles:
            p.draw(surface)
