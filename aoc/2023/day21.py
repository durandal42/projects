from common import assertEqual
from common import submit
from collections import deque


def day21(input, steps):
  grid = input.splitlines()
  r = next(r for r, row in enumerate(grid) if 'S' in row)
  c = grid[r].index('S')
  shortest_paths = shortest_paths_from(grid, r, c)
  return len([s for s in shortest_paths.values()
              if s <= steps and s % 2 == steps % 2])


def shortest_paths_from(grid, r, c):
  frontier = deque()
  shortest_paths = dict()
  start = (r, c)
  frontier.appendleft(start)
  shortest_paths[start] = 0
  while frontier:
    loc = frontier.pop()
    r, c = loc
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
      nr, nc = r + dr, c + dc
      if (nr, nc) in shortest_paths:
        continue
      if nr not in range(len(grid)):
        continue
      if nc not in range(len(grid[0])):
        continue
      if grid[nr][nc] == '#':
        continue

      frontier.appendleft((nr, nc))
      shortest_paths[(nr, nc)] = shortest_paths[(r, c)] + 1

  return shortest_paths


test_input = '''\
...........
.....###.#.
.###.##..#.
..#.#...#..
....#.#....
.##..S####.
.##..#...#.
.......##..
.##.#.####.
.##..##.##.
...........
'''
test_param = 6
test_output = 16

assertEqual(test_output, day21(test_input, test_param))


print('day21 answer:')
submit(day21(open('day21_input.txt', 'r').read(), 64),
       expected=3809)
print()
