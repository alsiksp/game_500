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

    def update(self):
        # обновление эффектов
        if self.shake_duration > 0:
            self.shake_duration -= clock.get_time()
            if self.shake_duration <= 0:
                self.shake_amount = 0
                
        if self.flash_duration > 0:
            self.flash_duration -= clock.get_time()
            if self.flash_duration <= 0:
                self.background_color = BLACK
            
        # обновление препятствий
        for obstacle in self.obstacles:
            obstacle.update()
            
        if self.state == GameState.GAME:
            self.snake.move()
            
            if not self.snake.is_alive:
                self.trigger_death_effects()
                
                if self.game_over_time == 0:
                    self.game_over_time = pygame.time.get_ticks() + 1500
                
                if pygame.time.get_ticks() >= self.game_over_time:
                    self.state = GameState.GAME_OVER
                    self.game_over_time = 0
                    
                    # обнова рекорда
                    if self.snake.score > self.high_score:
                        self.high_score = self.snake.score
                        self.save_high_score()
                return
            
            # проверка, съела ли змейка еду
            if self.snake.get_head_position() == self.food.position:
                # увеличиваем змейку
                self.snake.grow()
                
                # если это была специальная еда, даем дополнительные очки
                if self.food.special:
                    self.snake.score += 15
                
                # новая еда
                self.food.randomize_position(self.snake.positions + [o.position for o in self.obstacles])
                
            self.snake.update_particles()
        elif self.state == GameState.GAME_OVER:
            self.snake.update_particles()

   def draw_menu(self):
        screen.fill(BLACK)

        title_text = font_large.render("ЗМЕЙКА", True, GREEN)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 150))
        
        # инструкции
        instruction_text = font_medium.render("Нажмите ПРОБЕЛ чтобы начать", True, WHITE)
        screen.blit(instruction_text, (SCREEN_WIDTH // 2 - instruction_text.get_width() // 2, 300))
        
        # рекорд
        high_score_text = font_small.render(f"Рекорд: {self.high_score}", True, YELLOW)
        screen.blit(high_score_text, (SCREEN_WIDTH // 2 - high_score_text.get_width() // 2, 400))
        
        # управление
        controls_text = font_small.render("Управление: стрелки - движение, P - пауза", True, GRAY)
        screen.blit(controls_text, (SCREEN_WIDTH // 2 - controls_text.get_width() // 2, 450))
        
        # анимация змейки на фоне
        current_time = pygame.time.get_ticks() // 1000
        menu_snake_length = 10
        for i in range(menu_snake_length):
            x = (current_time + i) % GRID_WIDTH
            y = (GRID_HEIGHT // 2 + i % 3) % GRID_HEIGHT
            
            color = GREEN if i == 0 else DARK_GREEN
            pygame.draw.rect(screen, color, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

    def draw_mode_select(self):
        screen.fill(BLACK)
        
        # заголовок
        title_text = font_large.render("ВЫБЕРИТЕ РЕЖИМ", True, GREEN)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100))
        
        # варианты режимов
        mode1_text = font_medium.render("1. Классический", True, WHITE)
        screen.blit(mode1_text, (SCREEN_WIDTH // 2 - mode1_text.get_width() // 2, 220))
        
        mode2_text = font_medium.render("2. Стены", True, WHITE)
        screen.blit(mode2_text, (SCREEN_WIDTH // 2 - mode2_text.get_width() // 2, 280))
        
        mode3_text = font_medium.render("3. Препятствия", True, WHITE)
        screen.blit(mode3_text, (SCREEN_WIDTH // 2 - mode3_text.get_width() // 2, 340))
        
        # описания режимов
        desc1_text = font_small.render("Классический режим со свободными границами", True, GRAY)
        screen.blit(desc1_text, (SCREEN_WIDTH // 2 - desc1_text.get_width() // 2, 250))
        
        desc2_text = font_small.render("Столкновение со стеной приводит к смерти", True, GRAY)
        screen.blit(desc2_text, (SCREEN_WIDTH // 2 - desc2_text.get_width() // 2, 310))
        
        desc3_text = font_small.render("Препятствия на игровом поле", True, GRAY)
        screen.blit(desc3_text, (SCREEN_WIDTH // 2 - desc3_text.get_width() // 2, 370))
        
        # инструкция для возврата
        back_text = font_small.render("Нажмите ESC для возврата в меню", True, GRAY)
        screen.blit(back_text, (SCREEN_WIDTH // 2 - back_text.get_width() // 2, 450))

    def apply_screen_shake(self):
        if self.shake_amount > 0:
            dx = random.randint(-self.shake_amount, self.shake_amount)
            dy = random.randint(-self.shake_amount, self.shake_amount)
            return dx, dy
        return 0, 0

    def draw_game(self):
        # эффект вспышки при смерти
        if self.flash_duration > 0:
            self.background_color = RED

        screen.fill(self.background_color)
        shake_offset_x, shake_offset_y = self.apply_screen_shake()

        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                if (x + y) % 2 == 0:
                    rect = pygame.Rect(
                        x * GRID_SIZE + shake_offset_x, 
                        y * GRID_SIZE + shake_offset_y, 
                        GRID_SIZE, 
                        GRID_SIZE
                    )
                    pygame.draw.rect(screen, (20, 20, 20), rect)

        if self.mode == GameMode.WALLS or self.mode == GameMode.OBSTACLES:
            border_color = (80, 80, 80)
            pygame.draw.rect(
                screen, 
                border_color, 
                (
                    0 + shake_offset_x, 
                    0 + shake_offset_y, 
                    SCREEN_WIDTH, 
                    SCREEN_HEIGHT
                ), 
                3
            )
            
        # препятствия
        for obstacle in self.obstacles:
            original_position = obstacle.position
            
            # времено изменяем позицию для тряски
            offset_position = (
                obstacle.position[0] * GRID_SIZE + shake_offset_x,
                obstacle.position[1] * GRID_SIZE + shake_offset_y
            )
            
            # сохраняем и изменяем позицию для рисования
    def draw(self, screen, position=None):
        if position is None:
            position = self.position

    obstacle.draw(screen, offset_position)
            
            # возвращаем исходную позицию
            obstacle.position = real_position
        
        # создаем временную поверхность для тряски
        temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # рисуем змейку на временную поверхность
        self.snake.draw(temp_surface)
        
        # рисуем еду на временную поверхность
        self.food.draw(temp_surface)
        
        # добавляем тряску и переносим на основной экран
        screen.blit(temp_surface, (shake_offset_x, shake_offset_y))
        
        # счет
        score_text = font_small.render(f"Счет: {self.snake.score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        # рекорд
        high_score_text = font_small.render(f"Рекорд: {self.high_score}", True, YELLOW)
        screen.blit(high_score_text, (SCREEN_WIDTH - high_score_text.get_width() - 10, 10))
        
        # текущий режим
        mode_names = {
            GameMode.CLASSIC: "Классический",
            GameMode.WALLS: "Стены",
            GameMode.OBSTACLES: "Препятствия"
        }
        mode_text = font_small.render(f"Режим: {mode_names[self.mode]}", True, CYAN)
        screen.blit(mode_text, (SCREEN_WIDTH // 2 - mode_text.get_width() // 2, 10))
        
        # отображаем FPS
        fps = int(clock.get_fps())
        fps_text = font_small.render(f"FPS: {fps}", True, CYAN)
        screen.blit(fps_text, (10, SCREEN_HEIGHT - 30))
        # отображаем время игры
        elapsed = (pygame.time.get_ticks() - self.snake.death_time if not self.snake.death_time else pygame.time.get_ticks())//1000
        time_text = font_small.render(f"Time: {elapsed}s", True, CYAN)
        screen.blit(time_text, (100, SCREEN_HEIGHT - 30))
    
    def draw_game_over(self):
        # частицы конфетти
        self.snake.draw_particles(screen)
        
        # прозрачность для эффекта появления
        time_since_death = pygame.time.get_ticks() - self.snake.death_time
        alpha = min(180, time_since_death)
        
        # затемняем игровое поле
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(alpha)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # сообщение о конце игры с эффектом пульсации
        pulse = (pygame.time.get_ticks() // 100) % 20
        pulse_scale = 1.0 + (pulse / 100.0)
        
        game_over_text = font_large.render("ИГРА ОКОНЧЕНА", True, RED)
        text_width = game_over_text.get_width() * pulse_scale
        text_height = game_over_text.get_height() * pulse_scale
        scaled_game_over = pygame.transform.scale(game_over_text, (int(text_width), int(text_height)))
        
        screen.blit(scaled_game_over, (SCREEN_WIDTH // 2 - text_width // 2, 150))

        if self.snake.death_reason:
            reason_text = font_medium.render(self.snake.death_reason, True, RED)
            screen.blit(reason_text, reason_text.get_rect(centerx=SCREEN_WIDTH//2, top=240))


