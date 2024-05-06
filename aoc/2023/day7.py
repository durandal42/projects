from common import assertEqual
from common import submit
import collections


def rank_card(c):
  # TODO(durandal): map lookup if this bottlenecks
  return -['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2'].index(c)


def tiebreaker(hand):
  return tuple(rank_card(c) for c in hand)


def rank_hand(hand):
  return tuple(sorted(collections.Counter(hand).values(), reverse=True))

assertEqual((1, 1, 1, 1, 1), rank_hand('23456'))
assertEqual((2, 1, 1, 1), rank_hand('32T3K'))
assertEqual((2, 2, 1), rank_hand('KTJJT'))
assertEqual((2, 2, 1), rank_hand('KK677'))
assertEqual((3, 1, 1), rank_hand('T55J5'))
assertEqual((3, 1, 1), rank_hand('QQQJA'))


def score_and_rank_hands(hands_and_bids):
  hands = []
  for hand, bid in hands_and_bids:
    hands.append((rank_hand(hand), tiebreaker(hand), bid, hand))
  hands.sort()
  return hands


def parse_input(input):
  hands_and_bids = []
  for line in input.splitlines():
    tokens = line.split()
    assertEqual(2, len(tokens))
    hand, bid = tokens[0], int(tokens[1])
    hands_and_bids.append((hand, bid))
  return hands_and_bids


def day7(input):
  result = 0
  for i, score_and_bid in enumerate(score_and_rank_hands(parse_input(input))):
    bid = score_and_bid[2]
    # print(i + 1, score_and_bid, "->", (i + 1) * bid)
    result += (i + 1) * bid
  return result

test_input = '''32T3K 765
T55J5 684
KK677 28
KTJJT 220
QQQJA 483
'''
test_output = 6440

assertEqual(test_output, day7(test_input))

print('day7 answer:')
submit(day7(open('day7_input.txt', 'r').read()),
       expected=251136060)
print()
