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
