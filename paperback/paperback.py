import collections
import random


class Card():
  WILD = '_'

  def __init__(self, letter=' ', play=0, cost=0, fame=0, special=None):
    self.letter = letter
    self.play = play
    self.cost = cost
    self.fame = fame
    self.special = special

  def __repr__(self):
    return "%s(%d)%s" % (self.letter, self.play, self.special and "*" or "")


def make_starting_deck():
  return [Card(letter=letter, play=1, cost=1) for letter in "RSTLN"] + ([Card(letter=Card.WILD, cost=2)] * 5)


def make_commons():
  return [Card(letter=letter, play=1, fame=5) for letter in "AEIO"]


def make_offer():
  return ([Card(letter=letter, play=2, cost=2, special='Trash after use') for letter in "AAEEIIOOUU"] +
          [Card(letter="ER", play=2, cost=3),
           Card(letter="TE", play=2, cost=3),
           Card(letter="ON", play=2, cost=3),
           Card(letter="TE", play=2, cost=3),
           Card(letter="IN", play=2, cost=3),
           Card(letter="RE", play=2, cost=3),
           Card(letter="AN", play=2, cost=3),
           Card(letter="TI", play=2, cost=3),
           Card(letter="ES", play=2, cost=3),
           Card(letter="EN", play=2, cost=3),
           Card(letter="AT", play=2, cost=3),
           Card(letter="S", play=1, cost=3,
                special="If this is the last letter, +1 card next hand"),
           Card(letter="S", play=1, cost=3,
                special="If word scores 8c or more, +1 card next hand"),
           Card(letter="T", play=1, cost=3,
                special="You may trash a card from hand. If you do, +1c"),
           Card(letter="T", play=1, cost=3,
                special="If this is the last letter, +1 card next hand"),
           Card(letter="L", play=1, cost=3,
                special="Attack: Cannot use the Common Card"),
           Card(letter="L", play=1, cost=3,
                special="If word uses all your cards, +2c"),
           Card(letter="N", play=1, cost=3,
                special="Attack: can only buy one card"),
           ])


def playable_words(hand, common, words):
  usable = collections.defaultdict(list)
  max_word_length = 0
  for card in hand + [common]:
    usable[card.letter].append(card)
    max_word_length += len(card.letter)
  for letter, values in usable.iteritems():
    values.sort(key=lambda c: c.play, reverse=True)

  usable_count = collections.Counter(card.letter for card in hand + [common])
  wilds_available = usable[Card.WILD]
  for word in words:
    if len(word) > max_word_length:
      continue

    played = ""
    score = 0
    triggers = []
    used = collections.defaultdict(int)

    i = 0
    while i < len(word):
      # greedily try double-letter cards > singles > wilds
      to_try = [word[i:i + 2], word[i], Card.WILD]
      text = None
      for t in to_try:
        if used[t] < len(usable[t]):
          text = t
          break
      if text is None:
        played = None
        break
      card_used = usable[text][used[text]]
      assert card_used.letter == text
      score += card_used.play
      used[text] += 1
      if card_used.special is not None:
        triggers.append(card_used.special)
      played += "[%s]" % text
      i += len(text)
    if played is not None:
      yield score, word, played  # , triggers


if __name__ == '__main__':

  print 'loading words...',
  words = set(line.upper().strip() for line in open('../TWL06.txt'))
  print 'done.'

  deck = make_starting_deck() + make_offer()
  commons = make_commons()
  random.shuffle(commons)
  hand = random.sample(deck, 7)

  print 'common:', commons[0]
  print 'hand:', hand
  for word in sorted(playable_words(hand, commons[0], words))[-10:]:
    print '\t', word
