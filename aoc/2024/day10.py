from common import assertEqual
from common import submit

import collections


def day10(input):
  grid = [[int(s) for s in row] for row in input.splitlines()]

  return sum(score_trailhead(grid, r, c)
             for r, row in enumerate(grid)
             for c, x in enumerate(row)
             )


def score_trailhead(grid, r, c):
  return len(find_reachable_peaks(grid, r, c))


def find_reachable_peaks(grid, r, c):
  if grid[r][c] != 0:
    return {}

  reachable = {(r, c): 1}
  height = 0
  while height < 9:
    newly_reachable = collections.defaultdict(int)
    height += 1
    for rc, num_paths in reachable.items():
      r, c = rc
      for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        if (r+dr in range(len(grid)) and
            c+dc in range(len(grid[r+dr])) and
                grid[r+dr][c+dc] == height):
          newly_reachable[(r+dr, c+dc)] += num_paths
    reachable = newly_reachable

  return reachable


test_input = '''\
89010123
78121874
87430965
96549874
45678903
32019012
01329801
10456732
'''
test_output = 36

assertEqual(test_output, day10(test_input))


print('day10 answer:')
submit(day10(open('day10_input.txt', 'r').read()),
       expected=574)
print()

# part 2 complication

test_output = 81


def score_trailhead(grid, r, c):
  return sum(find_reachable_peaks(grid, r, c).values())


assertEqual(test_output, day10(test_input))

print('day10, part 2 answer:')
submit(day10(open('day10_input.txt', 'r').read()),
       expected=None)
print()
