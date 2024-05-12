from common import assertEqual
from common import submit


def day9(input):
  return sum(extrapolate(parse_line(line)) for line in input.splitlines())


def parse_line(line):
  return [int(n) for n in line.split()]

assertEqual([0, 3, 6, 9, 12, 15], parse_line('0 3 6 9 12 15'))


def pretty_print_grid(grid):
  for i, row in enumerate(grid):
    print('  ' * i, row)


def extrapolate(values):
  grid = [values]
  while any(v != 0 for v in grid[-1]):
    grid.append([second - first
                 for first, second
                 in zip(grid[-1][:-1], grid[-1][1:])])
  pretty_print_grid(grid)
  print("->")
  grid[-1].append(0)
  for i in range(len(grid) - 2, -1, -1):
    grid[i].append(grid[i][-1] + grid[i + 1][-1])
  pretty_print_grid(grid)
  print()
  return grid[0][-1]

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
