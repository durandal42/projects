COLORS = ['red', 'green', 'blue', 'yellow', 'white', 'rainbow']
MAX_NUMBER = 5
NUMBERS = list(range(1, MAX_NUMBER + 1))
NUMBER_FREQUENCY = {1: 3, 2: 2, 3: 2, 4: 2, 5: 1}
HAND_SIZE_BY_PLAYER_COUNT = {2: 6, 3: 5, 4: 4, 5: 3}

import random


# card = (color, number)
def new_deck():
  result = []
  for c in COLORS:
    for n in NUMBERS:
      result.extend([(c, n)] * NUMBER_FREQUENCY[n])
  random.shuffle(result)
  return result

# print "deck:", deck()
assert len(new_deck()) == 60

# board = {color:highest_value}


def board_score(board):
  return sum(v for k, v in board.iteritems())


def is_victory(board):
  return board_score(board) == len(COLORS) * MAX_NUMBER

assert is_victory({}) == False
assert is_victory({'red': 2}) == False
assert is_victory(dict((c, MAX_NUMBER) for c in COLORS)) == True


def is_playable(card, board):
  color, number = card
  return board.get(color, 0) == number - 1

assert is_playable(('red', 1), {}) == True
assert is_playable(('red', 2), {}) == False
assert is_playable(('red', 2), {'red': 1}) == True
assert is_playable(('white', 1), {'white': 1}) == False
assert is_playable(('green', 1), {'green': 4}) == False

# state = ([hands], board, deck, discard)


def new_game(num_players):
  deck = new_deck()
  discard = {}
  board = {}
  hands = []
  for p in range(num_players):
    hand = []
    for i in range(HAND_SIZE_BY_PLAYER_COUNT[num_players]):
      hand.append(deck.pop())
    hands.append(hand)
  return (hands, board, deck, discard)

print new_game(2)


def play_card(player_index, card_index, state):
  hands, board, deck, discard = state
  card = hands[player_index].pop(card_index)
  print 'player %d playing card %d: %s' % (player_index, card_index, card)
  assert is_playable(card, board)
  color, number = card
  board[color] = number
  if deck:
    hands[player_index].append(deck.pop())
    print 'player %d draws: %s' % (player_index, hands[player_index][-1])
  return (hands, board, deck, discard)


def discard_card(player_index, card_index, state):
  hands, board, deck, discard = state
  card = hands[player_index].pop(card_index)
  print 'player %d discarding card %d: %s' % (player_index, card_index, card)
  discard[card] = discard.get(card, 0) + 1
  if deck:
    hands[player_index].append(deck.pop())
    print 'player %d draws: %s' % (player_index, hands[player_index][-1])
  return (hands, board, deck, discard)


def pick_playable(player_index, state):
  hands, board, deck, discard = state
  hand = hands[player_index]
  playable_cards = [(i, c) for i, c in enumerate(hand) if is_playable(c, board)]
  if not playable_cards:
    return None
  playable_cards.sort(key=lambda ic: ic[1][1])
  return playable_cards[0][0]


def is_already_played(card, board):
  color, number = card
  return board.get(color, 0) >= number


def pick_discard(player_index, state):
  hands, board, deck, discard = state
  hand = hands[player_index]

  already_played_cards = [(i, c) for i, c in enumerate(hand)
                          if is_already_played(c, board)]
  if already_played_cards:
    return already_played_cards[0][0]

  # todo: detect holes, and abandon cards lost on the other side of them
  # lost_cards = [(c, n) for c in COLORS for n in NUMBERS
  #               if discard.get((c, n), 0) >= NUMBER_FREQUENCY[n]]
  # dead_cards =
  noncritical_cards = [(i, c) for i, c in enumerate(hand)
                       if discard.get(c, 0) < NUMBER_FREQUENCY[c[1]] - 1]
  noncritical_cards.sort(key=lambda ic: -ic[1][1])
  if noncritical_cards:
    return noncritical_cards[0][0]

  return None


def play_out(state):
  player_index = len(state[0])
  while not is_victory(state[1]):
    player_index += 1
    player_index %= len(state[0])
    # todo: endgame begins when deck runs dry

    card_to_play = pick_playable(player_index, state)
    if card_to_play is not None:
      state = play_card(player_index, card_to_play, state)
      continue

    card_to_discard = pick_discard(player_index, state)
    if card_to_discard is not None:
      state = discard_card(player_index, card_to_discard, state)
      continue

    print 'no playable or discardable cards in hand; giving up'
    print 'board:', state[1]
    print 'hand:', state[0][player_index]
    print 'hands:', state[0]
    print 'discard:', state[3]
    break

  return board_score(state[1]), state[1]

print play_out(new_game(2))
