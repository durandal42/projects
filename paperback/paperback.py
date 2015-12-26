import collections
import random

class Card():
  WILD = '_'

  def __init__(self, letter=' ', play_value=0, cost=0, fame=0, special=None):
    self.letter = letter
    self.play_value = play_value
    self.cost = cost
    self.fame = fame
    self.special = special

  def __repr__(self):
    return "%s(%d)%s" % (self.letter, self.play_value, self.special and "*" or "")


def make_starting_deck():
  return [Card(letter=letter, play_value=1, cost=1) for letter in "RSTLN"] + ([Card(letter=Card.WILD, cost=2)] * 5)

def make_commons():
  return [Card(letter=letter, play_value=1, fame=5) for letter in "AEIO"]

def make_offer():
  return [Card(letter=letter, play_value=2, cost=2, special='Trash after use') for letter in "AAEEIIOOUU"]

def playable_words(hand, common, words):
  usable = collections.defaultdict(list)
  for card in hand+[common]:
    usable[card.letter].append(card.play_value)
  for letter, values in usable.iteritems():
    values.sort(reverse=True)
  print usable

  usable_count = collections.Counter(card.letter for card in hand+[common])
  wilds_available = usable[Card.WILD]
  for word in words:
    if len(word) > len(hand):  # TODO(durandal): double-letter cards break this.
      continue

    can_play = True
    score = 0
    used = collections.defaultdict(int)
    for letter in word:
      if used[letter] >= len(usable[letter]):
        letter = Card.WILD
        if used[letter] >= len(usable[letter]):
          can_play = False
          break
      score += usable[letter][used[letter]]
      used[letter] += 1
    yield score, word


if __name__ == '__main__':

  print 'loading words...',
  words = set(line.upper().strip() for line in open('TWL06.txt'))
  print 'done.'

  deck = make_starting_deck() + make_offer()
  commons = make_commons()
  random.shuffle(commons)
  hand = random.sample(deck, 7)
  print 'common:', commons[0]
  print 'hand:', hand
  for word in sorted(playable_words(hand, commons[0], words))[-10:]:
    print '\t', word
