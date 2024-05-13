from common import assertEqual
from common import submit
import collections


def day10(input):
  grid = parse_input(input)
  # print('\n'.join(grid))
  # print(find_start(grid))

  frontier = collections.deque()
  seen = set()
  frontier.appendleft((0, find_start(grid)))
  max_steps = 0
  while frontier:
    # print('frontier:', frontier)
    # print('len(frontier):', len(frontier))
    steps, loc = frontier.pop()
    if loc in seen:
      continue
    seen.add(loc)
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
          # connection found!
  return max_steps

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
  return list(input.splitlines())


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
