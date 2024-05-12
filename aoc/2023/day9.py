from common import assertEqual
from common import submit
import math


def day9(input):
  return sum(extrapolate(find_pattern(parse_line(line))) for line in input.splitlines())


def parse_line(line):
  return [int(n) for n in line.split()]

assertEqual([0, 3, 6, 9, 12, 15], parse_line('0 3 6 9 12 15'))


def pretty_print_grid(grid):
  for i, row in enumerate(grid):
    print('  ' * i, row)


def find_pattern(values):
  grid = [values]
  while any(v != 0 for v in grid[-1]):
    grid.append([second - first
                 for first, second
                 in zip(grid[-1][:-1], grid[-1][1:])])
  # pretty_print_grid(grid)
  return grid


def choose(n, k):
  # Like math.comb(n, k), but works with negative n.
  return math.prod(range(n, n - k, -1)) // math.factorial(k)


def extrapolate_anywhere(grid, n):
  # https://www.youtube.com/watch?v=4AuV93LOPcE#t=16m03s
  return sum(values[0] * choose(n, i) for i, values in enumerate(grid))


def extrapolate(grid):
  return extrapolate_anywhere(grid, len(grid[0]))

test_input = '''0 3 6 9 12 15
1 3 6 10 15 21
10 13 16 21 30 45
'''
test_output = 114

assertEqual(test_output, day9(test_input))


print('day9 answer:')
submit(day9(open('day9_input.txt', 'r').read()),
       expected=1762065988)
print()

# part 2 complication
test_output = 2


def extrapolate(grid):
  return extrapolate_anywhere(grid, -1)


assertEqual(test_output, day9(test_input))

print('day9, part2 answer:')
submit(day9(open('day9_input.txt', 'r').read()),
       expected=1066)
print()
