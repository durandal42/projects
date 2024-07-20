from common import assertEqual
from common import submit
import collections


CARD_RANKS = [
    'A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2',
]


def rank_card(c):
  # TODO(durandal): map lookup if this bottlenecks
  return -CARD_RANKS.index(c)


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


def day07(input):
  result = 0
  for i, score_and_bid in enumerate(score_and_rank_hands(parse_input(input))):
    bid = score_and_bid[2]
    # print(i + 1, score_and_bid, "->", (i + 1) * bid)
    result += (i + 1) * bid
  return result


test_input = '''\
32T3K 765
T55J5 684
KK677 28
KTJJT 220
QQQJA 483
'''
test_output = 6440

assertEqual(test_output, day07(test_input))

print('day07 answer:')
submit(day07(open('day07_input.txt', 'r').read()),
       expected=251136060)
print()

# part 2 complication
test_output = 5905

CARD_RANKS = [
    'A', 'K', 'Q', 'T', '9', '8', '7', '6', '5', '4', '3', '2', 'J',
]


def rank_hand(hand):
  # TODO(durandal): be more clever if this is somehow too slow, but I think it's
  # worst case 12**5 times slower than part 1, if the whole hand is J's.
  if 'J' in hand:
    i = hand.index('J')
    return max(rank_hand(hand[0:i] + r + hand[i + 1:]) for r in CARD_RANKS[:-1])
  return tuple(sorted(collections.Counter(hand).values(), reverse=True))


assertEqual(test_output, day07(test_input))

print('day07 part2 answer:')
submit(day07(open('day07_input.txt', 'r').read()),
       expected=249400220)
print()
