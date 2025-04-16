import pygame
import time
import random

# Инициализация pygame
pygame.init()

# Определение цветов
white = (255, 255, 255)
black = (0, 0, 0)
red = (213, 50, 80)
green = (0, 255, 0)
blue = (50, 153, 213)

# Размеры окна
display_width = 800
display_height = 600

# Создание окна игры
display = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('Змейка')

# Часы для контроля FPS
clock = pygame.time.Clock()

# Размер блока змейки и скорость игры
block_size = 20
snake_speed = 10

# Шрифты для текста
font_style = pygame.font.SysFont("bahnschrift", 25)
score_font = pygame.font.SysFont("comicsansms", 35)

# Функция для отображения счета
def your_score(score):
    value = score_font.render("Счет: " + str(score), True, black)
    display.blit(value, [0, 0])

# Функция для отрисовки змейки
def our_snake(block_size, snake_list):
    for x in snake_list:
        pygame.draw.rect(display, green, [x[0], x[1], block_size, block_size])

# Функция для вывода сообщения
def message(msg, color):
    mesg = font_style.render(msg, True, color)
    display.blit(mesg, [display_width / 6, display_height / 3])

# Основная функция игры
def gameLoop():
    game_over = False
    game_close = False

    # Начальная позиция змейки
    x1 = display_width / 2
    y1 = display_height / 2

    # Изменение координат
    x1_change = 0
    y1_change = 0

    # Список сегментов змейки
    snake_list = []
    length_of_snake = 1

    # Генерация первой еды
    foodx = round(random.randrange(0, display_width - block_size) / block_size) * block_size
    foody = round(random.randrange(0, display_height - block_size) / block_size) * block_size

    while not game_over:

        # Экран окончания игры
        while game_close:
            display.fill(white)
            message("Вы проиграли! Нажмите Q для выхода или C для повторной игры", red)
            your_score(length_of_snake - 1)
            pygame.display.update()

            # Обработка нажатий клавиш на экране окончания игры
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
                if event.key == pygame.K_LEFT and x1_change == 0:
                    x1_change = -block_size
                    y1_change = 0
                elif event.key == pygame.K_RIGHT and x1_change == 0:
                    x1_change = block_size
                    y1_change = 0
                elif event.key == pygame.K_UP and y1_change == 0:
                    y1_change = -block_size
                    x1_change = 0
                elif event.key == pygame.K_DOWN and y1_change == 0:
                    y1_change = block_size
                    x1_change = 0

        # Проверка на столкновение со стеной
        if x1 >= display_width or x1 < 0 or y1 >= display_height or y1 < 0:
            game_close = True

        # Обновление позиции змейки
        x1 += x1_change
        y1 += y1_change
        display.fill(white)
        
        # Отрисовка еды
        pygame.draw.rect(display, red, [foodx, foody, block_size, block_size])
        
        # Обновление змейки
        snake_head = []
        snake_head.append(x1)
        snake_head.append(y1)
        snake_list.append(snake_head)
        
        # Удаление лишних сегментов
        if len(snake_list) > length_of_snake:
            del snake_list[0]

        # Проверка на столкновение с собой
        for x in snake_list[:-1]:
            if x == snake_head:
                game_close = True

        # Отрисовка змейки и счета
        our_snake(block_size, snake_list)
        your_score(length_of_snake - 1)

        pygame.display.update()

        # Проверка на поедание еды
        if x1 == foodx and y1 == foody:
            foodx = round(random.randrange(0, display_width - block_size) / block_size) * block_size
            foody = round(random.randrange(0, display_height - block_size) / block_size) * block_size
            length_of_snake += 1

        # Установка скорости игры
        clock.tick(snake_speed)

    # Выход из игры
    pygame.quit()
    quit()

# Запуск игры
gameLoop() 