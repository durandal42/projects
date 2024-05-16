from common import assertEqual
from common import submit
import itertools


def day12(input):
  return sum(possible_arrangements(line) for line in input.splitlines())


def possible_arrangements(line):
  tokens = line.split()
  conditions = list(tokens[0])
  runs = [int(t) for t in tokens[1].split(',')]

  result = 0
  num_unknowns = sum(1 for c in conditions if c == '?')
  # print(f'checking 2**{num_unknowns} possibilities')
  for values_for_unknowns in itertools.product('.#', repeat=num_unknowns):
    arrangement = conditions[:]
    j = 0
    for i, c in enumerate(arrangement):
      if c == '?':
        arrangement[i] = values_for_unknowns[j]
        j += 1
    if valid_arrangement(arrangement, runs):
      result += 1
  return result


def valid_arrangement(arrangement, runs):
  return compute_runs(arrangement) == runs


def compute_runs(arrangement):
  result = []
  current_run = 0
  for c in arrangement:
    if c == '#':
      current_run += 1
    else:
      if current_run > 0:
        result.append(current_run)
        current_run = 0
  if current_run > 0:
    result.append(current_run)
    current_run = 0
  return result


test_input = '''???.### 1,1,3
.??..??...?##. 1,1,3
?#?#?#?#?#?#?#? 1,3,1,6
????.#...#... 4,1,1
????.######..#####. 1,6,5
?###???????? 3,2,1
'''
test_output = 21

assertEqual(1, possible_arrangements("???.### 1,1,3"))
assertEqual(4, possible_arrangements(".??..??...?##. 1,1,3"))
assertEqual(1, possible_arrangements("?#?#?#?#?#?#?#? 1,3,1,6"))
assertEqual(1, possible_arrangements("????.#...#... 4,1,1"))
assertEqual(4, possible_arrangements("????.######..#####. 1,6,5"))
assertEqual(10, possible_arrangements("?###???????? 3,2,1"))
assertEqual(test_output, day12(test_input))


print('day12 answer:')
submit(day12(open('day12_input.txt', 'r').read()),
       expected=7622)
print()
