from common import assertEqual
from common import submit
from common import sign
import re
import math


def parse_input(input):
  return [((int(ax), int(ay)), (int(bx), int(by)), (int(px), int(py)))
          for ax, ay, bx, by, px, py in re.findall('''\
Button A: X\+(\d+), Y\+(\d+)
Button B: X\+(\d+), Y\+(\d+)
Prize: X=(\d+), Y=(\d+)\
''', input)]


def cost_to_win(machine):
  a, b, p = machine
  ax, ay = a
  bx, by = b
  px, py = p

  # brute force:
  solutions = []
  for a in range(100 + 1):
    for b in range(100 + 1):
      if (a*ax + b*bx == px and a*ay + b*by == py):
        solutions.append(3*a + b)

  if not solutions:
    return 0
  return min(solutions)


def day13(input):
  machines = parse_input(input)
  return sum(cost_to_win(m) for m in machines)


test_input = '''\
Button A: X+94, Y+34
Button B: X+22, Y+67
Prize: X=8400, Y=5400

Button A: X+26, Y+66
Button B: X+67, Y+21
Prize: X=12748, Y=12176

Button A: X+17, Y+86
Button B: X+84, Y+37
Prize: X=7870, Y=6450

Button A: X+69, Y+23
Button B: X+27, Y+71
Prize: X=18641, Y=10279
'''
test_output = 480

assertEqual(test_output, day13(test_input))


print('day13 answer:')
submit(day13(open('day13_input.txt', 'r').read()),
       expected=29201)
print()

# part 2 complication


def cost_to_win(machine):
  print()
  print("a, b, p:", machine)
  a, b, p = machine
  ax, ay = a
  bx, by = b
  px, py = p[0] + 10000000000000, p[1] + 10000000000000

  dxy_a = ax - ay
  dxy_b = bx - by
  dxy_p = px - py

  print("dxy_a, dxy_b, dxy_p:", dxy_a, dxy_b, dxy_p)
  if sign(dxy_a) != -sign(dxy_b):
    print("dxy_a and db don't have opposed signs; unlikely to work")
    return 0

  gcd = math.gcd(dxy_a, dxy_b)
  if dxy_p % gcd != 0:
    print("gcd(dxy_a, dxy_b) doesn't divide dxy_p; no solution possible")

  # TODO: press a and b enough to satisfy dp
  dxy = 0
  a, b = 0, 0
  while dxy != dxy_p:
    if (dxy < dxy_p and dxy_a > 0) or (dxy > dxy_p and dxy_a < 0):
      a += 1
      dxy += dxy_a
    if (dxy < dxy_p and dxy_b > 0) or (dxy > dxy_p and dxy_b < 0):
      b += 1
      dxy += dxy_b
  print("to satisfy dxy_p -> a,b:", a, b)

  da = abs(dxy_b // gcd)
  db = abs(dxy_a // gcd)
  assert math.gcd(da, db) == 1
  dx = da*ax + db*bx
  dy = da*ay + db*by
  print("to increase x,y without changing (x-y) -> da,db:", da, db)

  remain_x = (px - (a * ax) - (b * bx))
  remain_y = (py - (a * ay) - (b * by))
  if (remain_x % dx != 0) or (remain_y % dy != 0):
    print("non-integer solution")
    return 0
  i1 = remain_x // dx
  i2 = remain_y // dy
  print(f"do that {i1} times to reach px")
  print(f"do that {i2} times to reach py")
  if i1 != i2:
    print("no solution")
    return 0

  a += i1 * da
  b += i1 * db

  print(a*ax + b*bx, "==", px)
  print(a*ay + b*by, "==", py)
  assert a*ax + b*bx == px
  assert a*ay + b*by == py

  cost = 3*a + b
  print(f"press a {a} times, b {b} times, costing {cost} tokens")
  return cost


print('day13, part 2 answer:')
submit(day13(open('day13_input.txt', 'r').read()),
       expected=104140871044942)
print()
