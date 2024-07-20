from common import assertEqual
from common import submit
from collections import deque
import day09


def day21(input, steps):
  grid = input.splitlines()
  r, c = find_start(grid)
  return steps_reachable_in(grid, r, c, steps)


def find_start(grid):
  r = next(r for r, row in enumerate(grid) if 'S' in row)
  c = grid[r].index('S')
  return r, c


def steps_reachable_in(grid, r, c, steps):
  shortest_paths = shortest_paths_from(grid, r, c, steps)
  return len([s for s in shortest_paths.values()
              if s % 2 == steps % 2])


def shortest_paths_from(grid, r, c, max_steps):
  rows, cols = len(grid), len(grid[0])
  frontier = deque()
  shortest_paths = dict()
  start = (r, c)
  frontier.appendleft(start)
  shortest_paths[start] = 0
  while frontier:
    loc = frontier.pop()
    r, c = loc
    if shortest_paths[(r, c)] > max_steps:
      break
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
      nr, nc = r + dr, c + dc
      if (nr, nc) in shortest_paths:
        continue
      if grid[nr % rows][nc % cols] == '#':
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

# part 2 complication

for steps, plots in [
    (6, 16),
    (10, 50),
    (50, 1594),
    (100, 6536),
    # (500, 167004),
    # (1000, 668697),
    # (5000, 16733044),
]:
  assertEqual(plots, day21(test_input, steps))


def day21(input, steps):
  grid = input.splitlines()
  r, c = find_start(grid)
  assertEqual(r, steps % len(grid))  # necessary for pattern-matching
  examples = [steps_reachable_in(grid, r, c, r + len(grid) * i)
              for i in range(3)]  # enough to fit a quadratic, which this probably is
  pattern = day09.find_pattern(examples)
  print(pattern)
  return day09.extrapolate_anywhere(pattern, steps // len(grid))


print('day21 answer:')
submit(day21(open('day21_input.txt', 'r').read(), 26501365),
       expected=629720570456311)
print()
