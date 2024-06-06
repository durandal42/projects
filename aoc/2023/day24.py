from common import assertEqual
from common import submit
import fractions


def parse_hailstone(line):
  return tuple(tuple(int(x) for x in token.split(', ')) for token in line.split(' @ '))


assertEqual(((1, 2, 3), (4, 5, 6)), parse_hailstone('1, 2, 3 @ 4, 5, 6'))


def cross_product_2d(xyz1, xyz2):
  return xyz1[0]*xyz2[1] - xyz1[1]*xyz2[0]


def cross_product(v1, v2):
  return (v1[1]*v2[2] - v1[2]*v2[1],
          v1[2]*v2[0] - v1[0]*v2[2],
          v1[0]*v2[1] - v1[1]*v2[0])


def dot_product(v1, v2):
  return sum(c1*c2 for c1, c2 in zip(v1, v2))


def tuple_add(v1, v2):
  return tuple(c1+c2 for c1, c2 in zip(v1, v2))


def tuple_sub(v1, v2):
  return tuple_add(v1, tuple_scale(v2, -1))


def tuple_scale(v, s):
  return tuple(c * s for c in v)


def tuple_div(v, s):
  return tuple(c // s for c in v)


def intersects_2d(h1, h2):
  p, r = h1
  q, s = h2
  rxs = cross_product_2d(r, s)
  qmp = tuple_sub(q, p)
  qmpxr = cross_product_2d(qmp, r)
  if rxs == 0 and qmpxr == 0:
    # colinear - this should never happen?
    assert False
  if rxs == 0 and qmpxr != 0:
    # parallel and non-intersecting
    return None, None

  # t = (q − p) × s / (r × s)
  t = fractions.Fraction(cross_product_2d(qmp, s), rxs)
  # u = (q − p) × r / (r × s)
  u = fractions.Fraction(cross_product_2d(qmp, r), rxs)

  return tuple_add(p, tuple_scale(r, t)), (t, u)


def intersects_future_target_area_2d(h1, h2, target_min, target_max):
  intersection, times = intersects_2d(h1, h2)
  if not intersection:
    return False
  if any(t <= 0 for t in times):
    return False
  if any(c < target_min or c > target_max for c in intersection[:2]):
    return False
  return True


def day24(input, target_min, target_max):
  hailstones = [parse_hailstone(line) for line in input.splitlines()]

  return sum(sum(1 for j, h2 in enumerate(hailstones) if i < j and
                 intersects_future_target_area_2d(h1, h2, target_min, target_max))
             for i, h1 in enumerate(hailstones))


test_input = '''\
19, 13, 30 @ -2,  1, -2
18, 19, 22 @ -1, -1, -2
20, 25, 34 @ -2, -2, -4
12, 31, 28 @ -1, -2, -1
20, 19, 15 @  1, -5, -3
'''
test_output = 2

assertEqual(test_output, day24(test_input, 7, 27))


print('day24 answer:')
submit(day24(open('day24_input.txt', 'r').read(),
             200000000000000,
             400000000000000),
       expected=21843)
print()

# part2 complication


def day24(input):
  h = [parse_hailstone(line) for line in input.splitlines()]

  # stones 0-2:
  position_0, position_1, position_2 = h[0][0], h[1][0], h[2][0]
  velocity_0, velocity_1, velocity_2 = h[0][1], h[1][1], h[2][1]

  # Stones 1 and 2, relative to stone 0:
  # p1 = position_1 - position_0
  # p2 = position_2 - position_0
  p1 = tuple_sub(position_1, position_0)
  p2 = tuple_sub(position_2, position_0)
  # v1 = velocity_1 - velocity_0
  # v2 = velocity_2 - velocity_0
  v1 = tuple_sub(velocity_1, velocity_0)
  v2 = tuple_sub(velocity_2, velocity_0)

  # t1 = -((p1 x p2) * v2) / ((v1 x p2) * v2)
  # t2 = -((p1 x p2) * v1) / ((p1 x v2) * v1)
  # assuming collisions happen at integer times!
  t1 = -dot_product(cross_product(p1, p2), v2) // dot_product(cross_product(v1, p2), v2)
  t2 = -dot_product(cross_product(p1, p2), v1) // dot_product(cross_product(p1, v2), v1)
  print('t1, t2 =', t1, t2)

  # c1 = position_1 + t1 * velocity_1
  # c2 = position_2 + t2 * velocity_2
  c1 = tuple_add(position_1, tuple_scale(velocity_1, t1))
  c2 = tuple_add(position_2, tuple_scale(velocity_2, t2))

  # v = (c2 - c1) / (t2 - t1)
  v = tuple_div(tuple_sub(c2, c1), t2-t1)

  # p = c1 - t1 * v
  p = tuple_sub(c1, tuple_scale(v, t1))

  return sum(p)


test_output = 47

assertEqual(test_output, day24(test_input))


print('day24, part2 answer:')
submit(day24(open('day24_input.txt', 'r').read()),
       expected=540355811503157)
print()
