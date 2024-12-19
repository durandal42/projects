from common import assertEqual
from common import submit

import collections


def parse_input(input):
  l1, l2 = [], []
  for row in input.splitlines():
    tokens = row.split()
    l1.append(int(tokens[0]))
    l2.append(int(tokens[1]))
  return l1, l2


def day01(input):
  l1, l2 = parse_input(input)
  return sum(abs(i1 - i2) for i1, i2 in zip(sorted(l1), sorted(l2)))


test_input = '''\
3   4
4   3
2   5
1   3
3   9
3   3
'''

assertEqual(parse_input(test_input), ([3, 4, 2, 1, 3, 3], [4, 3, 5, 3, 9, 3]))
test_output = 11

assertEqual(test_output, day01(test_input))


print('day01 answer:')
submit(day01(open('day01_input.txt', 'r').read()),
       expected=1320851)
print()


test_output = 31


def day01(input):
  l1, l2 = parse_input(input)
  l2_counts = collections.Counter(l2)
  return sum(i * l2_counts.get(i, 0) for i in l1)


assertEqual(test_output, day01(test_input))


print('day01, part2 answer:')
submit(day01(open('day01_input.txt', 'r').read()),
       expected=26859182)
print()
