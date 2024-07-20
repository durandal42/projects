from common import assertEqual
from common import submit
import math

test_input = '''\
Time:      7  15   30
Distance:  9  40  200'''
test_output = 288


def parse_input(input):
  lines = input.splitlines()
  times = [int(t) for t in lines[0].split(':')[1].split()]
  distances = [int(d) for d in lines[1].split(':')[1].split()]
  return list(zip(times, distances))


assertEqual([(7, 9), (15, 40), (30, 200)], parse_input(test_input))


def ways_to_win(time, distance):
  # solve: t * (time - t) > distance
  # -t**2 + time*t - distance > 0
  # -t**2 + time*t - distance - 1 = 0 (and then round appropriately)
  a = -1
  b = time
  c = -distance - 1
  discrim = b**2 - 4 * a * c
  sqrt_discrim = math.sqrt(discrim)
  s1 = (-b + sqrt_discrim) / (2 * a)
  s2 = (-b - sqrt_discrim) / (2 * a)
  # print(s1, s2)
  return math.floor(s2) - math.ceil(s1) + 1


assertEqual(4, ways_to_win(7, 9))
assertEqual(8, ways_to_win(15, 40))
assertEqual(9, ways_to_win(30, 200))


def day06(input):
  races = parse_input(input)
  result = 1
  for time, distance in races:
    result *= ways_to_win(time, distance)
  return result


assertEqual(test_output, day06(test_input))


print('day06 answer:')
submit(day06(open('day06_input.txt', 'r').read()),
       expected=449550)
print()

# part 2 complication
test_output = 71503


def parse_input(input):
  lines = input.splitlines()
  times = [int(''.join(lines[0].split(':')[1].split()))]
  distances = [int(''.join(lines[1].split(':')[1].split()))]
  return list(zip(times, distances))


assertEqual(test_output, day06(test_input))

print('day06 part2 answer:')
submit(day06(open('day06_input.txt', 'r').read()),
       expected=28360140)
print()
