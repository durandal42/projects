from common import assertEqual
from common import submit
import re
import collections
import math

test_input = '''\
broadcaster -> a, b, c
%a -> b
%b -> c
%c -> inv
&inv -> a
'''
test_pulses_sent = '''\
button -low-> broadcaster
broadcaster -low-> a
broadcaster -low-> b
broadcaster -low-> c
a -high-> b
b -high-> c
c -high-> inv
inv -low-> a
a -low-> b
b -low-> c
c -low-> inv
inv -high-> a
'''
test_output = 32000000

test_input2 = '''\
broadcaster -> a
%a -> inv, con
&inv -> b
%b -> con
&con -> output
'''
test_pulses_sent2 = '''\
button -low-> broadcaster
broadcaster -low-> a
a -high-> inv
a -high-> con
inv -low-> b
con -high-> output
b -high-> con
con -low-> output
'''
test_output2 = 11687500


def parse_input(input):
  return dict(parse_module(line) for line in input.splitlines())


def parse_module(line):
  m = re.match('([%&]?)(\\w+) -> ((\\w+, )*\\w+)', line)
  module_type = m.group(1)
  label = m.group(2)
  destinations = m.group(3).split(', ')
  return label, (module_type, destinations)


def init_conjunction_states(modules):
  conjunction_states = collections.defaultdict(lambda: collections.defaultdict(bool))
  for label, type_and_destinations in modules.items():
    t, ds = type_and_destinations
    for d in ds:
      if d in modules and modules[d][0] == '&':
        conjunction_states[d][label]
  return conjunction_states


def press_button(modules, flipflop_states=None, conjunction_states=None):
  if flipflop_states is None:
    flipflop_states = collections.defaultdict(bool)
  if conjunction_states is None:
    conjunction_states = init_conjunction_states(modules)

  pulse_q = collections.deque()
  pulse_q.append(('button', 'low', 'broadcaster'))
  pulses_sent = []
  while pulse_q:
    pulse = pulse_q.popleft()
    # print('handling pulse:', pulse)
    pulses_sent.append(pulse)
    source, height, label = pulse
    if label not in modules:
      continue
    module_type, destinations = modules[label]
    # print(module_type, destinations)
    if label == 'broadcaster':
      for d in destinations:
        pulse_q.append((label, height, d))
    elif module_type == '%':  # flip-flop
      if height == 'high':
        continue
      state = flipflop_states[label]
      send_height = 'low' if state else 'high'
      for d in destinations:
        pulse_q.append((label, send_height, d))
      flipflop_states[label] = not state
    elif module_type == '&':  # conjunction
      state = conjunction_states[label]
      state[source] = (height == 'high')
      send_height = 'low' if all(state.values()) else 'high'
      # print(state, send_height)
      for d in destinations:
        pulse_q.append((label, send_height, d))
    else:
      assert False
  return pulses_sent


assertEqual(
    test_pulses_sent.splitlines(),
    [f'{p[0]} -{p[1]}-> {p[2]}'
     for p in press_button(parse_input(test_input))])
assertEqual(
    test_pulses_sent2.splitlines(),
    [f'{p[0]} -{p[1]}-> {p[2]}'
     for p in press_button(parse_input(test_input2))])


def day20(input):
  modules = parse_input(input)
  # print(modules)

  flipflop_states = collections.defaultdict(bool)
  conjunction_states = init_conjunction_states(modules)

  pulses_sent = []
  for _ in range(1000):
    pulses_sent += press_button(modules, flipflop_states, conjunction_states)

  pulse_count_by_height = collections.Counter()
  for p in pulses_sent:
    pulse_count_by_height[p[1]] += 1
  # print(pulse_count_by_height)
  return math.prod(pulse_count_by_height.values())


assertEqual(test_output, day20(test_input))
assertEqual(test_output2, day20(test_input2))


print('day20 answer:')
submit(day20(open('day20_input.txt', 'r').read()),
       expected=730797576)
print()
