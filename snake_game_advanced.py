import pygame
import time
import random
import sys

# Инициализация pygame
pygame.init()

# Определение цветов
white = (255, 255, 255)
black = (0, 0, 0)
red = (213, 50, 80)
green = (0, 255, 0)
blue = (50, 153, 213)
yellow = (255, 255, 0)
purple = (128, 0, 128)

# Размеры окна
display_width = 800
display_height = 600

# Создание окна игры
display = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('Змейка - Расширенная версия')

# Часы для контроля FPS
clock = pygame.time.Clock()

# Размер блока змейки и скорость игры
block_size = 20
initial_snake_speed = 15

# Шрифты для текста
font_style = pygame.font.SysFont("bahnschrift", 25)
score_font = pygame.font.SysFont("comicsansms", 35)
menu_font = pygame.font.SysFont("comicsansms", 50)

# Загрузка звуков
try:
    eat_sound = pygame.mixer.Sound("eat.wav")
    game_over_sound = pygame.mixer.Sound("game_over.wav")
    pygame.mixer.music.load("background.mp3")
    sounds_loaded = True
except:
    sounds_loaded = False

# Класс для еды
class Food:
    def __init__(self, color, points, duration=None):
        self.x = 0
        self.y = 0
        self.color = color
        self.points = points
        self.duration = duration
        self.spawn_time = 0
        self.generate_position()
    
    def generate_position(self):
        self.x = round(random.randrange(0, display_width - block_size) / block_size) * block_size
        self.y = round(random.randrange(0, display_height - block_size) / block_size) * block_size
        self.spawn_time = time.time()
    
    def draw(self):
        pygame.draw.rect(display, self.color, [self.x, self.y, block_size, block_size])
    
    def is_expired(self):
        if self.duration is None:
            return False
        return time.time() - self.spawn_time > self.duration

# Класс для змейки
class Snake:
    def __init__(self):
        self.x = display_width / 2
        self.y = display_height / 2
        self.x_change = 0
        self.y_change = 0
        self.body = []
        self.length = 1
        self.color = green
        self.score = 0
        self.speed = initial_snake_speed
    
    def change_direction(self, direction):
        if direction == "LEFT" and self.x_change == 0:
            self.x_change = -block_size
            self.y_change = 0
        elif direction == "RIGHT" and self.x_change == 0:
            self.x_change = block_size
            self.y_change = 0
        elif direction == "UP" and self.y_change == 0:
            self.y_change = -block_size
            self.x_change = 0
        elif direction == "DOWN" and self.y_change == 0:
            self.y_change = block_size
            self.x_change = 0
    
    def move(self):
        self.x += self.x_change
        self.y += self.y_change
        
        head = [self.x, self.y]
        self.body.append(head)
        
        if len(self.body) > self.length:
            del self.body[0]
    
    def draw(self):
        for segment in self.body:
            pygame.draw.rect(display, self.color, [segment[0], segment[1], block_size, block_size])
    
    def check_collision_with_self(self):
        head = self.body[-1]
        for segment in self.body[:-1]:
            if segment == head:
                return True
        return False
    
    def check_collision_with_walls(self):
        if self.x >= display_width or self.x < 0 or self.y >= display_height or self.y < 0:
            return True
        return False
    
    def check_collision_with_food(self, food):
        if self.x == food.x and self.y == food.y:
            return True
        return False
    
    def grow(self, points):
        self.length += 1
        self.score += points
        # Увеличиваем скорость каждые 5 очков
        if self.score % 5 == 0:
            self.speed += 1

# Функция для отображения счета
def display_score(score):
    value = score_font.render("Счет: " + str(score), True, black)
    display.blit(value, [0, 0])

# Функция для отображения скорости
def display_speed(speed):
    value = score_font.render("Скорость: " + str(speed), True, black)
    display.blit(value, [0, 40])

# Функция для вывода сообщения
def message(msg, color, y_displace=0):
    mesg = font_style.render(msg, True, color)
    display.blit(mesg, [display_width / 6, display_height / 3 + y_displace])

# Функция для отображения меню
def game_menu():
    menu = True
    
    while menu:
        display.fill(white)
        title = menu_font.render("Змейка", True, green)
        display.blit(title, [display_width/2 - 100, 100])
        
        message("Нажмите P для начала игры", black, -50)
        message("Нажмите Q для выхода", black, 0)
        message("Нажмите H для просмотра справки", black, 50)
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    menu = False
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_h:
                    show_help()

# Функция для отображения справки
def show_help():
    help_screen = True
    
    while help_screen:
        display.fill(white)
        title = menu_font.render("Справка", True, blue)
        display.blit(title, [display_width/2 - 100, 50])
        
        message("Управление: стрелки для движения", black, -100)
        message("Цель: собирать еду и расти", black, -50)
        message("Красная еда: 1 очко", red, 0)
        message("Желтая еда: 3 очка, появляется редко", yellow, 50)
        message("Фиолетовая еда: 5 очков, исчезает через 5 секунд", purple, 100)
        message("Нажмите BACKSPACE для возврата в меню", black, 150)
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    help_screen = False

# Функция для отображения паузы
def pause_game():
    paused = True
    
    message("Пауза. Нажмите C для продолжения", black)
    pygame.display.update()
    
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    paused = False

# Основная функция игры
def gameLoop():
    game_over = False
    game_close = False
    
    # Создаем змейку
    snake = Snake()
    
    # Создаем обычную еду
    regular_food = Food(red, 1)
    
    # Список для специальной еды
    special_foods = []
    
    # Время последнего появления специальной еды
    last_special_food_time = time.time()
    
    # Запускаем фоновую музыку, если звуки загружены
    if sounds_loaded:
        pygame.mixer.music.play(-1)
    
    while not game_over:

        # Экран окончания игры
        while game_close:
            display.fill(white)
            message("Вы проиграли! Счет: " + str(snake.score), red, -50)
            message("Нажмите Q для выхода или C для повторной игры", black, 0)
            pygame.display.update()
            
            if sounds_loaded:
                pygame.mixer.music.stop()
                game_over_sound.play()
            
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        gameLoop()

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    snake.change_direction("LEFT")
                elif event.key == pygame.K_RIGHT:
                    snake.change_direction("RIGHT")
                elif event.key == pygame.K_UP:
                    snake.change_direction("UP")
                elif event.key == pygame.K_DOWN:
                    snake.change_direction("DOWN")
                elif event.key == pygame.K_p:
                    pause_game()

        # Перемещение змейки
        snake.move()
        
        # Проверка столкновений со стенами и собой
        if snake.check_collision_with_walls() or snake.check_collision_with_self():
            game_close = True
        
        # Отрисовка фона
        display.fill(white)
        
        # Отрисовка обычной еды
        regular_food.draw()
        
        # Генерация специальной еды
        current_time = time.time()
        if current_time - last_special_food_time > 10:  # Каждые 10 секунд
            # 20% шанс на появление желтой еды (3 очка)
            if random.random() < 0.2:
                special_foods.append(Food(yellow, 3))
            # 10% шанс на появление фиолетовой еды (5 очков, исчезает через 5 секунд)
            elif random.random() < 0.1:
                special_foods.append(Food(purple, 5, 5))
            
            last_special_food_time = current_time
        
        # Отрисовка и проверка специальной еды
        for food in special_foods[:]:
            # Проверка на истечение времени
            if food.is_expired():
                special_foods.remove(food)
                continue
            
            food.draw()
            
            # Проверка столкновения с едой
            if snake.check_collision_with_food(food):
                if sounds_loaded:
                    eat_sound.play()
                snake.grow(food.points)
                special_foods.remove(food)
        
        # Проверка столкновения с обычной едой
        if snake.check_collision_with_food(regular_food):
            if sounds_loaded:
                eat_sound.play()
            snake.grow(regular_food.points)
            regular_food.generate_position()
        
        # Отрисовка змейки
        snake.draw()
        
        # Отображение счета и скорости
        display_score(snake.score)
        display_speed(snake.speed)
        
        pygame.display.update()
        
        # Установка скорости игры
        clock.tick(snake.speed)

    # Выход из игры
    pygame.quit()
    quit()

# Запуск меню игры
game_menu()

# Запуск игры
gameLoop() 