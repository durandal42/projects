from common import assertEqual
from common import submit

import re
import itertools


def parse_input(input):
  return [parse_line(line) for line in input.splitlines()]


def parse_line(line):
  tokens = [int(t) for t in re.findall("\d+", line)]
  return (tokens[0], tokens[1:])


def can_produce(target, inputs, supported_ops):
  targets = set([target])
  while len(inputs) > 1:
    i = inputs.pop()
    new_targets = set()
    for t in targets:
      if "+" in supported_ops:
        nt = t - i
        if nt > 0:
          new_targets.add(nt)
      if "*" in supported_ops:
        if t % i == 0:
          new_targets.add(t // i)
      if "|" in supported_ops:
        si = str(i)
        st = str(t)
        split_left, split_right = st[:-len(si)], st[-len(si):]
        if split_right == si and len(split_left) > 0:
          new_targets.add(int(split_left))
    targets = new_targets
  return inputs[0] in targets


def day07(input, supported_ops="+*"):
  return sum(target
             for target, inputs in parse_input(input)
             if can_produce(target, inputs, supported_ops)
             )


test_input = '''\
190: 10 19
3267: 81 40 27
83: 17 5
156: 15 6
7290: 6 8 6 15
161011: 16 10 13
192: 17 8 14
21037: 9 7 18 13
292: 11 6 16 20
'''
test_output = 3749

assertEqual(test_output, day07(test_input))


print('day07 answer:')
submit(day07(open('day07_input.txt', 'r').read()),
       expected=1038838357795)
print()

# part 2 complication

test_output = 11387

assertEqual(test_output, day07(test_input, "*+|"))


print('day07, part 2 answer:')
submit(day07(open('day07_input.txt', 'r').read(), "*+|"),
       expected=254136560217241)
print()
