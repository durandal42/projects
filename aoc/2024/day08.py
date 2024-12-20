from common import assertEqual
from common import submit

import collections
import itertools


def day08(input):
  grid = input.splitlines()
  num_rows = len(grid)
  num_cols = len(grid[0])

  ants = {}
  for r, row in enumerate(grid):
    for c, x in enumerate(row):
      if x != ".":
        ants[r, c] = x

  ants_by_freq = collections.defaultdict(list)
  for loc, freq in ants.items():
    ants_by_freq[freq].append(loc)

  antinodes = set()
  for freq, locs in ants_by_freq.items():
    for loc1, loc2 in itertools.combinations(locs, 2):
      delta = loc2[0] - loc1[0], loc2[1] - loc1[1]
      a1 = loc1[0] - delta[0], loc1[1] - delta[1]
      a2 = loc2[0] + delta[0], loc2[1] + delta[1]
      if a1[0] in range(num_rows) and a1[1] in range(num_cols):
        antinodes.add(a1)
      if a2[0] in range(num_rows) and a2[1] in range(num_cols):
        antinodes.add(a2)

  return len(antinodes)


test_input = '''\
............
........0...
.....0......
.......0....
....0.......
......A.....
............
............
........A...
.........A..
............
............
'''
test_output = 14

assertEqual(test_output, day08(test_input))


print('day08 answer:')
submit(day08(open('day08_input.txt', 'r').read()),
       expected=269)
print()
