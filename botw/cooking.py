import typing
import csv
import itertools
import collections


class Material(typing.NamedTuple):
  name: str
  category: str
  hearts: float
  duration: int
  bonus_duration: int
  is_critter: bool
  effect: str
  potency: float
  star_bonus: bool
  is_condiment: bool


class Dish(typing.NamedTuple):
  name: str
  hearts: float
  effect: str
  duration: int
  potency: float


ON_HAND = set([
    "Apple",
    "Spicy Pepper",
    "Hylian Shroom",
    "Stamella Shroom",
    "Rushroom",
    "Ironshroom",
    "Hyrule Herb",
    "Swift Carrot",
    "Fortified Pumpkin",
    "Mighty Thistle",
    "Armoranth",
    "Raw Meat",
    "Raw Bird Drumstick",
    "Courser Bee Honey",
    "Acorn",
    "Rock Salt",
    "Hyrule Bass",
    "Sneaky River Snail",
    "Sunset Firefly",
    "Hot-Footed Frog",
    "Hightail Lizard",
    "Bokoblin Horn",
    "Bokoblin Fang",
    "Bokoblin Guts",
    "Lizalfos Horn",
    "Lizalfos Talon",
    "Chuchu Jelly",
    "Keese Wing",
    "Keese Eyeball",
    "Octorok Tentacle",
    "Octo Balloon",
])


# Reads data copied from a sheet like https://docs.google.com/spreadsheets/
# d/1XZMrMbrRjVnInAn5nbW1Z6CkjeH-son9Dhv17dO6Fkk/edit?gid=0#gid=0
# Columns needed:
# Material  Category  Hearts  Duration
# BonusDuration critter?  Effect  Potency star? condiment?
def load_ingredients():
  result = []
  with open('ingredients.csv') as csvfile:
    reader = csv.DictReader(csvfile, delimiter='\t', quotechar='"')
    for row in reader:
      # print(row)

      m = Material(
          name=row["Material"],
          category=row["Category"],
          hearts=float(row["Hearts"] or 0),
          duration=int(row["Duration"] or 0),
          bonus_duration=int(row["BonusDuration"] or 0),
          is_critter=(row["critter?"] == "TRUE"),
          effect=row["Effect"],
          potency=float(row["Potency"] or 0),
          star_bonus=(row["star?"] == "TRUE"),
          is_condiment=(row["condiment?"] == "TRUE"),
      )

      result.append(m)
      # print(m)

  names_seen = set(m.name for m in result)
  for n in ON_HAND:
    if n not in names_seen:
      print("Material listed in ON_HAND but was not loaded:", n)
      exit(-1)

  result = [m for m in result if m.name in ON_HAND]

  result = collapse_identical_ingredients(result)

  return result


def collapse_identical_ingredients(ingredients):
  nameless_map = collections.defaultdict(list)
  for i in ingredients:
    nameless_map[i._replace(name='')].append(i.name)
  return [nameless._replace(name=' | '.join(names))
          for nameless, names in nameless_map.items()]


def dish(ingredients):
  # TODO: naming the result

  has_parts = any(i.category == "Monster Parts" for i in ingredients)
  has_critters = any(i.is_critter for i in ingredients)
  if (has_parts != has_critters):
    # not strictly true, but we "never" want to do this
    return None

  hearts = sum(i.hearts for i in ingredients)

  duration = sum(i.duration for i in ingredients)
  bonus_duration_collected = set()
  for i in ingredients:
    if i.name not in bonus_duration_collected:
      duration += i.bonus_duration
    bonus_duration_collected.add(i.name)

  # TODO: potency tiers by effect
  potency = sum(i.potency for i in ingredients)

  effects = set([i.effect for i in ingredients if i.effect])
  if len(effects) == 1:  # more than one effect cancel each other
    effect = list(effects)[0]
  elif len(effects) == 0:
    effect = None
    duration = None
    potency = None
  else:
    return None  # not strictly true, but we "never" want to do this

  return Dish(name="unknown", hearts=hearts,
              effect=effect, duration=duration, potency=potency)


def print_dish(dish):
  full_hearts = "♥" * int(dish.hearts)
  maybe_half_heart = (dish.hearts % 1 > 0) and "𑁤" or ""
  hearts = f'[{full_hearts + maybe_half_heart}]'

  effect_duration = dish.duration and f' {dish.duration}s' or ''
  effect = dish.effect and f'[{dish.effect} {dish.potency}{effect_duration}]' or ''
  return hearts + effect


def main():
  ingredients = load_ingredients()

  for dish_ingredients in itertools.combinations_with_replacement(ingredients, r=3):
    d = dish(dish_ingredients)
    if not d:
      continue
    print(collections.Counter(
        [i.name for i in dish_ingredients]), "\n\t->", print_dish(d))


if __name__ == "__main__":
  main()
