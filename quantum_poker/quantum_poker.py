import collections

PLAYERS = 3

def print_hands(hands):
  print '['
  for hand in hands:
    print '\t', hand
  print ']'
  print

def possible(hand):
  return set(suit for card in hand for suit in card)

#print 'possible suits:', possible(start[0])

def ask(hands, asker, askee, suit):
  print '%d asks %d for a %d' % (asker, askee, suit)
  assert suit in possible(hands[asker])
  hands[asker] = constrain(hands[asker], suit)
  deduce(hands)

def answer(hands, asker, askee, suit, response):
  print '%d responds about suit %d: %s' % (askee, suit, response)
  if response:
    print 'transferring a %d from %d to %d' % (suit, askee, asker)
    hands[askee] = constrain(hands[askee], suit)
    hands[askee], hands[asker] = transfer(hands[askee], hands[asker], suit)
  else:
    hands[askee] = remove(hands[askee], suit)
  deduce(hands)

def constrain(hand, suit):
  # enforce that this hand now has suit in it

  # search for a card which is already definitely this suit
  for card in hand:
    if len(card) == 1 and suit in card:
      return hand

  # search for a card which *can* be this suit...
  for i, card in enumerate(hand):
    if suit in card:
      # ... and lock it down
      hand[i] = (suit,)
      sort(hand)
      return hand

  assert False
  return hand

def remove(hand, suit):
  hand = [tuple(s for s in card if s != suit) for card in hand]
  for card in hand:
    assert card
  sort(hand)
  return hand

def transfer(src, dst, suit):
  for i, card in enumerate(src):
    if len(card) == 1 and suit in card:
      del src[i]
      dst.append((suit,))
      sort(src)
      sort(dst)
      return src, dst
  assert False

def deduce(hands):
  known = collections.defaultdict(int)
  for hand in hands:
    for card in hand:
      if len(card) == 1:
        known[card[0]] += 1

  updated = False
  for suit, num_known in known.iteritems():
    assert num_known <= 4
    if num_known == 4:
      # all of this suit are accounted for; remove it as a possibility elsewhere
      for hand in hands:
        for i, card in enumerate(hand):
          if len(card) > 1 and suit in card:
            print "all %d's accounted for; removing possibility elsewhere" % suit
            hand[i] = tuple(s for s in card if s != suit)
            updated = True
  if updated:
    deduce(hands)
  sort_all(hands)

def sort(hand):
  hand.sort(key=lambda card: (len(card), card))

def sort_all(hands):
  for hand in hands: sort(hand)

def ask_and_answer(hands, asker, askee, suit, response):
  ask(hands, asker, askee, suit)
  print_hands(hands)
  answer(hands, asker, askee, suit, response)
  print_hands(hands)

def demo():
  hands = [[tuple(range(PLAYERS)) for card in range(4)] for player in range(PLAYERS)]
  print 'starting hands:'
  print_hands(hands)

  ask_and_answer(hands, 0, 1, 0, True)
  ask_and_answer(hands, 1, 2, 0, True)
  ask_and_answer(hands, 2, 0, 1, False)
  # TODO(durandal): "But there are only four 3's total, so at least one of B's cards must be a 2. Similarly, at least one of C's undetermined cards must be a 2."
  ask_and_answer(hands, 0, 2, 2, False)


demo()