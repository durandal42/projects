from enum import Enum
from collections import namedtuple
from pq import destroy_gems

# TODO(durandal) spell scaling based on non-board info

Spell = namedtuple('Spell', [
    # name as visible on screen
    'name',
    # required to cast, dict of Resource:quantity
    # can be handled by scanner detecting castability,
    # but might still be good for prioritization
    'cost',
    'cooldown',  # will probably be handled by UI detecting whether spell is castable, for now
    # a function which takes a board and returns
    # a list of distinct argument tuples this spell
    # could be cast with
    'args',
    # a function which takes a board and argment tuple,
    # and (maybe) mutates the board and (maybe) yields
    # resource gain events
    # (not a total, since effects may need to hook onto individual gain events)
    'effect',
    # plaintext explanation of what this spell does
    'description',
    # once cast, how many enemy turns must take
    # place before casting again
])


class Resource(Enum):
  GREEN = '🟩'
  RED = '🟥'
  YELLOW = '🟨'
  BLUE = '🟦'
  DAMAGE = '💀'
  EXP = '🔯'
  GOLD = '💰'
  LIFE = '❤️‍🩹'
  TURN = '♻️'


COST_STR_TO_RESOURCE = {
    "G": Resource.GREEN,
    "R": Resource.RED,
    "Y": Resource.YELLOW,
    "B": Resource.BLUE,
}


def parse_cost(cost_str):
  result = {}
  tokens = cost_str.split()
  for t in tokens:
    mana_color_str = t[-1]
    mana_quantity_str = t[:-1]
    result[COST_STR_TO_RESOURCE[mana_color_str]] = int(mana_quantity_str)
  return result


def no_args(b):
  return [()]


def choose_column(b):
  return list(range(8))


def no_op():
  # using this means probably something important is NYI
  return lambda b, args: []


def heal(n):
  return lambda b, args: [(Resource.LIFE, n)]


def damage(n):
  return lambda b, args: [(Resource.DAMAGE, n)]


def yellow(n):
  return lambda b, args: [(Resource.YELLOW, n)]


def turns(n):
  return lambda b, args: [(Resource.TURN, n)]


def destroy_column():
  return lambda b, args:


SPELLS = [
    Spell('Gemberry', '4Y 6B', 1,
          no_args, heal(6),
          "Heal (5 + Blue mana / 4)."),
    Spell('Channel Air', '3G 3R 3B',
          no_args, yellow(5), 1,
          "Add +5 to Yellow Mana. Turn doesn't end."),
    Spell('Entangle', '12G 12Y', 4,
          no_args, turns(2),
          "Enemy loses (1 + Green Mana / 20) turns. Turn doesn't end."),
    Spell('Calm', '2Y 3B', 1,
          no_args, no_op,
          "Removes status effects from both players. Turn doesn't end if Blue Mana >= 10."),
    Spell('Forest Fire', '6R 8Y', 1,
          no_args, damage(7),
          "Deal (6 + Red Mana / 4) damage."),
    Spell('Call Lightning', '6G 9Y 6B', 1,
          choose_column, destroy_column,
          "Destroy a column of gems."),
]
for s in SPELLS:
  assert parse_cost(s.cost) is not None
