import random
import time

import displayio
import terminalio


BOARD_W = 18
BOARD_H = 18
PLAY_MIN = 1
PLAY_MAX_X = BOARD_W - 2
PLAY_MAX_Y = BOARD_H - 2
CELL_SCALE = 8

COLOR_BG = 0
COLOR_GRID = 1
COLOR_BODY = 2
COLOR_HEAD = 3
COLOR_FOOD = 4
COLOR_WALL = 5


class EdgeButton:
    def __init__(self):
        self.last = True

    def pressed(self, value):
        hit = self.last and not value
        self.last = value
        return hit


def make_text_grid(width, x, y, color=0x9CFF70):
    text_palette = displayio.Palette(2)
    text_palette[0] = 0x000000
    text_palette[1] = color
    w, h = terminalio.FONT.get_bounding_box()
    grid = displayio.TileGrid(
        terminalio.FONT.bitmap,
        tile_width=w,
        tile_height=h,
        pixel_shader=text_palette,
        width=width,
        height=1,
    )
    grid.x = x
    grid.y = y
    return grid, terminalio.Terminal(grid, terminalio.FONT)


def write_line(term, text, width):
    line = text[:width]
    while len(line) < width:
        line += " "
    term.write("\r" + line)


def clear_board(board):
    for y in range(BOARD_H):
        for x in range(BOARD_W):
            if x == 0 or y == 0 or x == BOARD_W - 1 or y == BOARD_H - 1:
                board[x, y] = COLOR_WALL
            elif (x + y) & 1:
                board[x, y] = COLOR_GRID
            else:
                board[x, y] = COLOR_BG


def erase_cell(board, x, y):
    board[x, y] = COLOR_GRID if ((x + y) & 1) else COLOR_BG


def spawn_food(snake):
    while True:
        x = random.randint(PLAY_MIN, PLAY_MAX_X)
        y = random.randint(PLAY_MIN, PLAY_MAX_Y)
        if (x, y) not in snake:
            return x, y


def draw_snake(board, snake):
    for i, cell in enumerate(snake):
        x, y = cell
        board[x, y] = COLOR_HEAD if i == 0 else COLOR_BODY


def reset_game(board):
    clear_board(board)
    snake = [(9, 9), (8, 9), (7, 9)]
    direction = (1, 0)
    pending_direction = direction
    food = spawn_food(snake)
    draw_snake(board, snake)
    board[food[0], food[1]] = COLOR_FOOD
    return snake, direction, pending_direction, food, 0, False


def snake_game(hw_state):
    display = hw_state["display"]
    fpga_buttons = hw_state["fpga_overlay"].set_mode_buttons()
    button_a = hw_state["btn_action"][0]
    button_b = hw_state["btn_action"][1]

    palette = displayio.Palette(6)
    palette[COLOR_BG] = 0x04140A
    palette[COLOR_GRID] = 0x062010
    palette[COLOR_BODY] = 0x22CC55
    palette[COLOR_HEAD] = 0xD8FF55
    palette[COLOR_FOOD] = 0xFF3355
    palette[COLOR_WALL] = 0x3E7050

    board = displayio.Bitmap(BOARD_W, BOARD_H, 6)
    board_grid = displayio.TileGrid(board, pixel_shader=palette)
    board_group = displayio.Group(scale=CELL_SCALE)
    board_group.x = (240 - (BOARD_W * CELL_SCALE)) // 2
    board_group.y = 50
    board_group.append(board_grid)

    title_grid, title = make_text_grid(8, 96, 16, 0xD8FF55)
    score_grid, score_text = make_text_grid(9, 93, 31, 0x9CFF70)
    hint_grid, hint = make_text_grid(14, 78, 205, 0x79B8FF)

    root = displayio.Group()
    root.append(board_group)
    root.append(title_grid)
    root.append(score_grid)
    root.append(hint_grid)
    display.root_group = root

    write_line(title, "SNAKE", 8)
    write_line(hint, "A rst B exit", 14)

    snake, direction, pending_direction, food, score, game_over = reset_game(board)
    write_line(score_text, "SCORE 000", 9)
    tick = time.monotonic()
    delay = 0.18

    edge_a = EdgeButton()
    edge_b = EdgeButton()

    while True:
        if edge_b.pressed(button_b.value):
            return

        if edge_a.pressed(button_a.value) and game_over:
            snake, direction, pending_direction, food, score, game_over = reset_game(board)
            write_line(score_text, "SCORE 000", 9)
            write_line(title, "SNAKE", 8)
            write_line(hint, "A rst B exit", 14)
            delay = 0.18
            tick = time.monotonic()

        if not game_over:
            if fpga_buttons[0].value is False and direction != (1, 0):
                pending_direction = (-1, 0)
            elif fpga_buttons[4].value is False and direction != (-1, 0):
                pending_direction = (1, 0)
            elif fpga_buttons[1].value is False and direction != (0, 1):
                pending_direction = (0, -1)
            elif fpga_buttons[3].value is False and direction != (0, -1):
                pending_direction = (0, 1)

            now = time.monotonic()
            if now >= tick:
                tick = now + delay
                direction = pending_direction
                head_x, head_y = snake[0]
                next_head = (head_x + direction[0], head_y + direction[1])
                nx, ny = next_head

                if nx <= 0 or ny <= 0 or nx >= BOARD_W - 1 or ny >= BOARD_H - 1:
                    game_over = True
                elif next_head in snake:
                    game_over = True
                else:
                    snake.insert(0, next_head)
                    if next_head == food:
                        score += 1
                        write_line(score_text, "SCORE %03d" % score, 9)
                        delay = max(0.075, delay - 0.004)
                        food = spawn_food(snake)
                        board[food[0], food[1]] = COLOR_FOOD
                    else:
                        tail = snake.pop()
                        erase_cell(board, tail[0], tail[1])
                    draw_snake(board, snake)

                if game_over:
                    write_line(title, "GAMEOVER", 8)
                    write_line(hint, "A rst B exit", 14)

        time.sleep(0.015)
