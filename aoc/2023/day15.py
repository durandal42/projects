from common import assertEqual
from common import submit
import re
import collections


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
       expected=511498)
print()


# part2 complication
test_output = 145


def parse_step(step):
  m = re.match('(\\w+)([-=])(\\d?)', step)
  return (m.group(1), m.group(2), int(m.group(3)) if m.group(3) else None)


assertEqual(('rn', '=', 1), parse_step('rn=1'))
assertEqual(('cm', '-', None), parse_step('cm-'))


def parse_steps(input):
  return [parse_step(step) for step in input.strip().split(',')]


def day15(input):
  return score_buckets(fill_buckets(parse_steps(input)))


def fill_buckets(steps):
  buckets = [collections.defaultdict(collections.OrderedDict) for _ in range(256)]
  for label, op, length in steps:
    h = hash(label)
    if op == '-':
      if label in buckets[h]:
        del buckets[h][label]
    elif op == '=':
      buckets[h][label] = length
  return buckets


def score_bucket(i, b):
  return sum((i+1) * (j+1) * kv[1] for j, kv in enumerate(b.items()))


assertEqual(1+4, score_bucket(0, collections.OrderedDict([('rn', 1), ('cm', 2)])))


def score_buckets(buckets):
  return sum(score_bucket(i, b) for i, b in enumerate(buckets))


assertEqual(test_output, day15(test_input))


print('day15, part2 answer:')
submit(day15(open('day15_input.txt', 'r').read()),
       expected=284674)
print()
