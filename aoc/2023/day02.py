from common import assertEqual
from common import submit
import collections
import functools
import operator


def parse_reveal(reveal_str):
  result = collections.Counter()
  for counted_color_str in reveal_str.split(', '):
    tokens = counted_color_str.split(' ')
    assertEqual(len(tokens), 2)
    count, color = int(tokens[0]), tokens[1]
    result[color] = count
  return result


assertEqual(
    {'blue': 3, 'red': 4},
    parse_reveal("3 blue, 4 red")
)


def parse_reveals(reveals_str):
  return [parse_reveal(r) for r in reveals_str.split('; ')]


assertEqual(
    [
        parse_reveal("3 blue, 4 red"),
        parse_reveal("1 red, 2 green, 6 blue"),
        parse_reveal("2 green"),
    ],
    parse_reveals("3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green")
)


def parse_game(game_str):
  tokens = game_str.split()
  assertEqual(len(tokens), 2)
  assertEqual(tokens[0], 'Game')
  return int(tokens[1])


assertEqual(1, parse_game('Game 1'))


def parse_line(line):
  tokens = line.split(': ')
  assertEqual(len(tokens), 2)
  return int(parse_game(tokens[0])), parse_reveals(tokens[1])


assertEqual(
    (parse_game("Game 1"),
     parse_reveals("3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green")),
    parse_line("Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green")
)


def max_counters(counters):
  return functools.reduce(operator.or_, counters)


assertEqual(
    {'a': 2, 'b': 2, 'c': 3},
    max_counters([collections.Counter({'a': 1, 'b': 2}),
                  collections.Counter({'a': 2, 'b': 1, 'c': 3})]),

)


def day02(input, threshold):
  result = 0
  # print(f'threshold: {threshold}')
  for line in input.splitlines():
    i, balls_shown = parse_line(line)
    max_balls = max_counters(balls_shown)

    if max_balls <= threshold:
      result += i
  return result


test_input = '''Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green
Game 2: 1 blue, 2 green; 3 green, 4 blue, 1 red; 1 green, 1 blue
Game 3: 8 green, 6 blue, 20 red; 5 blue, 4 red, 13 green; 5 green, 1 red
Game 4: 1 green, 3 red, 6 blue; 3 green, 6 red; 3 green, 15 blue, 14 red
Game 5: 6 red, 1 blue, 3 green; 2 blue, 1 red, 2 green
'''
test_output = 8

assertEqual(test_output,
            day02(test_input, parse_reveal('12 red, 13 green, 14 blue')))


print('day02 answer:')
submit(day02(open('day02_input.txt', 'r').read(),
             parse_reveal('12 red, 13 green, 14 blue')),
       expected=2369)
print()


# part 2 complication:
test_output = 2286


def day02(input):
  result = 0
  for line in input.splitlines():
    i, balls_shown = parse_line(line)
    max_balls = max_counters(balls_shown)

    power = max_balls['red'] * max_balls['green'] * max_balls['blue']

    result += power
  return result


assertEqual(test_output, day02(test_input))

print('day02 part2 answer:')
submit(day02(open('day02_input.txt', 'r').read()),
       expected=66363)
print()
