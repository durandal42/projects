from common import assertEqual
from common import submit

import collections
import itertools
import math


def tuple_add(t1, t2):
  return tuple(x1 + x2 for x1, x2 in zip(t1, t2))


def tuple_scale(t, scale):
  return tuple(map(lambda x: scale * x, t))


def in_range(t, limit_t):
  return all(c in range(limit_c) for c, limit_c in zip(t, limit_t))


def antinodes_from_antennae(loc1, loc2, num_rows, num_cols):
  delta = tuple_add(loc2, tuple_scale(loc1, -1))
  a1 = tuple_add(loc1, tuple_scale(delta, -1))
  a2 = tuple_add(loc2, delta)
  if in_range(a1, (num_rows, num_cols)):
    yield a1
  if in_range(a2, (num_rows, num_cols)):
    yield a2


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
      for a in antinodes_from_antennae(loc1, loc2, num_rows, num_cols):
        antinodes.add(a)

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

# part 2 complication

test_output = 34


def antinodes_from_antennae(loc1, loc2, num_rows, num_cols):
  delta = tuple_add(loc2, tuple_scale(loc1, -1))
  if delta[0] == 0:
    delta = (1, 0)
  elif delta[1] == 0:
    delta = (0, 1)
  else:
    delta = tuple_scale(delta, 1 / math.gcd(abs(delta[0]), abs(delta[1])))

  t = loc1
  while in_range(t, (num_rows, num_cols)):
    yield t
    t = tuple_add(t, tuple_scale(delta, -1))

  t = tuple_add(loc1, delta)
  while in_range(t, (num_rows, num_cols)):
    yield t
    t = tuple_add(t, delta)


assertEqual(test_output, day08(test_input))


print('day08, part 2 answer:')
submit(day08(open('day08_input.txt', 'r').read()),
       expected=949)
print()
