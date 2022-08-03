import pygame as pg
from pprint import PrettyPrinter
from queue import Queue
import random

pg.init()

printer = PrettyPrinter()

width = 1000
height = 800
win = pg.display.set_mode((width, height))

BG_COLOR = "white"
FONT = pg.font.SysFont('comicsans', 20)
LOST_FONT = pg.font.SysFont('comicsans', 80)
RESET_FONT = pg.font.SysFont('comicsans', 20)


NUM_COLORS = {-1: "black", 1: "black", 2: (0, 150, 0), 3: (200, 0, 0), 4: (0, 0, 200), 5: "yellow",
              6: "orange", 7: "violet", 8: "pink"}
RECT_COLOR = (150, 100, 100)
CLICKED_COLOR = (200, 200, 200)
FLAG_COLOR = (255, 200, 0)
BOMB_COLOR = "red"

Font = pg.font.SysFont('Arial', 20)

ROWS = 20
COLS = 20
MINES = 40

SIZE = height // ROWS - 5


def draw(window, field, cover):
    window.fill(BG_COLOR)

    for i, row in enumerate(field):
        y = SIZE * i + (height - ROWS * SIZE) / 2
        for j, value in enumerate(row):
            x = SIZE * j + (width - COLS * SIZE) / 2

            is_covered = cover[i][j] == 0
            is_flag = cover[i][j] == -2
            is_bomb = value == -1

            if is_flag:
                pg.draw.rect(win, FLAG_COLOR, (x, y, SIZE, SIZE))
                pg.draw.rect(win, "black", (x, y, SIZE, SIZE), 2)
                continue

            if is_covered:
                pg.draw.rect(win, RECT_COLOR, (x, y, SIZE, SIZE))
                pg.draw.rect(win, "black", (x, y, SIZE, SIZE), 2)
                continue
            else:
                pg.draw.rect(win, CLICKED_COLOR, (x, y, SIZE, SIZE))
                pg.draw.rect(win, "black", (x, y, SIZE, SIZE), 2)
                if is_bomb:
                    pg.draw.circle(win, BOMB_COLOR, (x + SIZE / 2, y + SIZE / 2), (SIZE - 4) / 2)
                    pg.draw.circle(win, CLICKED_COLOR, (x + SIZE / 2, y + SIZE / 2), (SIZE - 10) / 2)
                    pg.draw.circle(win, BOMB_COLOR, (x + SIZE / 2, y + SIZE / 2), (SIZE - 20) / 2)

            if value > 0:
                text = FONT.render(str(value), True, NUM_COLORS[value])
                win.blit(text, (x + (SIZE / 2 - text.get_width() / 2), y + (SIZE / 2 - text.get_height() / 2)))

    pg.display.update()


def get_neighbors(row, col, rows, cols):
    neighbors = []

    if row > 0:  # down
        neighbors.append((row - 1, col))
    if row < rows - 1:  # up
        neighbors.append((row + 1, col))
    if col > 0:  # left
        neighbors.append((row, col - 1))
    if col < cols - 1:  # right
        neighbors.append((row, col + 1))

    if row > 0 and col > 0:
        neighbors.append((row - 1, col - 1))
    if row > 0 and col < cols - 1:
        neighbors.append((row - 1, col + 1))
    if row < rows - 1 and col > 0:
        neighbors.append((row + 1, col - 1))
    if row < rows - 1 and col < cols - 1:
        neighbors.append((row + 1, col + 1))

    return neighbors


def create_minefield(rows, cols, mines):
    field = [[0 for _ in range(cols)] for _ in range(rows)]

    mine_positions = set()

    while len(mine_positions) < mines:
        row = random.randrange(rows)
        col = random.randrange(cols)
        mine_pos = (row, col)

        if mine_pos in mine_positions:
            continue
        mine_positions.add(mine_pos)
        field[row][col] = -1

    for mine in mine_positions:
        neighbors = get_neighbors(*mine, ROWS, COLS)

        for r, c in neighbors:
            if field[r][c] != -1:
                field[r][c] += 1

    return field, mine_positions


def get_cell(mouse_pos):
    mx, my = mouse_pos

    row = int((my - (height - ROWS * SIZE) / 2) // SIZE)
    col = int((mx - (width - COLS * SIZE) / 2) // SIZE)

    return row, col


def uncover_blank(row, col, field, cover):
    q = Queue()
    q.put((row, col))
    visited = set()

    while not q.empty():

        (r1, c1) = q.get()

        neighbors = get_neighbors(r1, c1, ROWS, COLS)
        for r, c in neighbors:
            if (r, c) in visited:
                continue

            val = field[r][c]
            if val == 0 and cover[r][c] != -2:
                q.put((r, c))
            if cover[r][c] != -2:
                cover[r][c] = 1
            visited.add((r, c))


def draw_lost(window, text):
    # window.fill("white")
    text = LOST_FONT.render(text, True, "black")
    pg.draw.rect(window, "white", (width / 2 - text.get_width() / 2, height / 2 - text.get_height() / 2,
                                   text.get_width() + 20, text.get_height() + 20))
    pg.draw.rect(window, "black", (width / 2 - text.get_width() / 2 - 20, height / 2 - text.get_height() / 2,
                                   text.get_width() + 40, text.get_height() + 20), 2)
    win.blit(text, (width / 2 - text.get_width() / 2, height / 2 - text.get_height() / 2))
    pg.display.update()


def draw_reset(text):
    # window.fill("white")
    text = RESET_FONT.render(text, True, "black")
    win.blit(text, (20, 20))
    pg.display.flip()


def create_game():
    field, mine_pos = create_minefield(ROWS, COLS, MINES)
    cover = [[0 for _ in range(ROWS)] for _ in range(COLS)]

    return field, cover, mine_pos


def main():
    run = True

    field, cover, mine_pos = create_game()

    pg.display.flip()

    flags = MINES
    lost = False

    while run:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
                break
            if event.type == pg.MOUSEBUTTONDOWN:
                if not lost:
                    row, col = get_cell(pg.mouse.get_pos())
                    if row >= ROWS or col >= COLS:
                        continue

                    mouse_pressed = pg.mouse.get_pressed()
                    if mouse_pressed[0] and cover[row][col] != -2:
                        cover[row][col] = 1
                        if field[row][col] == 0:
                            uncover_blank(row, col, field, cover)
                        if field[row][col] == -1:
                            draw_lost(win, "You lost!! Try Again...")
                            pg.time.delay(2000)
                            for r, c in mine_pos:
                                cover[r][c] = 1
                            draw_reset("Click anywhere to reset field....")
                            # draw_lost(win, "Click anywhere to reset field....")
                            pg.display.flip()
                            pg.time.delay(2000)
                            lost = True
                    elif mouse_pressed[2] and flags > 0:
                        if cover[row][col] == -2:
                            cover[row][col] = 0
                            flags += 1
                        else:
                            if field[row][col] != -1 and cover[row][col] != 1:
                                cover[row][col] = -2
                                flags -= 1
                            elif cover[row][col] == 0:
                                cover[row][col] = -2
                                flags -= 1
                else:
                    mouse_pressed = pg.mouse.get_pressed()

                    if mouse_pressed:
                        field, cover, mine_pos = create_game()
                        lost = False

        draw(win, field, cover)

    pg.quit()


if __name__ == "__main__":
    main()
