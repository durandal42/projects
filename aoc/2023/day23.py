from common import assertEqual
from common import submit
from collections import deque


def day23(input):
  grid = input.splitlines()
  r = 0
  c = grid[r].index('.')
  return longest_path(input.splitlines(), r, c)
  pass


def longest_path(grid, r, c):
  frontier = deque()
  frontier.appendleft((r, c, ()))
  max_steps = 1
  while frontier:
    r, c, path = frontier.pop()
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    here = grid[r][c]
    directions = {
        '^': [(-1, 0)],
        'v': [(1, 0)],
        '>': [(0, 1)],
        '<': [(0, -1)],
    }.get(grid[r][c], [(-1, 0), (1, 0), (0, -1), (0, 1)])
    for dr, dc in directions:
      nr, nc = r + dr, c + dc
      if (nr, nc) in path:
        continue
      if nr not in range(len(grid)):
        continue
      if nc not in range(len(grid[nr])):
        continue
      if grid[nr][nc] == '#':
        continue
      frontier.appendleft((nr, nc, path + ((r, c),)))
      max_steps = max(max_steps, len(path))

  return max_steps + 1


test_input = '''\
#.#####################
#.......#########...###
#######.#########.#.###
###.....#.>.>.###.#.###
###v#####.#v#.###.#.###
###.>...#.#.#.....#...#
###v###.#.#.#########.#
###...#.#.#.......#...#
#####.#.#.#######.#.###
#.....#.#.#.......#...#
#.#####.#.#.#########v#
#.#...#...#...###...>.#
#.#.#v#######v###.###v#
#...#.>.#...>.>.#.###.#
#####v#.#.###v#.#.###.#
#.....#...#...#.#.#...#
#.#########.###.#.#.###
#...###...#...#...#.###
###.###.#.###v#####v###
#...#...#.#.>.>.#.>.###
#.###.###.#.###.#.#v###
#.....###...###...#...#
#####################.#
'''
test_output = 94

assertEqual(test_output, day23(test_input))


print('day23 answer:')
submit(day23(open('day23_input.txt', 'r').read()),
       expected=2190)
print()
