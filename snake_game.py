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

    def draw(self, surface):
        self.draw_particles(surface)
        for i, (x, y) in enumerate(self.positions):
            if not self.is_alive:
                progress = min(1.0, (pygame.time.get_ticks() - self.death_time) / 1000.0)
                color_blend = (
                    int(GREEN[0] * (1 - progress) + RED[0] * progress),
                    int(GREEN[1] * (1 - progress) + RED[1] * progress),
                    int(GREEN[2] * (1 - progress) + RED[2] * progress)
                )
                color = color_blend
            else:
                if i == 0:
                else:
                    color = GREEN
                    
                    # Градиентная окраска тела
                    gradient_factor = (i / self.length) * 0.7
                    r = max(0, int(GREEN[0] * (1 - gradient_factor)))
                    g = max(0, int(GREEN[1] * (1 - gradient_factor / 3)))
                    b = max(0, int(GREEN[2] * (1 - gradient_factor)))
                    color = (r, g, b)

            segment_rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(surface, color, segment_rect)
            pygame.draw.rect(surface, BLACK, segment_rect, 1)

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.color = RED
        self.special = False
        self.special_timer = 0
        self.randomize_position()
    
    def randomize_position(self, snake_positions=None):
        if snake_positions is None:
            snake_positions = []
        
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if (x, y) not in snake_positions:
                break
        
        self.position = (x, y)
     
        if random.random() < 0.15:
            self.special = True
            self.color = YELLOW
            self.special_timer = pygame.time.get_ticks() + 5000  # еда исчезает через 5 секунд
        else:
            self.special = False
            self.color = RED
            self.special_timer = 0
    
    def draw(self, surface):
        food_rect = pygame.Rect(
            self.position[0] * GRID_SIZE, 
            self.position[1] * GRID_SIZE, 
            GRID_SIZE, 
            GRID_SIZE
        )
        
        if self.special:
            current_time = pygame.time.get_ticks()
            if current_time > self.special_timer:
                self.randomize_position()
                return
            
            # Мигание для специальной еды
            if (current_time // 200) % 2 == 0:
                pygame.draw.rect(surface, self.color, food_rect)
            else:
                pygame.draw.rect(surface, PURPLE, food_rect)
        else:
            pygame.draw.rect(surface, self.color, food_rect) 
        pygame.draw.rect(surface, BLACK, food_rect, 1)

class GameState(Enum):
    MENU = 0
    GAME = 1
    GAME_OVER = 2
    PAUSE = 3
    MODE_SELECT = 4  # новое состояние для выбора режима игры 

class Game:
    def __init__(self):
        self.snake = Snake()
        self.food = Food()
        self.state = GameState.MENU
        self.high_score = 0
        self.mode = GameMode.CLASSIC
        self.obstacles = []

        #эффекты переходов
        self.transition_alpha = 255
        self.transition_speed = 5
        self.transition_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.transition_surface.fill(BLACK)
        self.game_over_time = 0
        # загрузка или создание рекорда
        self.load_high_score()
        self.start_time = 0
        self.shake_amount = 0
        self.shake_duration = 0
        self.flash_duration = 0
        # цвет фона
        self.background_color = BLACK

    def load_high_score(self):
        try:
            with open("highscore.txt", "r") as file:
                self.high_score = int(file.read())
        except:
            self.high_score = 0
    
    def save_high_score(self):
        with open("highscore.txt", "w") as file:
            file.write(str(self.high_score))
    
    def generate_obstacles(self, count=10):
        self.obstacles = []
        snake_positions = self.snake.positions
        head_x, head_y = snake_positions[0]
        safe_zone = []
        for x in range(head_x - 2, head_x + 3):
            for y in range(head_y - 2, head_y + 3):
                safe_zone.append((x, y))

        #случайные препятствия
        for _ in range(count):
            while True:
                x = random.randint(0, GRID_WIDTH - 1)
                y = random.randint(0, GRID_HEIGHT - 1)
                pos = (x, y)

                # проверяем, что препятствие не на змейке, не на еде, не в безопасной зоне 
                # и не на другом препятствии
                if (pos not in snake_positions and 
                    pos != self.food.position and
                    pos not in safe_zone and
                    not any(o.position == pos for o in self.obstacles)):
                    self.obstacles.append(Obstacle(pos))
                    break


    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # обработка клавиш в зависимости от состояния игры
            if event.type == pygame.KEYDOWN:
                if self.state == GameState.MENU:
                    if event.key == pygame.K_SPACE:
                        self.state = GameState.MODE_SELECT
                elif self.state == GameState.MODE_SELECT:
                    if event.key == pygame.K_1:
                        self.mode = GameMode.CLASSIC
                        self.start_new_game()
                    elif event.key == pygame.K_2:
                        self.mode = GameMode.WALLS
                        self.start_new_game()
                    elif event.key == pygame.K_3:
                        self.mode = GameMode.OBSTACLES
                        self.start_new_game()
                        self.generate_obstacles()
                    elif event.key == pygame.K_ESCAPE:
                        self.state = GameState.MENU
                elif self.state == GameState.GAME:
                    if event.key == pygame.K_UP:
                        self.snake.update_direction(Direction.UP)
                    elif event.key == pygame.K_DOWN:
                        self.snake.update_direction(Direction.DOWN)
                    elif event.key == pygame.K_LEFT:
                        self.snake.update_direction(Direction.LEFT)
                    elif event.key == pygame.K_RIGHT:
                        self.snake.update_direction(Direction.RIGHT)
                    elif event.key == pygame.K_p:
                        self.state = GameState.PAUSE
                elif self.state == GameState.GAME_OVER:
                    if event.key == pygame.K_r:
                        # перезапуск игры
                        self.start_new_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.state = GameState.MENU
                elif self.state == GameState.PAUSE:
                    if event.key == pygame.K_p:
                        self.state = GameState.GAME
                    elif event.key == pygame.K_ESCAPE:
                        self.state = GameState.MENU


    def start_new_game(self):
        self.state = GameState.GAME
        self.snake.reset()
        self.food.randomize_position(self.snake.positions)
        self.background_color = BLACK    

        # емли режим с препятствиями, генерируем их
        if self.mode == GameMode.OBSTACLES:
            self.generate_obstacles()

    def trigger_death_effects(self):
        # эффект тряски экрана
        self.shake_amount = 15
        self.shake_duration = 500  # миллисекунды
        # эффект вспышки
        self.flash_duration = 100  # миллисекунды

