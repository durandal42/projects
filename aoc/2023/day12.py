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

print('day12, showboating:')
import sys  # nopep8
sys.setrecursionlimit(10000)
submit(day12(open('day12_input.txt', 'r').read(), blowup=25),
       expected=716810895108049883391643471219064205525760353694142812814055463934)
submit(day12(open('day12_input.txt', 'r').read(), blowup=30),
       expected=17431308163207960040598974623809088157278806730535723130332423885935031056107200)
submit(day12(open('day12_input.txt', 'r').read(), blowup=35),
       expected=429906089352210480545466380532048837182627754542295370759083512303006035657580369685465852795)
submit(day12(open('day12_input.txt', 'r').read(), blowup=40),
       expected=10712325155868918675748263675231720231990128990680463102327501351223804870707997631587844335379228025548046)
submit(day12(open('day12_input.txt', 'r').read(), blowup=45),
       expected=269032310678736665226371658438567233447376439418248332624970951171959214229939604665897432578611923065868185742400079321)
submit(day12(open('day12_input.txt', 'r').read(), blowup=50),
       expected=6798544204571224941038314524100909249622733430313584935688712798224309986705550261697353106747732123775089399664581723186536009722602)
print()
