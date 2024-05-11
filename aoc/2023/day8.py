from common import assertEqual
from common import submit
import re
import math


def day8(input):
  instructions, nodes = parse_input(input)
  return follow_instructions('AAA', lambda l: l == 'ZZZ', nodes, instructions)


def parse_input(input):
  lines = input.splitlines()
  instructions = lines[0]
  assert not lines[1]
  nodes = dict([parse_node(line) for line in lines[2:]])
  return instructions, nodes


def follow_instructions(label, dst_criteria, nodes, instructions):
  steps = 0
  while not dst_criteria(label):
    label = nodes[label][instructions[steps % len(instructions)]]
    steps += 1
  return steps


def parse_node(line):
  m = re.match('(\\w+) = \\((\\w+), (\\w+)\\)', line)
  label, left, right = m.group(1), m.group(2), m.group(3)
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
       expected=12169)
print()

# part 2 complication
test_input = '''LR

11A = (11B, XXX)
11B = (XXX, 11Z)
11Z = (11B, XXX)
22A = (22B, XXX)
22B = (22C, 22C)
22C = (22Z, 22Z)
22Z = (22B, 22B)
XXX = (XXX, XXX)
'''
test_output = 6


def day8(input):
  instructions, nodes = parse_input(input)
  srcs = filter(lambda l: l.endswith('A'), nodes.keys())

  steps = [follow_instructions(src, lambda l: l.endswith('Z'),
                               nodes, instructions) for src in srcs]
  print(steps)
  return math.lcm(*steps)

assertEqual(test_output, day8(test_input))

print('day8, part2 answer:')
submit(day8(open('day8_input.txt', 'r').read()),
       expected=12030780859469)
print()
