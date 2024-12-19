from common import assertEqual
from common import submit

import re


def day03(input):
  return sum(int(m.group(1)) * int(m.group(2))
             for m in re.finditer("mul\((\d+),(\d+)\)", input))


test_input = '''\
xmul(2,4)%&mul[3,7]!@^do_not_mul(5,5)+mul(32,64]then(mul(11,8)mul(8,5))
'''
test_output = 161

assertEqual(test_output, day03(test_input))


print('day03 answer:')
submit(day03(open('day03_input.txt', 'r').read()),
       expected=170778545)
print()

# Part 2 complication
test_input = '''\
xmul(2,4)&mul[3,7]!^don't()_mul(5,5)+mul(32,64](mul(11,8)undo()?mul(8,5))
'''
test_output = 48


def day03(input):
  result = 0
  do = True
  for m in re.finditer("(mul)\((\d+),(\d+)\)|(do)\(\)|(don't)\(\)", input):
    if m.group(1) == "mul" and do:
      result += int(m.group(2)) * int(m.group(3))
    elif m.group(4) == "do":
      do = True
    elif m.group(5) == "don't":
      do = False
  return result


assertEqual(test_output, day03(test_input))


print('day03 answer:')
submit(day03(open('day03_input.txt', 'r').read()),
       expected=82868252)
print()
