from common import assertEqual
from common import submit
from common import fill
import re
import collections


def parse_instructions(input):
  result = []
  for line in input.splitlines():
    m = re.match("(\\w) (\\d+) \\(#(\\w+)\\)", line)
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
  r, c = 0, 0
  corners = []
  for inst in instructions:
    direction, distance, color = inst
    dr, dc = DIRECTIONS[direction]
    r += dr * distance
    c += dc * distance
    corners.append((r, c))
  return corners


def shoelace(coords):
  if coords[-1] != coords[0]:  # close loop as needed
    coords = coords + [coords[0]]
  result = 0
  for coord1, coord2 in zip(coords[:-1], coords[1:]):
    r1, c1 = coord1
    r2, c2 = coord2
    result += r1 * c2 - r2 * c1
  return result


def sign(x):
  return bool(x > 0) - bool(x < 0)


def fix_corners(corners):
  # nudge corners so we can treat them as spatial coordinates instead of grid cells.
  assert corners[-1] != corners[0]  # we *don't* want the loop closed
  fixed_corners = []
  for i in range(0, len(corners)):
    r1, c1 = corners[i-1]
    r2, c2 = corners[i]
    r3, c3 = corners[(i+1) % len(corners)]
    dr1, dc1 = sign(r2 - r1), sign(c2 - c1)
    dr2, dc2 = sign(r3 - r2), sign(c3 - c2)
    if dc1 > 0 or dc2 > 0:  # in or out rightward
      r2 += 1
    if dr1 < 0 or dr2 < 0:  # in or out upward
      c2 += 1
    fixed_corners.append((r2, c2))

  return fixed_corners


assertEqual([(0, 0), (2, 0), (2, 2), (0, 2)],
            fix_corners([(0, 0), (1, 0), (1, 1), (0, 1)]))
assertEqual([(1, 1), (1, 1), (1, 1), (1, 1)],
            fix_corners([(0, 0), (0, 1), (1, 1), (1, 0)]))


def day18(input, fix=False):
  instructions = parse_instructions(input)
  if fix:
    instructions = [fix_instruction(inst) for inst in instructions]

  corners = dig(instructions)
  if shoelace(corners) < 0:
    # ensure that polygon is positively oriented (counter-clockwise)
    corners = corners[::-1]

  return shoelace(fix_corners(corners))//2


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

# part2 complication
test_output = 952408144115


def fix_instruction(inst):
  return ('RDLU'[int(inst[2][-1])], int(inst[2][:-1], 16), None)


assertEqual(('R', 461937, None),
            fix_instruction((None, None, '70c710')))

assertEqual(test_output, day18(test_input, fix=True))

print('day18, part2 answer:')
submit(day18(open('day18_input.txt', 'r').read(), fix=True),
       expected=72811019847283)
print()
