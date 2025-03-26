import random
import pygame
import pyautogui
import time
import pickle

pygame.init()

WINDOW_SIZE = (400, 400)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("2048")

font = pygame.font.Font(None, 36)

def add_random_tile(board):
    empty_cells = [(i, j) for i in range(4) for j in range(4) if board[i][j] == 0]
    if empty_cells:
        i, j = random.choice(empty_cells)
        board[i][j] = random.choice([2, 4])

board = [[0] * 4 for _ in range(4)]
add_random_tile(board)
add_random_tile(board)

def can_move(board, new_board):
    for i in range(4):
        for j in range(4):
            if new_board[i][j] != board[i][j]:
                return True
    return False

def is_game_over(board):
    if any(0 in row for row in board):
        return False
    for i in range(4):
        for j in range(3):
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

def slide_left(board):
    for row in board:
        row[:] = [val for val in row if val != 0]
        row.extend([0] * (4 - len(row)))

def merge_left(board):
    for row in board:
        for i in range(3):
            if row[i] == row[i + 1] and row[i] != 0:
                row[i] *= 2
                row[i + 1] = 0

def move_left(board):
    slide_left(board)
    merge_left(board)
    slide_left(board)

def move_right(board):
    mirror_board(board)
    move_left(board)
    mirror_board(board)

def move_up(board):
    transpose_board(board)
    move_left(board)
    transpose_board(board)

def move_down(board):
    transpose_board(board)
    mirror_board(board)
    move_left(board)
    mirror_board(board)
    transpose_board(board)

def transpose_board(board):
    board[:] = [list(row) for row in zip(*board)]

def mirror_board(board):
    for row in board:
        row.reverse()

training_data = []
count=0
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            temp_board = [row[:] for row in board]  # Создаем резервную копию
            if event.key == pygame.K_LEFT:
                move_left(board)
                training_data_n=0

            elif event.key == pygame.K_RIGHT:
                move_right(board)
                training_data_n=2

            elif event.key == pygame.K_UP:
                move_up(board)
                training_data_n=1

            elif event.key == pygame.K_DOWN:
                move_down(board)
                training_data_n=3

                
            # Проверка доступности хода перед выполнением
            if can_move(temp_board, board):
                training_data.append(([val for row in board for val in row], training_data_n))
                add_random_tile(board)
            else:
                print("НЕВОЗМОЖНО СДЕЛАТЬ ХОД!!!!!!!")
            count+=1
            print(count)
    draw_board(board)
    pygame.display.flip()

    if is_game_over(board):
        print('ПРОИГРАЛИ!!!!!!')
        with open('training_data.pkl', 'wb') as file:
            pickle.dump(training_data, file)
        board = [[0] * 4 for _ in range(4)]
        add_random_tile(board)
        add_random_tile(board)
        time.sleep(2)
        draw_board(board)
        pygame.display.flip()

pygame.quit()
