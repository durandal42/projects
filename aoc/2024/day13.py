from common import assertEqual
from common import submit
from common import sign
import re
import math
import numpy


def parse_input(input):
  return [((int(ax), int(ay)), (int(bx), int(by)), (int(px), int(py)))
          for ax, ay, bx, by, px, py in re.findall('''\
Button A: X\\+(\\d+), Y\\+(\\d+)
Button B: X\\+(\\d+), Y\\+(\\d+)
Prize: X=(\\d+), Y=(\\d+)\
''', input)]


def cost_to_win(machine, prize_offset):
  a, b, p = machine
  ax, ay = a
  bx, by = b
  px, py = p[0] + prize_offset, p[1] + prize_offset

  # solve:
  # a*ax + b*bx = px
  # a*ay + b*by = py
  lhs = numpy.array([[ax, bx], [ay, by]])
  rhs = numpy.array([px, py])
  soln = numpy.linalg.solve(lhs, rhs)
  print(soln)
  a, b = soln[0], soln[1]
  print(a, b)
  a, b = round(a), round(b)

  print(a*ax + b*bx, "==", px)
  print(a*ay + b*by, "==", py)
  if (a*ax + b*bx != px) or (a*ay + b*by != py):
    print("non-integer solution")
    return 0

  cost = 3*a + b
  print(f"press a {a} times, b {b} times, costing {cost} tokens")
  return cost


def day13(input, prize_offset=0):
  machines = parse_input(input)
  return sum(cost_to_win(m, prize_offset) for m in machines)


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

print('day13, part 2 answer:')
submit(day13(open('day13_input.txt', 'r').read(), 10000000000000),
       expected=104140871044942)
print()
