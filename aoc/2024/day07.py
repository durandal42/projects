from common import assertEqual
from common import submit

import re
import itertools


def parse_input(input):
  return [parse_line(line) for line in input.splitlines()]


def parse_line(line):
  tokens = [int(t) for t in re.findall("\d+", line)]
  return (tokens[0], tokens[1:])


def can_produce(target, inputs):
  for operators in itertools.product("*+", repeat=len(inputs)-1):
    result = inputs[0]
    for op, value in zip(operators, inputs[1:]):
      if op == "+":
        result += value
      if op == "*":
        result *= value
    if result == target:
      return True
  return False


def day07(input):
  return sum(target
             for target, inputs in parse_input(input)
             if can_produce(target, inputs)
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
