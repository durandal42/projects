from common import assertEqual
from common import submit
import collections


def match_score(num_matches):
  if not num_matches:
    return 0
  return 2**(num_matches - 1)

assertEqual(0, match_score(0))
assertEqual(1, match_score(1))
assertEqual(2, match_score(2))
assertEqual(8, match_score(4))


def num_matches(line):
  tokens = line.split(': ')
  assertEqual(2, len(tokens))
  label, numbers = tokens[0], tokens[1]
  tokens = numbers.split(' | ')
  assertEqual(2, len(tokens))
  have = set(int(n) for n in tokens[0].split())
  winners = set(int(n) for n in tokens[1].split())
  return len(have.intersection(winners))

assertEqual(4, num_matches('Card 1: 41 48 83 86 17 | 83 86  6 31 17  9 48 53'))


def day4(input):
  return sum(match_score(num_matches(line)) for line in input.splitlines())


test_input = '''Card 1: 41 48 83 86 17 | 83 86  6 31 17  9 48 53
Card 2: 13 32 20 16 61 | 61 30 68 82 17 32 24 19
Card 3:  1 21 53 59 44 | 69 82 63 72 16 21 14  1
Card 4: 41 92 73 84 69 | 59 84 76 51 58  5 54 83
Card 5: 87 83 26 28 32 | 88 30 70 12 93 22 82 36
Card 6: 31 18 13 56 72 | 74 77 10 23 35 67 36 11
'''
test_output = 13

assertEqual(test_output, day4(test_input))


print('day4 answer:')
submit(day4(open('day4_input.txt', 'r').read()),
       expected=23678)
print()

# part2 complication
test_output = 30


def day4(input):
  cards = collections.defaultdict(int)
  for i, line in enumerate(input.splitlines()):
    cards[i] += 1
    nm = num_matches(line)
    for j in range(nm):
      cards[i + j + 1] += cards[i]
  return sum(cards.values())

assertEqual(test_output, day4(test_input))

print('day4 part2 answer:')
submit(day4(open('day4_input.txt', 'r').read()),
       expected=15455663)
print()
