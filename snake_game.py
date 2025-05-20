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
