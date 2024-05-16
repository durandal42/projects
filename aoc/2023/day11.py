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


def expand_rows(universe):
  result = []
  for row in universe:
    if '#' not in row:
      result.append(row)
    result.append(row)
  return result


def expand(universe):
  return expand_rows(transpose(expand_rows(transpose(universe))))


def find_galaxies(universe):
  for r, row in enumerate(universe):
    for c, x in enumerate(row):
      if x == '#':
        yield (r, c)


def distance(g1, g2):
  x1, y1 = g1
  x2, y2 = g2
  return abs(x1 - x2) + abs(y1 - y2)


def day11(input):
  galaxies = list(find_galaxies(expand(parse_input(input))))
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
test_expanded_universe = '''....#........
.........#...
#............
.............
.............
........#....
.#...........
............#
.............
.............
.........#...
#....#.......
'''
assertEqual(parse_input(test_expanded_universe),
            expand(parse_input(test_input)))
test_output = 374

assertEqual(test_output, day11(test_input))


print('day11 answer:')
submit(day11(open('day11_input.txt', 'r').read()),
       expected=9693756)
print()
