from enum import Enum
import collections


class Gem(Enum):
  EMPTY = '⬛'
  GREEN = '🟩'
  RED = '🟥'
  YELLOW = '🟨'
  BLUE = '🟦'
  SKULL = '💀'
  STAR = '🔯'
  COIN = '💰'
  BIG_SKULL = '☠️'
  WILD2 = '🍭2'
  WILD3 = '🍭3'
  WILD4 = '🍭4'
  WILD5 = '🍭5'
  WILD6 = '🍭6'  # TODO(durandal): more wilds


class Resource(Enum):
  GREEN = '🟩'
  RED = '🟥'
  YELLOW = '🟨'
  BLUE = '🟦'
  DAMAGE = '💀'
  EXP = '🔯'
  GOLD = '💰'
  LIFE = '❤️'
  TURN = '♻️'


def all_coordinates():
  for r in range(8):
    for c in range(8):
      yield r, c


def convert_gem_to_resource(g):
  # TODO(durandal): skill scaling happens here?
  return {
      Gem.GREEN: Resource.GREEN,
      Gem.RED: Resource.RED,
      Gem.YELLOW: Resource.YELLOW,
      Gem.BLUE: Resource.BLUE,
      Gem.SKULL: Resource.DAMAGE,
      Gem.STAR: Resource.EXP,
      Gem.COIN: Resource.GOLD,
  }[g]


def convert_gem_yields_to_resource_yields(gy):
  result = []
  for gem, amount in gy:
    result.append((convert_gem_to_resource(gem), amount))
  return result


def sum_yields(ys):
  result = collections.Counter()
  for kind, amount in ys:
    result[kind] += amount
  return result
