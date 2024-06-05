from common import assertEqual
from common import submit
import fractions


def parse_hailstone(line):
  return tuple(tuple(int(x) for x in token.split(', ')) for token in line.split(' @ '))


assertEqual(((1, 2, 3), (4, 5, 6)), parse_hailstone('1, 2, 3 @ 4, 5, 6'))


def cross_product_2d(xyz1, xyz2):
  return xyz1[0]*xyz2[1] - xyz1[1]*xyz2[0]


def tuple_add(v1, v2):
  return tuple(c1+c2 for c1, c2 in zip(v1, v2))


def tuple_scale(v, s):
  return tuple(c * s for c in v)


def intersects_2d(h1, h2):
  p, r = h1
  q, s = h2
  rxs = cross_product_2d(r, s)
  qmp = tuple_add(q, tuple_scale(p, -1))
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

  return tuple_add(p, tuple_scale(r, t))[:2], (t, u)


def intersects_future_target_area_2d(h1, h2, target_min, target_max):
  intersection, times = intersects_2d(h1, h2)
  if not intersection:
    return False
  if any(t <= 0 for t in times):
    return False
  if any(c < target_min or c > target_max for c in intersection):
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
