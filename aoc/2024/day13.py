from common import assertEqual
from common import submit
import re


def parse_input(input):
  return [((int(ax), int(ay)), (int(bx), int(by)), (int(px), int(py)))
          for ax, ay, bx, by, px, py in re.findall('''\
Button A: X\+(\d+), Y\+(\d+)
Button B: X\+(\d+), Y\+(\d+)
Prize: X=(\d+), Y=(\d+)\
''', input)]


def cost_to_win(machine):
  print(machine)
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
  print(solutions)
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
