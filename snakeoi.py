import pygame
import random
import sys
import time

import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import pyplot as plt

# ------------- SETTINGS YOU EDIT -------------
EAT_SOUND_FILE = "mixkit-chewing-something-crunchy-2244.wav"      # <-- put your eat sound filename here
DIE_SOUND_FILE = "mixkit-sword-slashes-in-battle-2763.wav"      # <-- put your die sound filename here
# ---------------------------------------------

pygame.init()
pygame.mixer.init()

# Screen settings
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake Game - Levels & Blocks")

# Clock
clock = pygame.time.Clock()
FPS = 15

# Fonts
font = pygame.font.SysFont("comicsansms", 30)
big_font = pygame.font.SysFont("comicsansms", 60)

# Load images
apple_img = pygame.image.load("apple.png")
poison_img = pygame.image.load("poison.png")

# Sizes
snake_size = 32
food_size = 48
apple_img = pygame.transform.scale(apple_img, (food_size, food_size))
poison_img = pygame.transform.scale(poison_img, (food_size, food_size))

# Load sounds
eat_sound = pygame.mixer.Sound(EAT_SOUND_FILE)
die_sound = pygame.mixer.Sound(DIE_SOUND_FILE)
eat_sound.set_volume(0.2)
die_sound.set_volume(0.5)

# Global stats
snake_speed = 20
max_level = 5


def draw_snake(snake_list, direction):
    for i, segment in enumerate(snake_list):
        x, y = segment
        pygame.draw.rect(screen, (0, 255, 0), (x, y, snake_size, snake_size))
        if i == len(snake_list) - 1:  # head
            eye_size = snake_size // 6
            if direction == "UP":
                eye1 = (x + eye_size, y + eye_size)
                eye2 = (x + snake_size - 2 * eye_size, y + eye_size)
            elif direction == "DOWN":
                eye1 = (x + eye_size, y + snake_size - 2 * eye_size)
                eye2 = (x + snake_size - 2 * eye_size, y + snake_size - 2 * eye_size)
            elif direction == "LEFT":
                eye1 = (x + eye_size, y + eye_size)
                eye2 = (x + eye_size, y + snake_size - 2 * eye_size)
            else:  # RIGHT
                eye1 = (x + snake_size - 2 * eye_size, y + eye_size)
                eye2 = (x + snake_size - 2 * eye_size, y + snake_size - 2 * eye_size)
            pygame.draw.rect(screen, (0, 0, 0), (*eye1, eye_size, eye_size))
            pygame.draw.rect(screen, (0, 0, 0), (*eye2, eye_size, eye_size))


def draw_apple(pos):
    screen.blit(apple_img, pos)


def draw_poison(pos):
    screen.blit(poison_img, pos)


def draw_blocks(blocks):
    for block in blocks:
        pygame.draw.rect(screen, (150, 75, 0), (*block, snake_size, snake_size))


def draw_text(text, color, x, y, big=False):
    label = big_font.render(text, True, color) if big else font.render(text, True, color)
    screen.blit(label, (x, y))


def generate_blocks(level):
    blocks = []

    if level >= 2:
        # Edge frame
        for x in range(0, SCREEN_WIDTH, snake_size):
            blocks.append([x, 0])
            blocks.append([x, SCREEN_HEIGHT - snake_size])
        for y in range(snake_size, SCREEN_HEIGHT - snake_size, snake_size):
            blocks.append([0, y])
            blocks.append([SCREEN_WIDTH - snake_size, y])

    if level == 3:
        # Vertical line middle with gap
        mid_x = SCREEN_WIDTH // 2
        gap_start = SCREEN_HEIGHT // 3
        gap_end = SCREEN_HEIGHT * 2 // 3
        for y in range(snake_size * 2, SCREEN_HEIGHT - snake_size * 2, snake_size):
            if not (gap_start <= y <= gap_end):
                blocks.append([mid_x, y])

    elif level == 4:
        # Two horizontal lines with gaps
        y1 = SCREEN_HEIGHT // 3
        y2 = SCREEN_HEIGHT * 2 // 3
        gap_left = snake_size * 3
        gap_right = SCREEN_WIDTH - snake_size * 5
        for x in range(snake_size * 2, SCREEN_WIDTH - snake_size * 2, snake_size):
            if x < gap_left or x > gap_right:
                blocks.append([x, y1])
                blocks.append([x, y2])

    elif level == 5:
        # Frame + cross with gaps
        start_x, start_y = SCREEN_WIDTH // 3, SCREEN_HEIGHT // 3
        end_x, end_y = SCREEN_WIDTH * 2 // 3, SCREEN_HEIGHT * 2 // 3
        for x in range(start_x, end_x + 1, snake_size):
            if x != SCREEN_WIDTH // 2:
                blocks.append([x, start_y])
                blocks.append([x, end_y])
        for y in range(start_y, end_y + 1, snake_size):
            if y != SCREEN_HEIGHT // 2:
                blocks.append([start_x, y])
                blocks.append([end_x, y])

    return blocks


def generate_food(blocks):
    while True:
        food = [
            random.randrange(0, SCREEN_WIDTH - food_size, snake_size),
            random.randrange(0, SCREEN_HEIGHT - food_size, snake_size),
        ]
        food_rect = pygame.Rect(food[0], food[1], food_size, food_size)
        overlap = False
        for block in blocks:
            if food_rect.colliderect(pygame.Rect(*block, snake_size, snake_size)):
                overlap = True
                break
        if not overlap:
            return food


def show_stats_window(level, won, seconds, level_apples, moves,
                      total_wins_run, total_apples_run, last_level):
    root = tk.Tk()
    root.title("Game Stats")

    if last_level and won:
        status_text = "YOU FINISHED ALL LEVELS!"
    elif won:
        status_text = "YOU WON THIS LEVEL!"
    else:
        status_text = "YOU LOST!"

    tk.Label(root, text=status_text, font=("Arial", 18)).pack(pady=5)
    tk.Label(root, text=f"Level: {level}").pack()
    tk.Label(root, text=f"Time played: {seconds:.2f} seconds").pack()
    tk.Label(root, text=f"Apples this level: {level_apples}").pack()
    tk.Label(root, text=f"Total apples eaten: {total_apples_run}").pack()
    tk.Label(root, text=f"Total wins this run: {total_wins_run}").pack()

    for d in ["UP", "DOWN", "LEFT", "RIGHT"]:
        moves.setdefault(d, 0)

    fig, ax = plt.subplots(figsize=(4, 3))
    dirs = ["UP", "DOWN", "LEFT", "RIGHT"]
    counts = [moves[d] for d in dirs]
    ax.bar(dirs, counts, color=["blue", "red", "green", "orange"])
    ax.set_title("Moves per direction")
    ax.set_ylabel("Number of moves")

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=10)

    choice = {"val": None}

    def on_retry():
        choice["val"] = "retry"
        root.destroy()

    def on_next():
        choice["val"] = "next"
        root.destroy()

    def on_exit():
        choice["val"] = "exit"
        root.destroy()

    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=10)

    if won and not last_level:
        tk.Button(btn_frame, text="Try Again", width=12, command=on_retry).pack(
            side="left", padx=10
        )
        tk.Button(btn_frame, text="Next Level", width=12, command=on_next).pack(
            side="right", padx=10
        )
    else:
        tk.Button(btn_frame, text="Try Again", width=12, command=on_retry).pack(
            side="left", padx=10
        )
        tk.Button(btn_frame, text="Exit", width=12, command=on_exit).pack(
            side="right", padx=10
        )

    root.mainloop()
    return choice["val"]


def play_level(level, total_apples_so_far, total_wins_so_far, high_score_so_far):
    snake_list = [[100, 100]]
    snake_length = 1
    direction = "RIGHT"

    blocks = generate_blocks(level)
    food = generate_food(blocks)
    poison_list = [
        [
            random.randrange(0, SCREEN_WIDTH - food_size, snake_size),
            random.randrange(0, SCREEN_HEIGHT - food_size, snake_size),
        ]
        for _ in range(5)
    ]

    score = 0
    running = True

    start_time = time.time()
    moves = {"UP": 0, "DOWN": 0, "LEFT": 0, "RIGHT": 0}
    apples_eaten_level = 0
    level_won = False
    high_score = high_score_so_far
    total_apples = total_apples_so_far
    total_wins = total_wins_so_far

    while running:
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and direction != "DOWN":
                    direction = "UP"
                    moves["UP"] += 1
                elif event.key == pygame.K_DOWN and direction != "UP":
                    direction = "DOWN"
                    moves["DOWN"] += 1
                elif event.key == pygame.K_LEFT and direction != "RIGHT":
                    direction = "LEFT"
                    moves["LEFT"] += 1
                elif event.key == pygame.K_RIGHT and direction != "LEFT":
                    direction = "RIGHT"
                    moves["RIGHT"] += 1

        head = snake_list[-1].copy()
        if direction == "UP":
            head[1] -= snake_speed
        elif direction == "DOWN":
            head[1] += snake_speed
        elif direction == "LEFT":
            head[0] -= snake_speed
        elif direction == "RIGHT":
            head[0] += snake_speed

        # wrap only level 1
        if level == 1:
            if head[0] < 0:
                head[0] = SCREEN_WIDTH - snake_size
            elif head[0] >= SCREEN_WIDTH:
                head[0] = 0
            if head[1] < 0:
                head[1] = SCREEN_HEIGHT - snake_size
            elif head[1] >= SCREEN_HEIGHT:
                head[1] = 0

        snake_list.append(head)
        head_rect = pygame.Rect(head[0], head[1], snake_size, snake_size)

        # self collision
        if head in snake_list[:-1]:
            die_sound.play()
            running = False

        # block collision
        for block in blocks:
            if head_rect.colliderect(pygame.Rect(*block, snake_size, snake_size)):
                die_sound.play()
                running = False

        # food collision
        food_rect = pygame.Rect(
            food[0] + (food_size - snake_size) // 2,
            food[1] + (food_size - snake_size) // 2,
            snake_size,
            snake_size,
        )
        if head_rect.colliderect(food_rect):
            eat_sound.play()
            snake_length += 1
            score += 1
            apples_eaten_level += 1
            total_apples += 1
            food = generate_food(blocks)

        # poison collision
        for p in poison_list:
            p_rect = pygame.Rect(
                p[0] + (food_size - snake_size) // 2,
                p[1] + (food_size - snake_size) // 2,
                snake_size,
                snake_size,
            )
            if head_rect.colliderect(p_rect):
                die_sound.play()
                running = False

        if len(snake_list) > snake_length:
            del snake_list[0]

        draw_blocks(blocks)
        draw_apple(food)
        for p in poison_list:
            draw_poison(p)
        draw_snake(snake_list, direction)
        draw_text(f"Score: {score}/10", (255, 255, 0), 10, 10)
        draw_text(f"Level: {level}", (255, 255, 0), 10, 40)
        draw_text(f"High Score: {high_score}", (255, 255, 255), 900, 10)

        pygame.display.update()
        clock.tick(FPS)

        if score > high_score:
            high_score = score

        if score >= 10:
            level_won = True
            total_wins += 1
            running = False

    total_seconds = time.time() - start_time
    return (level_won, total_seconds, apples_eaten_level, moves,
            total_apples, total_wins, high_score)


def run_game(start_level=1):
    global screen
    level = start_level
    high_score = 0
    total_apples = 0
    total_wins = 0

    while True:
        (won, seconds, apples_level, moves,
         total_apples, total_wins, high_score) = play_level(
            level, total_apples, total_wins, high_score
        )

        last_level = (level == max_level)

        if (not won) or last_level:
            pygame.display.iconify()

            choice = show_stats_window(
                level,
                won,
                seconds,
                apples_level,
                moves,
                total_wins,
                total_apples,
                last_level,
            )

            pygame.display.quit()
            pygame.display.init()
            screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.display.set_caption("Snake Game - Levels & Blocks")

            if not won:
                if choice == "retry":
                    return "retry_same_level", level
                else:
                    return "exit", None
            else:
                if choice == "retry":
                    return "retry_from_start", None
                else:
                    return "exit", None
        else:
            level += 1
            if level > max_level:
                return "exit", None


def main():
    while True:
        result, level_to_restart = run_game(start_level=1)

        if result == "retry_same_level":
            result2, _ = run_game(start_level=level_to_restart)
            if result2 != "retry_from_start":
                break
        elif result == "retry_from_start":
            continue
        else:
            break

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
