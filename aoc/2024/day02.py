from common import assertEqual
from common import submit


def parse_input(input):
  return [[int(t) for t in line.split()] for line in input.splitlines()]


def is_safe(report):
  direction = 0
  for l1, l2 in zip(report[:-1], report[1:]):
    d = l2 - l1
    if abs(d) < 1:
      return False
    if abs(d) > 3:
      return False
    if (d < 0 and direction > 0 or
            d > 0 and direction < 0):
      return False
    direction = d
  return True


def day02(input):
  return sum(1 for report in parse_input(input) if is_safe(report))


test_input = '''\
7 6 4 2 1
1 2 7 8 9
9 7 6 2 1
1 3 2 4 5
8 6 4 4 1
1 3 6 7 9
'''
test_output = 2

assertEqual(parse_input(test_input), [
    [7, 6, 4, 2, 1],
    [1, 2, 7, 8, 9],
    [9, 7, 6, 2, 1],
    [1, 3, 2, 4, 5],
    [8, 6, 4, 4, 1],
    [1, 3, 6, 7, 9],
])

assertEqual(test_output, day02(test_input))


print('day02 answer:')
submit(day02(open('day02_input.txt', 'r').read()),
       expected=442)
print()


# Part 2 complication:

test_output = 4


def is_safe_dampened(report):
  return is_safe(report) or any(is_safe(report[:i]+report[i+1:]) for i in range(len(report)))


def day02(input):
  return sum(1 for report in parse_input(input) if is_safe_dampened(report))


assertEqual(test_output, day02(test_input))


print('day02, part 2 answer:')
submit(day02(open('day02_input.txt', 'r').read()),
       expected=493)
print()
