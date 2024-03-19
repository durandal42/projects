import pyautogui
import math
import PIL
import collections
import time
import random
import itertools


def show_entire_screen():
    pyautogui.screenshot().show()


def get_unique_window_named(name):
    windows = pyautogui.getWindowsWithTitle(name)
    for w in windows:
        if w.title == name:
            return w
    assert len(windows) == 1
    return windows[0]


def capture_window(w):
    # print(w)
    bounds = (w.left, w.top, w.width, w.height)
    # print(dir(w))
    # print(bounds)
    w.activate()
    return pyautogui.screenshot(region=bounds)


def draw_zone(draw, cx, cy, r, outline=(255, 0, 0), fill=None):
    left = cx - r
    right = cx + r
    top = cy - r
    bottom = cy + r
    draw.ellipse((left, top, right, bottom), outline=outline, fill=fill)


def guess_color(pix, cx, cy, r):
    counter = collections.Counter()
    left = int(cx - r)
    right = int(cx + r)
    top = int(cy - r)
    bottom = int(cy + r)
    for x in range(left, right):
        for y in range(top, bottom):
            counter[pix[x, y]] += 1
    return counter.most_common(1)[0][0]


COLORS = [17, 30, 44, 57, 71, 85]
RADIUS = 44.7


def grid_to_xy(row, col):
    per_col_offset = [
        math.cos(math.radians(-30)) * RADIUS * 2,
        -math.sin(math.radians(-30)) * RADIUS * 2,
    ]
    per_row_offset = [
        math.cos(math.radians(-150)) * RADIUS * 2,
        -math.sin(math.radians(-150)) * RADIUS * 2,
    ]
    origin = (305, 361)
    cx = origin[0] + int(row * per_row_offset[0]) + \
        int(col * per_col_offset[0])
    cy = origin[1] + int(row * per_row_offset[1]) + \
        int(col * per_col_offset[1])
    return cx, cy


def cells():
    for row in range(0, 7):
        for col in range(0, 7):
            if row < 3 and col > row + 3:
                continue
            if row > 3 and col < row - 3:
                continue
            yield row, col


def read_grid(img):
    draw = PIL.ImageDraw.Draw(img)
    pix = img.load()
    colors_seen = set()
    grid = {}
    for row, col in cells():
        cx, cy = grid_to_xy(row, col)
        color = guess_color(pix, cx, cy, RADIUS)
        number = COLORS.index(color[0]) + 1
        grid[row, col] = number
        draw_zone(draw, cx, cy, RADIUS)
        draw_zone(draw, cx, cy, RADIUS/2, outline=color, fill=color)
        draw.text((cx, cy), str(number))
    draw_zone(draw, 305, 1020, 10)
    return grid


NEIGHBORS = [
    (-1, -1), (-1, 0),
    (0, -1), (0, 0), (0, 1),
    (1, 0), (1, 1),
]


def click(grid, clicks, pos):
    if pos not in grid:
        print("Tried to click a bad position!", pos)
    r, c = pos
    clicks[pos] += 1
    for dr, dc in NEIGHBORS:
        increment(grid, (r+dr, c+dc))


def increment(grid, pos):
    if pos in grid:
        grid[pos] = grid[pos] % 6 + 1


def propagate(grid, clicks):
    for r, c in sorted(grid.keys()):
        if (r+1, c+1) not in grid:
            continue
        while grid[r, c] != 1:
            click(grid, clicks, (r+1, c+1))


def solve_grid(grid, expert=False):
    clicks = collections.defaultdict(int)
    # propagate:
    propagate(grid, clicks)

    # Label the bottom right cells (from left to right): A, B, C, D.
    big_a = (6, 6)
    big_b = (5, 6)
    big_c = (4, 6)
    big_d = (3, 6)
    # Label the top right cells (from left to right): a, b, c, d.
    a = (0, 0)
    b = (0, 1)
    c = (0, 2)
    d = (0, 3)

    # Tap a so that a is the same as C.
    while grid[a] != grid[big_c]:
        click(grid, clicks, a)
    # Tap b and d the number of times you will need to solve C.
    for _ in range(7-grid[big_c]):
        click(grid, clicks, b)
        click(grid, clicks, d)
    # Tap a the number of times you would need to solve D.
    for _ in range(7-grid[big_d]):
        click(grid, clicks, a)
    # If B + D is odd, tap c three times (once in Hard).
    if (grid[big_b] + grid[big_d]) % 2 == 1:
        for _ in range(3):
            click(grid, clicks, c)
    # propagate from top once more to finish the solve.
    propagate(grid, clicks)

    result = []
    for k, v in clicks.items():
        for _ in range(v % (expert and 6 or 2)):
            result.append(k)

    return result


def deploy_solution_into_window(clicks, w):
    w.activate()
    pyautogui.PAUSE = 0.00
    num_clicks = 0
    for c in clicks:
        row, col = c
        x, y = grid_to_xy(row, col)
        pyautogui.click(x=x+w.left, y=y+w.top)
    time.sleep(0.4)
    pyautogui.click(x=305+w.left, y=1020+w.top)
    time.sleep(0.2)
    return len(clicks)


def spiral_cells():
    all_cells = set(cells())
    seen_cells = set()
    frontier = collections.deque()
    frontier.append((3, 3))
    spiral_neighbors = sorted(NEIGHBORS, key=lambda x: -math.atan2(x[0], x[1]))
    result = {}
    while frontier:
        c = frontier.popleft()
        if c not in all_cells:
            continue
        if c in seen_cells:
            continue
        result[c] = len(result)
        seen_cells.add(c)
        for n in spiral_neighbors:
            frontier.append((c[0] + n[0], c[1] + n[1]))
    return result


def sorted_clicks(clicks, method=None):
    if method == 'random':
        random.shuffle(clicks)
        return clicks
    if method == 'top-down':
        return sorted(clicks, key=lambda x: sum(x))
    if method == 'outside-in':
        sc = spiral_cells()
        return sorted(clicks, key=lambda x: sc[x])
    if method == 'inside-out':
        sc = spiral_cells()
        return sorted(clicks, key=lambda x: sc[x], reverse=True)
    return sorted(clicks)


def main():
    w = get_unique_window_named("BlueStacks")
    solves = collections.Counter()
    for i in itertools.count():  # range(10):
        print("Grid", i, "...", end='')
        print(" capturing...", end='')
        img = capture_window(w)
        try:
            grid = read_grid(img)
        except:
            img.show()
            return
        # img.show()
        # print(grid)
        print(" solving...", end='')
        solution = solve_grid(grid, expert=False)
        solution = sorted_clicks(solution, method='random')
        # print(solution)
        print(" clicking...", end='')
        num_clicks = deploy_solution_into_window(solution, w)
        solves[num_clicks] += 1
        print(" done in", num_clicks, "clicks.")
        time.sleep(0.3)
    print("Solves by click count:", sorted(solves.items()))


main()
