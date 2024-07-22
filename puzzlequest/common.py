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

  def __repr__(self):
    return str(self.value)


def all_coordinates():
  for r in range(8):
    for c in range(8):
      yield r, c


GEM_TO_RESOURCE = {
    Gem.GREEN: Resource.GREEN,
    Gem.RED: Resource.RED,
    Gem.YELLOW: Resource.YELLOW,
    Gem.BLUE: Resource.BLUE,
    Gem.SKULL: Resource.DAMAGE,
    Gem.STAR: Resource.EXP,
    Gem.COIN: Resource.GOLD,
}


def convert_gem_yields_to_resource_yields(gy):
  return [(GEM_TO_RESOURCE.get(gem, gem), amount) for gem, amount in gy]


def apply_buffs(resource_yields):
  result = []
  for resource, amount in resource_yields:
    # TODO(durandal): handle items/effects in a more systematic way

    # Item: Helm of the Ram
    if resource == Resource.DAMAGE and amount >= 3:
      amount += 2

    # Item: Elven Bow
    if resource == Resource.DAMAGE and amount >= 2:
      # TODO(durandal): these might trigger more effects; loop it back around!
      result.append((Resource.GREEN, 2))
      result.append((Resource.YELLOW, 2))

    result.append((resource, amount))
  return result


def sum_yields(ys):
  result = collections.Counter()
  for kind, amount in ys:
    result[kind] += amount
  return result
