import random
import pygame
import time
import numpy as np
import tensorflow as tf

# Константы и настройки
WINDOW_SIZE = (400, 400)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SLEEP_TIME = 1

# Создание окна Pygame
pygame.init()
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("2048")
font = pygame.font.Font(None, 60)

# Загрузка модели
model = tf.keras.models.load_model('trained_2048_model.keras')

board=[]

def is_move_possible(board, direction):
    if direction == "left":
        return any(can_move_left(row) for row in board)
    elif direction == "up":
        return any(can_move_up(col) for col in np.transpose(board))
    elif direction == "right":
        return any(can_move_right(row) for row in board)
    elif direction == "down":
        return any(can_move_down(col) for col in np.transpose(board))
    else:
        raise ValueError("Invalid direction")

def can_move_left(row):
    for i in range(1, 4):
        if row[i] != 0 and (row[i - 1] == 0 or row[i - 1] == row[i]):
            return True
    return False

def can_move_up(col):
    for i in range(1, 4):
        if col[i] != 0 and (col[i - 1] == 0 or col[i - 1] == col[i]):
            return True
    return False

def can_move_right(row):
    for i in range(2, -1, -1):
        if row[i] != 0 and (row[i + 1] == 0 or row[i + 1] == row[i]):
            return True
    return False

def can_move_down(col):
    for i in range(2, -1, -1):
        if col[i] != 0 and (col[i + 1] == 0 or col[i + 1] == col[i]):
            return True
    return False


def available_moves(board):
    moves = []
    if is_move_possible(board, "left"):
        moves.append(0)
    if is_move_possible(board, "up"):
        moves.append(1)
    if is_move_possible(board, "right"):
        moves.append(2)
    if is_move_possible(board, "down"):
        moves.append(3)
    return moves

def random_move(board):
    possible_moves = available_moves(board)
    if possible_moves:
        return random.choice(possible_moves)
    else:
        return None


# Функции для работы с игровым полем
def add_random_tile(board):
    empty_cells = [(i, j) for i in range(4) for j in range(4) if board[i][j] == 0]
    if empty_cells:
        i, j = random.choice(empty_cells)
        board[i][j] = random.choice([2, 4])

def is_game_over(board):
    for i in range(4):
        for j in range(4):
            if board[i][j] == board[i][j + 1] or board[j][i] == board[j + 1][i]:
                return False
    return True

def draw_board(board):
    for i in range(4):
        for j in range(4):
            pygame.draw.rect(screen, WHITE, (j * 100, i * 100, 100, 100))
            if board[i][j] != 0:
                text = font.render(str(board[i][j]), True, BLACK)
                text_rect = text.get_rect(center=(j * 100 + 50, i * 100 + 50))
                screen.blit(text, text_rect)
# Оптимизированные функции для движения
def slide_and_merge(row):
    row = [val for val in row if val != 0]
    for i in range(len(row) - 1):
        if row[i] == row[i + 1]:
            row[i] *= 2
            row[i + 1] = 0
    row = [val for val in row if val != 0]
    return row + [0] * (4 - len(row))

def move_left(board):
    new_board = [slide_and_merge(row) for row in board]
    return new_board

def move_right(board):
    new_board = [slide_and_merge(row[::-1])[::-1] for row in board]
    return new_board

def move_up(board):
    transposed_board = np.transpose(board)
    new_board = [slide_and_merge(col) for col in transposed_board]
    return np.transpose(new_board)

def move_down(board):
    transposed_board = np.transpose(board)
    new_board = [slide_and_merge(col[::-1])[::-1] for col in transposed_board]
    return np.transpose(new_board)



ACTIONS = [move_left, move_up, move_right, move_down]

def get_action(board_state):
    flattened_state = np.array(board_state).flatten()
    action_probs = model.predict(np.array([flattened_state]))[0]
    chosen_action = np.argmax(action_probs)
    return chosen_action



# Игровой цикл
def main():
    board = [[0] * 4 for _ in range(4)]
    add_random_tile(board)
    add_random_tile(board)
    temp_board = [row[:] for row in board]
    running = True
    while running:
        temp_board = [row[:] for row in board]
        action = get_action(board)
        time.sleep(0.2)
        available_moves_list = available_moves(board)
        if available_moves_list==[]:
            print('ПРОИГРАЛИ!!!!!!')
            board = [[0] * 4 for _ in range(4)]
            add_random_tile(board)
            add_random_tile(board)
            time.sleep(1)
            draw_board(board)
            pygame.display.flip()
            continue
        if action in available_moves_list:
            move_function = ACTIONS[action]
        else:
            move_function = ACTIONS[random.choice(available_moves_list)]
        board = move_function(board)  
        add_random_tile(board)
        draw_board(board)
        pygame.display.flip()


    pygame.quit()

if __name__ == "__main__":
    main()
