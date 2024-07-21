from common import Gem
from common import Resource
import common

import collections

# TODO(durandal) spell scaling based on non-board info

Spell = collections.namedtuple('Spell', [
    # name as visible on screen
    'name',
    # required to cast, dict of Resource:quantity
    # can be handled by scanner detecting castability,
    # but might still be good for prioritization
    'cost',
    # will probably be handled by UI detecting whether spell is
    # castable, for now
    'cooldown',
    # a function which takes a board and game state and returns
    # a list of distinct argument tuples this spell
    # could be cast with
    'arg_generator',
    # a function which takes a board and game state and an argment tuple,
    # and (maybe) mutates the board and (maybe) yields
    # resource gain events
    # (not a total, since effects may need to hook onto individual gain events)
    'effect',
    # plaintext explanation of what this spell does
    'description',
    # once cast, how many enemy turns must take
    # place before casting again
])


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


def no_args(b, gs):
  return [()]


def choose_column(b, gs):
  return list(range(8))


def no_op(b, gs, args):
  # using this means probably something important is NYI
  return []


def heal(n):
  return lambda b, gs, args: [(Resource.LIFE, n)]


def damage(n):
  return lambda b, gs, args: [(Resource.DAMAGE, n)]


def yellow(n):
  return lambda b, gs, args: [(Resource.YELLOW, n)]


def turns(n):
  return lambda b, gs, args: [(Resource.TURN, n)]


def convert(b, gs, args):
  src, dst = args
  for r, c in common.all_coordinates():
    if b[r][c] == src:
      b[r][c] = dst
  return []


def destroy_column(b, gs, args):
  c = args
  destroyed_gems = [(r, c) for r in range(8)]
  return destroy_gems(b, destroyed_gems)


def destroy_gems(b, to_destroy, benefit=True):
  assert isinstance(b, list)

  to_destroy = collections.deque(to_destroy)
  total_yields = []
  while len(to_destroy) > 0:
    r, c = to_destroy.pop()
    g = b[r][c]
    if g == Gem.EMPTY:
      continue
    if benefit:
      if g == Gem.BIG_SKULL:
        for r2, c2 in neighbors(r, c):
          to_destroy.append((r2, c2))
        total_yields.append((Gem.SKULL, 5))
      else:
        total_yields.append((g, 1))

    b[r][c] = Gem.EMPTY

  return common.convert_gem_yields_to_resource_yields(total_yields)


SPELLS = [
    Spell('Gemberry', '4Y 6B', 1,
          no_args, heal(6),  # TODO(durandal): heal scales
          "Heal (5 + Blue mana / 4)."),
    Spell('Channel Air', '3G 3R 3B', 1,
          no_args, yellow(5),
          "Add +5 to Yellow Mana. Turn doesn't end."),
    Spell('Entangle', '12G 12Y', 4,
          no_args, turns(2),  # TODO(durandal): scaling
          "Enemy loses (1 + Green Mana / 20) turns. Turn doesn't end."),
    Spell('Calm', '2Y 3B', 1,
          no_args, no_op,
          "Removes status effects from both players. "
          "Turn doesn't end if Blue Mana >= 10."),
    Spell('Forest Fire', '6R 8Y', 1,
          no_args, damage(7),  # TODO(durandal): scaling
          "Deal (6 + Red Mana / 4) damage."),
    Spell('Call Lightning', '6G 9Y 6B', 1,
          choose_column, destroy_column,
          "Destroy a column of gems."),
    Spell('Evaporate', '5R 3B', 1,
          lambda b, gs: [(Gem.BLUE, Gem.YELLOW)], convert,
          "Convert Blue gems into Yellow."
          )
]
for s in SPELLS:
  assert parse_cost(s.cost) is not None

SPELLS_BY_NAME = {spell.name: spell for spell in SPELLS}

# print(SPELLS_BY_NAME)
