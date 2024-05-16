from common import assertEqual
from common import submit
import itertools


def parse_input(input):
  return [list(row) for row in input.splitlines()]


def transpose(universe):
  return [[universe[r][c]
           for r in range(len(universe))]
          for c in range(len(universe[0]))]


assertEqual([[0, 1, 2]], transpose([[0], [1], [2]]))
assertEqual([[1, 2], [3, 4]], transpose(transpose([[1, 2], [3, 4]])))


def find_empty_rows(universe):
  return set(r for r, row in enumerate(universe)
             if '#' not in row)


def find_empty_space(universe):
  empty_rows = find_empty_rows(universe)
  empty_cols = find_empty_rows(transpose(universe))
  return empty_rows, empty_cols


def find_galaxies(universe):
  for r, row in enumerate(universe):
    for c, x in enumerate(row):
      if x == '#':
        yield (r, c)


def distance(g1, g2):
  x1, y1 = g1
  x2, y2 = g2
  return (abs(x1 - x2) + abs(y1 - y2))


def expand_coordinates(galaxies, space, expansion_factor):
  # merge-sort two types of coordinates: galaxies, and empty space
  to_consider = sorted([(g, 'g')
                        for g in galaxies] + [(s, 's') for s in space])
  total_expansion = 0
  for coordinate, case in to_consider:
    if case == 's':
      total_expansion += expansion_factor - 1
    if case == 'g':
      yield coordinate + total_expansion


def day11(input, expansion_factor=2):
  universe = parse_input(input)
  galaxies = list(find_galaxies(universe))
  empty_rows, empty_cols = find_empty_space(universe)
  galaxies_r = list(g[0] for g in galaxies)
  galaxies_c = list(g[1] for g in galaxies)
  galaxies_r = list(expand_coordinates(
      galaxies_r, empty_rows, expansion_factor))
  galaxies_c = list(expand_coordinates(
      galaxies_c, empty_cols, expansion_factor))
  galaxies = list(zip(galaxies_r, galaxies_c))
  return sum(distance(g1, g2)
             for g1, g2 in itertools.product(galaxies, galaxies)
             if g1 > g2)


test_input = '''...#......
.......#..
#.........
..........
......#...
.#........
.........#
..........
.......#..
#...#.....
'''
test_output = 374


assertEqual(test_output, day11(test_input))


print('day11 answer:')
submit(day11(open('day11_input.txt', 'r').read()),
       expected=9693756)
print()

# part 2 complication

assertEqual(1030, day11(test_input, 10))
assertEqual(8410, day11(test_input, 100))

print('day11, part2 answer:')
submit(day11(open('day11_input.txt', 'r').read(), 1000000),
       expected=717878258016)
print()
