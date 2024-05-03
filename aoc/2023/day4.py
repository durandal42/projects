from common import assertEqual
from common import submit


def match_score(num_matches):
  if not num_matches:
    return 0
  return 2**(num_matches - 1)


def card_score(line):
  # print(line)
  tokens = line.split(': ')
  assertEqual(2, len(tokens))
  label, numbers = tokens[0], tokens[1]
  tokens = numbers.split(' | ')
  assertEqual(2, len(tokens))
  have, winners = tokens[0], tokens[1]
  have = set(int(n) for n in have.split())
  winners = set(int(n) for n in winners.split())
  return match_score(sum(1 for n in have if n in winners))


def day4(input):
  return sum(card_score(line) for line in input.splitlines())


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
       expected=None)
print()
