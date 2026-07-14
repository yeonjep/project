import random
import sys

import pygame


# 화면 설정
CELL_SIZE = 30
BOARD_WIDTH = 10
BOARD_HEIGHT = 20

SCREEN_WIDTH = BOARD_WIDTH * CELL_SIZE
SCREEN_HEIGHT = BOARD_HEIGHT * CELL_SIZE

FPS = 60
DROP_DELAY = 500  # 블록 자동 낙하 간격(ms)


# 색상
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
WHITE = (255, 255, 255)

COLORS = [
    (0, 240, 240),    # I
    (240, 240, 0),    # O
    (160, 0, 240),    # T
    (0, 240, 0),      # S
    (240, 0, 0),      # Z
    (0, 0, 240),      # J
    (240, 160, 0),    # L
]


# 테트리스 블록 모양
SHAPES = [
    [[1, 1, 1, 1]],

    [[1, 1],
     [1, 1]],

    [[0, 1, 0],
     [1, 1, 1]],

    [[0, 1, 1],
     [1, 1, 0]],

    [[1, 1, 0],
     [0, 1, 1]],

    [[1, 0, 0],
     [1, 1, 1]],

    [[0, 0, 1],
     [1, 1, 1]],
]


class Piece:
    def __init__(self):
        shape_index = random.randrange(len(SHAPES))
        self.shape = SHAPES[shape_index]
        self.color = COLORS[shape_index]

        self.x = BOARD_WIDTH // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self):
        """블록을 시계 방향으로 회전한다."""
        self.shape = [list(row) for row in zip(*self.shape[::-1])]


def create_board():
    return [[None for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]


def is_valid_position(board, piece, offset_x=0, offset_y=0):
    for row_index, row in enumerate(piece.shape):
        for col_index, cell in enumerate(row):
            if cell == 0:
                continue

            new_x = piece.x + col_index + offset_x
            new_y = piece.y + row_index + offset_y

            if new_x < 0 or new_x >= BOARD_WIDTH:
                return False

            if new_y >= BOARD_HEIGHT:
                return False

            if new_y >= 0 and board[new_y][new_x] is not None:
                return False

    return True


def lock_piece(board, piece):
    for row_index, row in enumerate(piece.shape):
        for col_index, cell in enumerate(row):
            if cell:
                board_y = piece.y + row_index
                board_x = piece.x + col_index

                if 0 <= board_y < BOARD_HEIGHT:
                    board[board_y][board_x] = piece.color


def clear_lines(board):
    remaining_rows = [
        row for row in board
        if any(cell is None for cell in row)
    ]

    cleared_count = BOARD_HEIGHT - len(remaining_rows)

    while len(remaining_rows) < BOARD_HEIGHT:
        remaining_rows.insert(0, [None for _ in range(BOARD_WIDTH)])

    return remaining_rows, cleared_count


def draw_board(screen, board):
    screen.fill(BLACK)

    for y in range(BOARD_HEIGHT):
        for x in range(BOARD_WIDTH):
            rect = pygame.Rect(
                x * CELL_SIZE,
                y * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE,
            )

            pygame.draw.rect(screen, GRAY, rect, 1)

            if board[y][x] is not None:
                pygame.draw.rect(screen, board[y][x], rect.inflate(-2, -2))


def draw_piece(screen, piece):
    for row_index, row in enumerate(piece.shape):
        for col_index, cell in enumerate(row):
            if cell:
                x = (piece.x + col_index) * CELL_SIZE
                y = (piece.y + row_index) * CELL_SIZE

                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, piece.color, rect.inflate(-2, -2))
                pygame.draw.rect(screen, WHITE, rect.inflate(-2, -2), 1)


def draw_game_over(screen):
    font = pygame.font.SysFont(None, 48)
    text = font.render("GAME OVER", True, WHITE)

    text_rect = text.get_rect(
        center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    )

    screen.blit(text, text_rect)
    pygame.display.flip()
    pygame.time.wait(2000)


def main():
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Python Tetris")

    clock = pygame.time.Clock()

    board = create_board()
    current_piece = Piece()

    last_drop_time = pygame.time.get_ticks()
    running = True

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if is_valid_position(board, current_piece, offset_x=-1):
                        current_piece.x -= 1

                elif event.key == pygame.K_RIGHT:
                    if is_valid_position(board, current_piece, offset_x=1):
                        current_piece.x += 1

                elif event.key == pygame.K_DOWN:
                    if is_valid_position(board, current_piece, offset_y=1):
                        current_piece.y += 1

                elif event.key == pygame.K_UP:
                    old_shape = current_piece.shape
                    current_piece.rotate()

                    if not is_valid_position(board, current_piece):
                        current_piece.shape = old_shape

                elif event.key == pygame.K_SPACE:
                    while is_valid_position(
                        board,
                        current_piece,
                        offset_y=1,
                    ):
                        current_piece.y += 1

        current_time = pygame.time.get_ticks()

        if current_time - last_drop_time >= DROP_DELAY:
            if is_valid_position(board, current_piece, offset_y=1):
                current_piece.y += 1
            else:
                lock_piece(board, current_piece)
                board, _ = clear_lines(board)

                current_piece = Piece()

                if not is_valid_position(board, current_piece):
                    draw_board(screen, board)
                    draw_game_over(screen)
                    running = False

            last_drop_time = current_time

        draw_board(screen, board)
        draw_piece(screen, current_piece)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()