from common import assertEqual
from common import submit

test_input = '''Time:      7  15   30
Distance:  9  40  200'''
test_output = 288


def parse_input(input):
  lines = input.splitlines()
  times = [int(t) for t in lines[0].split(':')[1].split()]
  distances = [int(d) for d in lines[1].split(':')[1].split()]
  return list(zip(times, distances))

assertEqual([(7, 9), (15, 40), (30, 200)], parse_input(test_input))


def ways_to_win(time, distance):
  # TODO(durandal): quadratic formula, if this is too slow.
  result = 0
  for t in range(0, time + 1):
    if t * (time - t) > distance:
      # print(f'wait {t}, travel {time - t}, total distance {t * (time - t)}')
      result += 1
  return result

assertEqual(4, ways_to_win(7, 9))
assertEqual(8, ways_to_win(15, 40))
assertEqual(9, ways_to_win(30, 200))


def day6(input):
  races = parse_input(input)
  result = 1
  for time, distance in races:
    result *= ways_to_win(time, distance)
  return result


assertEqual(test_output, day6(test_input))


print('day6 answer:')
submit(day6(open('day6_input.txt', 'r').read()),
       expected=449550)
print()

# part 2 complication
test_output = 71503


def parse_input(input):
  lines = input.splitlines()
  times = [int(''.join(lines[0].split(':')[1].split()))]
  distances = [int(''.join(lines[1].split(':')[1].split()))]
  return list(zip(times, distances))


assertEqual(test_output, day6(test_input))

print('day6 part2 answer:')
submit(day6(open('day6_input.txt', 'r').read()),
       expected=28360140)
print()
