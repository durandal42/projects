from common import assertEqual
from common import submit


def day15(input):
  return sum(hash(s) for s in input.strip().split(','))


def hash(s):
  h = 0
  for c in s:
    h += ord(c)
    h *= 17
    h = h % 256
  return h


test_input = 'rn=1,cm-,qp=3,cm=2,qp-,pc=4,ot=9,ab=5,pc-,pc=6,ot=7'
test_output = 1320

assertEqual(test_output, day15(test_input))


print('day15 answer:')
submit(day15(open('day15_input.txt', 'r').read()),
       expected=None)
print()
