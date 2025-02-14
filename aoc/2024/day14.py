from common import assertEqual
from common import submit
from common import sign
import re
import collections
import math
import time


def parse_input(input):
  return [((int(x), int(y)), (int(dx), int(dy)))
          for x, y, dx, dy in
          re.findall("p=(-?\\d+),(-?\\d+) v=(-?\\d+),(-?\\d+)", input)]


def extrapolate(pos, v, steps, limit):
  x, y = pos
  dx, dy = v
  limit_x, limit_y = limit
  x += dx * steps
  y += dy * steps
  x %= limit_x
  y %= limit_y
  return (x, y)


assertEqual((1, 3), extrapolate((2, 4), (2, -3), 5, (11, 7)))


def day14(input, limit=(101, 103), steps=100):
  robots = parse_input(input)
  # print(robots)

  final_positions = [extrapolate(pos, v, steps, limit) for pos, v in robots]
  final_positions_hypothetical = [extrapolate(pos, v, steps + math.lcm(limit[0], limit[1]), limit) for pos, v in robots]
  assertEqual(final_positions, final_positions_hypothetical)

  # print(final_positions)

  quadrants = collections.Counter()
  for x, y in final_positions:
    qx = sign(x - limit[0] // 2)
    qy = sign(y - limit[1] // 2)
    if not qx or not qy:
      continue
    quadrants[(qx, qy)] += 1
  # print(quadrants)

  return math.prod(quadrants.values())


test_input = '''\
p=0,4 v=3,-3
p=6,3 v=-1,-3
p=10,3 v=-1,2
p=2,0 v=2,-1
p=0,0 v=1,3
p=3,0 v=-2,-2
p=7,6 v=-1,-3
p=3,0 v=-1,-2
p=9,3 v=2,3
p=7,3 v=-1,2
p=2,4 v=2,-3
p=9,5 v=-3,-3
'''
test_output = 12

assertEqual(test_output, day14(test_input, (11, 7), 100))


print('day14 answer:')
submit(day14(open('day14_input.txt', 'r').read()),
       expected=230435667)
print()

# part 2 complications


def render(positions, limit):
  limit_x, limit_y = limit
  positions = set(positions)
  print("\n".join("".join((x, y) in positions and "X" or " "
                          for x in range(limit_x))
                  for y in range(limit_y)))


def day14(input, limit=(101, 103)):
  robots = parse_input(input)

  for steps in range(math.prod(limit)):
    final_positions = [extrapolate(pos, v, steps, limit) for pos, v in robots]
    if steps % 101 != 33:
      # visually detected significant vertical alignment at step 33
      continue
    print("steps:", steps)
    render(final_positions, limit)
    time.sleep(1)
    # return steps


print('day14 answer:')
submit(day14(open('day14_input.txt', 'r').read()),
       expected=7709)
print()
