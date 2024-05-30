from common import assertEqual
from common import submit
from common import fill
import re


def parse_instructions(input):
  result = []
  for line in input.splitlines():
    m = re.match("(\w) (\d+) \(#(\w+)\)", line)
    result.append((m.group(1), int(m.group(2)), m.group(3)))
  return result


assertEqual([('R', 6, '70c710')], parse_instructions('R 6 (#70c710)'))

DIRECTIONS = {
    'U': (-1, 0),
    'D': (1, 0),
    'L': (0, -1),
    'R': (0, 1),
}


def dig(instructions):
  dug = {}
  r, c = 0, 0
  dug[(r, c)] = '#'
  for inst in instructions:
    direction, distance, color = inst
    dr, dc = DIRECTIONS[direction]
    for _ in range(distance):
      r += dr
      c += dc
      dug[(r, c)] = '#'
  return dug


def calibrate(dug):
  min_r = min(r for r, c in dug)
  min_c = min(c for r, c in dug)
  max_r = max(r for r, c in dug)
  max_c = max(c for r, c in dug)
  return [[dug.get((r, c), '.')
           for c in range(min_c-1, max_c+2)]
          for r in range(min_r-1, max_r+2)]


def pretty_print_grid(grid):
  return '\n'.join(''.join(row) for row in grid)


def day18(input):
  instructions = parse_instructions(input)

  boundary = dig(instructions)
  calibrated = calibrate(boundary)
  trench_length = pretty_print_grid(calibrated).count('#')
  fill(calibrated, 0, 0, '.', '#')
  num_unfilled = pretty_print_grid(calibrated).count('.')

  return trench_length + num_unfilled


test_input = '''\
R 6 (#70c710)
D 5 (#0dc571)
L 2 (#5713f0)
D 2 (#d2c081)
R 2 (#59c680)
D 2 (#411b91)
L 5 (#8ceee2)
U 2 (#caa173)
L 1 (#1b58a2)
U 2 (#caa171)
R 2 (#7807d2)
U 3 (#a77fa3)
L 2 (#015232)
U 2 (#7a21e3)
'''
test_output = 62

assertEqual(test_output, day18(test_input))


print('day18 answer:')
submit(day18(open('day18_input.txt', 'r').read()),
       expected=48400)
print()
