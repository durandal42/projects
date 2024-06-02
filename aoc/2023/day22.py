from common import assertEqual
from common import submit
import collections


def parse_brick(line):
  return tuple(sorted(list(int(t) for t in end.split(',')) for end in line.split('~')))


assertEqual(([1, 0, 1], [1, 2, 1]), parse_brick("1,0,1~1,2,1"))


def grounded(brick):
  # lhs is lower (because sorted), and bricks are "a single straight line of cubes"
  return brick[0][2] == 1


def is_vertical(brick):
  return brick[0][0] == brick[1][0] and brick[0][1] == brick[1][1]


def intersects(b1xy1, b1xy2, b2xy1, b2xy2):
  return not (b1xy1[0] > b2xy2[0] or b1xy1[1] > b2xy2[1] or
              b1xy2[0] < b2xy1[0] or b1xy2[1] < b2xy1[1])


def does_support(b1, b2):
  if b2[0][2] != b1[1][2] + 1:
    # b2's lowest point must be 1 higher than b1's highest
    return False
  return intersects(b1[0][:2], b1[1][:2], b2[0][:2], b2[1][:2])


def fall(brick):
  brick[0][2] -= 1
  brick[1][2] -= 1


def can_fall(b1, bricks):
  if grounded(b1):
    return False
  for b2 in bricks:
    if does_support(b2, b1):
      return False
  return True


def collapse(bricks):
  print(f'playing with {len(bricks)} bricks')
  progress = True
  while progress:
    progress = False
    for b in bricks:
      while can_fall(b, bricks):
        fall(b)
        progress = True
  print("bricks are done falling")


def supported_by(bricks):
  result = collections.defaultdict(list)
  for i, b1 in enumerate(bricks):
    if grounded(b1):
      result[i].append('G')
      continue
    for j, b2 in enumerate(bricks):
      if does_support(b2, b1):
        result[i].append(j)
  return result


def sole_supports(supported_by_map):
  result = set()
  for above, below in supported_by_map.items():
    if len(below) == 1:
      result.add(below[0])
  return result


def day22(input):
  bricks = [parse_brick(line) for line in input.splitlines()]
  collapse(bricks)

  return len(bricks) - len(sole_supports(supported_by(bricks))) + 1


test_input = '''\
1,0,1~1,2,1
0,0,2~2,0,2
0,2,3~2,2,3
0,0,4~0,2,4
2,0,5~2,2,5
0,1,6~2,1,6
1,1,8~1,1,9
'''
test_output = 5

assertEqual(test_output, day22(test_input))


print('day22 answer:')
submit(day22(open('day22_input.txt', 'r').read()),
       expected=386)
print()
