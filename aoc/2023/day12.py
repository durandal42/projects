from common import assertEqual
from common import submit
import functools


def day12(input, blowup=1):
  return sum(possible_arrangements(line, blowup)
             for line in input.splitlines())


def possible_arrangements(line, blowup=1):
  # print(line)
  tokens = line.split()
  conditions = '?'.join([tokens[0]] * blowup)
  runs = [int(t) for t in tokens[1].split(',')] * blowup
  # print(conditions, runs)

  return possible_arrangements_recursive(conditions, tuple(runs), 0)


@functools.cache
def possible_arrangements_recursive(conditions, runs, leading_broken=0):
  if not runs:
    if leading_broken == 0 and '#' not in conditions:
      # print('out of runs, no unaccounted-for broken parts')
      return 1
    else:
      # print('out of runs, but some unaccounted-for broken parts')
      return 0
  if not conditions:
    if (leading_broken == 0 and not runs) or runs == (leading_broken,):
      # print('out of conditions, final run satisfied')
      return 1
    else:
      # print('out of conditions, final run not satisfied')
      return 0
  if sum(runs) > (conditions.count('?') +
                  conditions.count('#') +
                  leading_broken):
    # print('remaining runs unsatisfiable - not enough places to put broken parts')
    return 0
  if sum(runs) + len(runs) - 1 > len(conditions) + leading_broken:
    # print('remaining runs unsatisfiable - not enough space left')
    return 0

  result = 0
  if conditions[0] in '.?':
    # treat as '.'
    if leading_broken == 0:
      result += possible_arrangements_recursive(conditions[1:], runs, 0)
    elif leading_broken == runs[0]:
      result += possible_arrangements_recursive(conditions[1:], runs[1:], 0)
  if conditions[0] in '#?' and leading_broken < runs[0]:
    # treat as '#
    result += possible_arrangements_recursive(
        conditions[1:], runs, leading_broken + 1)
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

# part2 complication
test_output = 525152

assertEqual(1, possible_arrangements("???.### 1,1,3", 5))
assertEqual(16384, possible_arrangements(".??..??...?##. 1,1,3", 5))
assertEqual(1, possible_arrangements("?#?#?#?#?#?#?#? 1,3,1,6", 5))
assertEqual(16, possible_arrangements("????.#...#... 4,1,1", 5))
assertEqual(2500, possible_arrangements("????.######..#####. 1,6,5", 5))
assertEqual(506250, possible_arrangements("?###???????? 3,2,1", 5))
assertEqual(test_output, day12(test_input, 5))

print('day12, part2 answer:')
submit(day12(open('day12_input.txt', 'r').read(), blowup=5),
       expected=4964259839627)
print()
