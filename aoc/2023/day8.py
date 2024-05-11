from common import assertEqual
from common import submit
import re


def day8(input):
  lines = input.splitlines()
  instructions = lines[0]
  _ = lines[1]
  nodes = {}
  for line in lines[2:]:
    k, v = parse_node(line)
    nodes[k] = v
  print(nodes)

  location = 'AAA'
  steps = 0
  while location != 'ZZZ':
    location = nodes[location][instructions[steps % len(instructions)]]
    steps += 1
  return steps


def parse_node(line):
  m = re.match('(\w+) = \((\w+), (\w+)\)', line)
  assert m
  label, left, right = m.group(1), m.group(2), m.group(3)
  print((label, {'L': left, 'R': right}))
  return (label, {'L': left, 'R': right})


test_input = '''RL

AAA = (BBB, CCC)
BBB = (DDD, EEE)
CCC = (ZZZ, GGG)
DDD = (DDD, DDD)
EEE = (EEE, EEE)
GGG = (GGG, GGG)
ZZZ = (ZZZ, ZZZ)
'''
test_output = 2

assertEqual(test_output, day8(test_input))


test_input = '''LLR

AAA = (BBB, BBB)
BBB = (AAA, ZZZ)
ZZZ = (ZZZ, ZZZ)
'''
test_output = 6

assertEqual(test_output, day8(test_input))


print('day8 answer:')
submit(day8(open('day8_input.txt', 'r').read()),
       expected=None)
print()
