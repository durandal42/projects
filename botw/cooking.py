import typing
import csv
import itertools
import collections


class Material(typing.NamedTuple):
  name: str
  sell_price: int
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
  strength: int


ON_HAND = set(
    '''
Hearty Durian
Palm Fruit
Apple
Wildberry
Spicy Pepper
Fleet-Lotus Seeds
Mighty Bananas
Big Hearty Truffle
Hearty Truffle
Endura Shroom
Hylian Shroom
Stamella Shroom
Chillshroom
Sunshroom
Zapshroom
Rushroom
Razorshroom
Ironshroom
Silent Shroom
Big Hearty Radish
Hearty Radish
Endura Carrot
Hyrule Herb
Swift Carrot
Fortified Pumpkin
Cool Safflina
Warm Safflina
Swift Violet
Mighty Thistle
Armoranth
Blue Nightshade
Silent Princess
Raw Gourmet Meat
Raw Whole Bird
Raw Prime Meat
Raw Bird Thigh
Raw Meat
Raw Bird Drumstick
Courser Bee Honey
Hylian Rice
Bird Egg
Fresh Milk
Acorn
Chickaloo Tree Nut
Goat Butter
Goron Spice
Rock Salt
Star Fragment
Dragon's Scale
Shard of Dragon's Horn
Hearty Salmon
Hearty Blueshell Snail
Hearty Bass
Hyrule Bass
Staminoka Bass
Chillfin Trout
Sizzlefin Trout
Voltfin Trout
Mighty Carp
Armored Carp
Sanke Carp
Mighty Porgy
Armored Porgy
Sneaky River Snail
Razorclaw Crab
Ironshell Crab
Bright-Eyed Crab
Fairy
Winterwing Butterfly
Summerwing Butterfly
Thunderwing Butterfly
Smotherwing Butterfly
Cold Darner
Warm Darner
Restless Cricket
Sunset Firefly
Hot-Footed Frog
Tireless Frog
Hightail Lizard
Hearty Lizard
Fireproof Lizard
Bokoblin Horn
Bokoblin Fang
Bokoblin Guts
Moblin Horn
Moblin Fang
Moblin Guts
Lizalfos Horn
Lizalfos Talon
Lizalfos Tail
Icy Lizalfos Tail
Red Lizalfos Tail
Yellow Lizalfos Tail
Lynel Horn
Lynel Guts
Chuchu Jelly
White Chuchu Jelly
Red Chuchu Jelly
Yellow Chuchu Jelly
Keese Wing
Ice Keese Wing
Fire Keese Wing
Electirc Keese Wing
Keese Eyeball
Octorok Tentacle
Octorok Eyeball
Octo Balloon
Hinox Toenail
Hinox Tooth
Hinox Guts
Ancient Screw
Ancient Spring
Ancient Gear
Ancient Shaft
Ancient Core
Giant Ancient Core
'''.strip().split('\n')
)


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
          sell_price=int(row["sell price"] or 10**6),
          category=row["Category"],
          hearts=float(row["Hearts"] or 0),
          duration=int(row["Duration"] or 0),
          bonus_duration=int(row["Bonus Duration"] or 0),
          is_critter=(row["critter?"] == "TRUE"),
          effect=row["Effect"],
          potency=float(row["Potency"] or 0),
          star_bonus=(row["star?"] == "TRUE"),
          is_condiment=(row["condiment?"] == "TRUE"),
      )

      result.append(m)
      # print(m)
  print(f"Loaded {len(result)} materials.")
  pretty_print_ingredients(result)

  names_seen = set(m.name for m in result)
  for n in ON_HAND:
    if n not in names_seen:
      print("Material listed in ON_HAND but was not loaded:", n)
      exit(-1)
  result = [m for m in result if m.name in ON_HAND]
  print(f"Filtered down to {len(result)} materials actually on hand.")
  pretty_print_ingredients(result)

  result = collapse_identical_ingredients(result)
  print(f"Collapsed down to {len(result)} mechanically distinct materials.")
  pretty_print_ingredients(result)

  print("Available effects:", set([i.effect for i in result]))

  return result


def pretty_print_ingredients(ingredients):
  print("[")
  print("\n".join(f"\t{m.name}" for m in ingredients))
  print("]")


def collapse_identical_ingredients(ingredients):
  nameless_map = collections.defaultdict(list)
  for i in ingredients:
    nameless_map[i._replace(name='')].append(i.name)
  return [nameless._replace(name=' | '.join(names))
          for nameless, names in nameless_map.items()]


DURATION_INDEPENDENT_EFFECTS = [
    "Energizing",
    "Enduring",
    "Hearty",
]


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

  effects = set([i.effect for i in ingredients if i.effect])
  if len(effects) == 1:  # more than one effect cancel each other
    effect = list(effects)[0]
    potency = sum(i.potency for i in ingredients)
    strength = strength_from_potency(effect, potency)
  elif len(effects) == 0:
    effect = ''
    duration = 0
    strength = 0
  else:
    return None  # not strictly true, but we "never" want to do this

  if effect in DURATION_INDEPENDENT_EFFECTS:
    duration = 0

  return Dish(name="unknown", hearts=hearts,
              effect=effect, duration=duration, strength=strength)


POTENCY_THRESHOLDS = {
    "Attack Up": (5, 7),
    "Defense Up": (5, 7),
    "Movement Speed Up": (5, 7),
    "Stealth Up": (6, 9),
    "Flame Guard": (7,),
    "Cold Resistance": (6,),
    "Heat Resistance": (6,),
    "Shock Resistance": (4, 6),
    "Hearty": range(2, 31),
    "Energizing": (2, 3, 3, 4, 5, 5, 6, 7, 8, 8, 9, 10, 10, 11),
    "Enduring": range(4, 22, 2),
}


def strength_from_potency(effect, potency):
  if effect not in POTENCY_THRESHOLDS:
    print(effect, "not in POTENCY_THRESHOLDS")
    assert effect in POTENCY_THRESHOLDS
  thresholds = POTENCY_THRESHOLDS[effect]

  strength = 1
  for t in thresholds:
    if potency < t:
      break
    strength += 1

  return strength


def print_dish(dish):
  full_hearts = "♥" * int(dish.hearts)
  maybe_half_heart = (dish.hearts % 1 > 0) and "𑁤" or ""
  hearts = f'[{full_hearts + maybe_half_heart}]'

  effect_duration = dish.duration and f' {dish.duration}s' or ''
  effect = dish.effect and f'[{dish.effect} {dish.strength}{effect_duration}]' or ''
  return hearts + effect


def ingredient_cost(ingredients):
  return sum(i.sell_price for i in ingredients)


HEART_CAP = 3
STAMINA_CAP = 6  # in 5ths of a stamina wheel
DURATION_CAP = 30*60  # 30 minutes


def dish_score(dish, required_effect=None, required_strength=None):
  if required_effect is not None and dish.effect != required_effect:
    return None
  if required_strength is not None and dish.strength < required_strength:
    return None

  if required_effect is None:
    return min(dish.hearts, HEART_CAP)
  if dish.duration == 0 and dish.effect in DURATION_INDEPENDENT_EFFECTS:
    return min(dish.strength, STAMINA_CAP)
  else:
    return min(dish.duration, DURATION_CAP)


def main():
  ingredients = load_ingredients()

  results = []
  for di in itertools.chain.from_iterable(
          itertools.combinations_with_replacement(ingredients, r=r)
          for r in range(1, 6)):
    d = dish(di)
    if not d:
      continue

    score = dish_score(d,
                       required_effect="Cold Resistance",
                       required_strength=2,
                       )
    if not score:
      continue

    results.append(
        (score / ingredient_cost(di),
         d, di))

  # print(results)

  for score, d, di in sorted(results):
    print(score,
          collections.Counter([i.name for i in di]),
          "\n\t->", print_dish(d))


if __name__ == "__main__":
  main()
