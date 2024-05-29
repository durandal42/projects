from common import assertEqual
from common import submit
import collections


def day10(input):
  grid = parse_input(input)
  # print_grid(grid)
  # print(find_start(grid))
  return find_main_loop(grid)[0]


def print_grid(grid):
  print('\n'.join(''.join(row) for row in grid))


def find_main_loop(grid):
  frontier = collections.deque()
  seen = set()
  start = find_start(grid)
  start_connections = []
  frontier.appendleft((0, start))
  seen.add(start)
  max_steps = 0
  while frontier:
    # print('frontier:', frontier)
    # print('len(frontier):', len(frontier))
    steps, loc = frontier.pop()
    # print('seen:', seen)
    # print('len(seen):', len(seen))
    max_steps = max(max_steps, steps)

    r, c = loc
    # print(r, c)
    tile = grid[r][c]
    # print(tile)
    for connection in TILES[tile]:
      dr, dc = DIRECTIONS[connection]
      nr, nc = r + dr, c + dc
      if (nr, nc) in seen:
        continue
      if nr not in range(len(grid)):
        continue
      if nc not in range(len(grid[0])):
        continue
      nt = grid[nr][nc]
      for reverse_connection in TILES[nt]:
        rdr, rdc = DIRECTIONS[reverse_connection]
        if rdr == -dr and rdc == -dc:
          frontier.appendleft((steps + 1, (nr, nc)))
          seen.add((nr, nc))
          if loc == start:
            start_connections.append(connection)
          # connection found!

  for tile, connections in TILES.items():
    if connections == start_connections:
      r, c = start
      grid[r][c] = tile
  for r, row in enumerate(grid):
    for c, _ in enumerate(row):
      if (r, c) not in seen:
        grid[r][c] = '.'

  return max_steps, seen


test_input = '''.....
.S-7.
.|.|.
.L-J.
.....
'''
test_output = 4

TILES = {
    '|': ['N', 'S'],
    '-': ['E', 'W'],
    'L': ['N', 'E'],
    'J': ['N', 'W'],
    '7': ['S', 'W'],
    'F': ['S', 'E'],
    '.': [],
    'S': ['N', 'S', 'E', 'W'],
}
OPPOSITES = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}
DIRECTIONS = {
    'N': (-1, 0),
    'S': (1, 0),
    'E': (0, 1),
    'W': (0, -1),
}


def parse_input(input):
  return [list(line) for line in input.splitlines()]


def find_start(grid):
  for r, row in enumerate(grid):
    if 'S' in row:
      return (r, row.index('S'))
  return None


assertEqual(test_output, day10(test_input))


print('day10 answer:')
submit(day10(open('day10_input.txt', 'r').read()),
       expected=6867)
print()

# part 2 complication

TILE_EXPLOSIONS = {
    '|': ['.|.',
          '.|.',
          '.|.'],
    '-': ['...',
          '---',
          '...'],
    'L': ['.|.',
          '.L-',
          '...'],
    'J': ['.|.',
          '-J.',
          '...'],
    '7': ['...',
          '-7.',
          '.|.'],
    'F': ['...',
          '.F-',
          '.|.'],
    '.': ['...',
          '...',
          '...'],
}


def explode_grid(grid):
  exploded_grid = [[None] * len(grid[0]) * 3 for _ in range(len(grid) * 3)]
  for r, row in enumerate(grid):
    for c, tile in enumerate(row):
      exploded_tile = TILE_EXPLOSIONS[tile]
      for dr in [0, 1, 2]:
        for dc in [0, 1, 2]:
          exploded_grid[3 * r + dr][3 * c + dc] = exploded_tile[dr][dc]
  return exploded_grid


def fill(grid, start):
  frontier = collections.deque()
  seen = set()
  frontier.appendleft(start)
  seen.add(start)
  while frontier:
    # print('len(frontier) =', len(frontier))
    loc = frontier.pop()
    r, c = loc
    # print(loc)
    grid[r][c] = 'X'
    for dr in [-1, 0, 1]:
      for dc in [-1, 0, 1]:
        nr, nc = r + dr, c + dc
        if (nr, nc) in seen:
          continue
        if nr not in range(len(grid)):
          continue
        if nc not in range(len(grid[0])):
          continue
        if grid[nr][nc] != '.':
          continue

        frontier.appendleft((nr, nc))
        seen.add((nr, nc))

  return len(seen)


def collapse_grid(grid):
  collapsed_grid = [[None] * (len(grid[0]) // 3) for _ in range(len(grid) // 3)]
  for r, row in enumerate(grid):
    if r % 3 != 1:
      continue
    for c, tile in enumerate(row):
      if c % 3 != 1:
        continue
      collapsed_grid[r // 3][c // 3] = grid[r][c]
  return collapsed_grid


def day10(input):
  grid = parse_input(input)
  # print_grid(grid)
  # print(find_start(grid))
  find_main_loop(grid)
  # print_grid(grid)
  # print("kaboom!")
  exploded = explode_grid(grid)
  # print_grid(exploded)
  # print("filling...")
  fill(exploded, (0, 0))
  # print_grid(grid)
  collapsed = collapse_grid(exploded)
  # print_grid(collapsed)
  return sum(''.join(row).count('.') for row in collapsed)


assertEqual(4, day10('''\
...........
.S-------7.
.|F-----7|.
.||.....||.
.||.....||.
.|L-7.F-J|.
.|..|.|..|.
.L--J.L--J.
...........
'''))

assertEqual(8, day10('''\
.F----7F7F7F7F-7....
.|F--7||||||||FJ....
.||.FJ||||||||L7....
FJL7L7LJLJ||LJ.L-7..
L--J.L7...LJS7F-7L7.
....F-J..F7FJ|L7L7L7
....L7.F7||L7|.L7L7|
.....|FJLJ|FJ|F7|.LJ
....FJL-7.||.||||...
....L---J.LJ.LJLJ...
'''))


assertEqual(10, day10('''\
FF7FSF7F7F7F7F7F---7
L|LJ||||||||||||F--J
FL-7LJLJ||||||LJL-77
F--JF--7||LJLJ7F7FJ-
L---JF-JLJ.||-FJLJJ7
|F|F-JF---7F7-L7L|7|
|FFJF7L7F-JF7|JL---7
7-L-JL7||F7|L7F-7F7|
L.L7LFJ|||||FJL7||LJ
L7JLJL-JLJLJL--JLJ.L
'''))


print('day10, part2 answer:')
submit(day10(open('day10_input.txt', 'r').read()),
       expected=595)
print()
