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

        rect = pygame.Rect(
            self.position[0] * GRID_SIZE, 
            self.position[1] * GRID_SIZE, 
            GRID_SIZE, 
            GRID_SIZE
        )
        
