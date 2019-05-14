def tuple_add(t1, t2):
  """Utility function for pairwise tuple addition."""
  assert isinstance(t1, tuple)
  assert isinstance(t2, tuple)
  assert len(t1) == len(t2)
  return tuple(i + j for i, j in zip(t1, t2))


def tuple_scale(s, t):
  """Utility function for tuple scalar multiplication."""
  assert isinstance(t, tuple)
  return tuple(s * v for v in t)


class Memoize:
  """Utility class for annotating functions to be memoized."""

  def __init__(self, fn):
    self.fn = fn
    self.memo = {}

  def __call__(self, *args):
    if args not in self.memo:
      self.memo[args] = self.fn(*args)
    return self.memo[args]


# Attacks come in three strengths.
MAX_STRENGTH = 3
ATTACKS = range(1, 1 + MAX_STRENGTH)

# Stronger attacks cost more stamina.
STAMINA_COST = {1: 1, 2: 2, 3: 3}
# ... but do more damage.
DAMAGE = {1: 1.0, 2: 2.5, 3: 4.0}
# ... and increase the accuracy of all additional attacks in the same chain.
ACCURACY_GAIN = {1: 1, 2: 3, 3: 7}

print "\nstrength:\tdamage efficiency (ignoring chance to hit)"
for a in ATTACKS:
  print "%d: %s" % (a, DAMAGE[a] / float(STAMINA_COST[a]))

print "\nstrength:\taccuracy gain efficiency (ignoring chance to hit)"
for a in ATTACKS:
  print "%d: %s" % (a, ACCURACY_GAIN[a] / float(STAMINA_COST[a]))


# Some equipped items increase chance to hit.
ACCURACY_ITEMS = {
    "sight scope": 3 + 2,  # fudge: glenn putting on sight scope
    "silver loupe": 2 + 4,  # fudge: kid putting on a silver loupe
    "dragoon's honor": 2 - 2,  # fudge: serge putting on dg while wearing silver loupe
}

# Weapons are made of different materials. Better materials do more
# damage, and are more likely to hit.
MATERIAL_MODIFIER = {
    "bone": (0, 0),
    "copper": (2, 1),
    "iron": (5, 2 + 3),  # fudge: glenn with no hit items and steel sword
    "mythril": (8, 2 + 3),  # fudge: lynx with silver swallow
    "denadorite": (12, 3),
    "rainbow": (17, 4),
}

# Weapon names have several variants which refer back to the same base material.
CANONICAL_MATERIAL = {
    "bone": "bone",
    "sea": "bone",
    "ivory": "bone",
    "porcelain": "bone",

    "copper": "copper",
    "bronze": "copper",
    "brass": "copper",

    "iron": "iron",
    "steel": "iron",
    "ferrous": "iron",

    "mythril": "mythril",
    "silver": "mythril",
    "argent": "mythril",

    "denadorite": "denadorite",
    "stone": "denadorite",

    "rainbow": "rainbow",
    "spectral": "rainbow",
    "prism": "rainbow",
}


def tare_material(stats, baseline_material):
  """
  Derive a fake "bone" version of a weapon class.

  Some weapons aren't available in low-quality materials, but the data on
  weapon stats all treats the weakest existing member of a weapon class as
  the baseline item. For such weapon classes, derive a fake "bone" version
  of that weapon.
  """
  return tuple(stat - mod for stat, mod in
               zip(stats, MATERIAL_MODIFIER[CANONICAL_MATERIAL[baseline_material]]))

# Weapons come in classes; these are the stats of the "bone" version of
# that class.
WEAPON_CLASS = {
    "swallow": (60, 85 + 4),  # fudge: serge with no hit items and sea swallow
    "glove": (47, 85),
    "sword": (36, 82 + 7),  # fudge: glenn with no hit items and bronze sword
    "axe": (51, 82),
    "dagger": (50, 89),
    "rod": (40, 85 - 2),  # porcelain rod is baseline and special
    "staff": tare_material((54, 91), "silver"),
    "gun": tare_material((58, 87), "ferrous"),
    "utensil": (51, 85),
    "carrot": (61, 93),
    "shot": tare_material((48, 84), "bronze"),
    "pick": (48, 89),
    "lure": tare_material((52, 86), "bronze"),
    "boomerang": tare_material((50, 84), "iron"),
}

# Some weapons have names that aren't trivially parseable as MATERIAL CLASS.
SPECIAL_WEAPONS = {
    # "name": ["base name", (delta from a weapon of that base name)]
    "mastermune": ["sea swallow", (15, 4)],
    "hero's blade": ["bone sword", (3, 4)],
    "einlanzer": ["bone sword", (13, 4)],
    "viper's venom": ["bone sword", (15, 0)],
    "slasher": ["bone sword", (15, 4)],
    "einlanzer (2)": ["bone sword", (18, 4)],
    "hammer": ["bone axe", (9, 5)],
    "master hammer": ["bone axe", (15, 5)],
    "porcelain rod": ["bone rod", (0, 2)],
    "shockwave gun": ["ferrous gun", (5, 2)],
    "plasma pistol": ["ferrous gun", (11, 2)],
    "spatula ca20": ["bone utensil", (0, 0)],
    "besom cu29": ["copper utensil", (0, 0)],
    "ladle fe26": ["iron utensil", (0, 0)],
    "frypan ag47": ["silver utensil", (0, 0)],
    "saucepan si02": ["stone utensil", (0, 0)],
    "crystalpan c6": ["rainbow utensil", (-3, 0)],
    "carrot": ["bone carrot", (0, 0)],
    "beta carotene": ["bone carrot", (6, 0)],
    "prism pellets": ["rainbow shot", (0, 0)],
    "private deck": ["bronze shot", (10, 3)],
    "pack of lies": ["bronze shot", (15, 3)],
    "steelrang": ["steel boomerang", (0, 0)],
    "silverang": ["silver boomerang", (0, 0)],
    "rockerang": ["rock boomerang", (0, 0)],
    "prismarang": ["rainbow boomerang", (0, 0)],
}


def weapon_stats(name):
  """Look up a weapon's stats, from its name."""
  if name in SPECIAL_WEAPONS:
    base, delta = SPECIAL_WEAPONS[name]
    return tuple_add(weapon_stats(base), delta)
  tokens = name.lower().split(" ")
  assert len(tokens) == 2
  weapon_material, weapon_class = tokens
  return tuple_add(WEAPON_CLASS[weapon_class], MATERIAL_MODIFIER[CANONICAL_MATERIAL[weapon_material]])

for name in ["sea swallow", "steel swallow", "ivory dagger", "bronze sword", "steel sword"]:
  print "%s:\t%s" % (name, weapon_stats(name))

# Constants used by some accuracy calculations.
NORMAL_HIT_MOD = 50
STRONG_HIT_MOD = 20


def base_hits(acc=85, equip_acc=0, evade=0):
  """Compute the base hit rates for the three attack strengths."""

  # The internet claims the basic ACC values of 80,85,90 are wrong.
  # https://www.chronocompendium.com/Term/Hit.html
  # if acc == 80: acc += 2
  # if acc == 90: acc -= 1

  # Black magic!
  # https://www.chronocompendium.com/Term/Game_Mechanics.html
  # https://gamefaqs.gamespot.com/boards/196917-chrono-cross/55191996
  acc_mod = equip_acc * 2 / 3
  return (min(100, acc_mod + acc / 3 - evade),
          min(100, acc_mod + NORMAL_HIT_MOD / 3 - evade),
          min(100, acc_mod + STRONG_HIT_MOD / 3 - evade))


def steal(hits, attacked=False):
  """Compute the chance of stealing an item."""
  # More black magic!
  # https://gamefaqs.gamespot.com/boards/196917-chrono-cross/61544012?page=2
  if attacked:
    chance = hits[2]
  else:
    chance = STRONG_HIT_MOD
  return chance * 2


def gear(weapon, items):
  """Compute equip_acc from a weapon and any equipped items."""
  return weapon_stats(weapon)[1] + sum(ACCURACY_ITEMS[item] for item in items)

# Trying to sanity check all of the above.
# It's not quite right; see "fudge" comments.
print "\nbase combat hit chance (full gear):"
print "serge (observed):", (94, 82, 72)
serge_base_hits = base_hits(acc=85, equip_acc=gear(
    "silver swallow", ["silver loupe", "dragoon's honor"]))
print "serge (computed):", serge_base_hits
print "kid (observed):", (96, 82, 72)
kid_base_hits = base_hits(acc=90, equip_acc=gear(
    "iron dagger", ["silver loupe"]))
print "kid (computed):", kid_base_hits
print "glenn (observed):", (94, 82, 72)
glenn_base_hits = base_hits(acc=85, equip_acc=gear(
    "steel sword", ["sight scope"]))
print "glenn (computed):", glenn_base_hits

print "\nbase combat hit chance (no +hit items):"
print "serge (observed):", (90, 78, 68)
print "serge (computed):", base_hits(acc=85, equip_acc=gear("steel swallow", []))
print "kid (observed):",   (92, 78, 68)
print "kid (computed):", base_hits(acc=90, equip_acc=gear("iron dagger", []))
print "glenn (observed):", (90, 78, 68)
print "glenn (computed):", base_hits(acc=85, equip_acc=gear("steel sword", []))

print "\nbase combat hit chance (no +hit items, low-tier weapons):"
print "serge (observed):", (87, 75, 65)
print "serge (computed):", base_hits(acc=85, equip_acc=gear("sea swallow", []))
print "kid (observed):", (89, 75, 65)
print "kid (computed):", base_hits(acc=90, equip_acc=gear("ivory dagger", []))
print "glenn (observed):", (88, 76, 66)
print "glenn (computed):", base_hits(acc=85, equip_acc=gear("bronze sword", []))


def update_hits(hits, num_updates=1):
  """Increase accuracy after landing a hit."""
  # https://www.chronocompendium.com/Term/Game_Mechanics.html
  # https://gamefaqs.gamespot.com/boards/196917-chrono-cross/55191996
  # stronger attacks apply this update multiple times.
  for i in range(num_updates):
    weak, medium, heavy = hits
    # Black magic!
    weak += (102 - weak) * 30 / 100
    medium += (102 - medium) * 25 / 100
    heavy += (103 - heavy) * 20 / 100
    hits = weak, medium, heavy
  return hits


def demo_hit_update(hits, steps, increment=1):
  result = [hits]
  for i in range(steps):
    hits = update_hits(hits, increment)
    result.append(hits)
  return result

# Sanity check hit updating; this seems to be exactly correct!
print "\nimproved combat hit chance 1(+1):"
print "serge (observed):", [(90, 78, 68), (93, 84, 75), (95, 88, 80), (97, 91, 84), (98, 93, 87), (99, 95, 90), (99, 96, 92)]
print "serge (computed):", demo_hit_update((90, 78, 68), 6, ACCURACY_GAIN[1])
print "kid (observed):", [(89, 75, 65), (92, 81, 72), (95, 86, 78), (97, 90, 83), (98, 93, 87), (99, 95, 90), (99, 96, 92)]
print "kid (computed):", demo_hit_update((89, 75, 65), 6, ACCURACY_GAIN[1])
print "glenn (observed):", [(90, 78, 68), (93, 84, 75), (95, 88, 80), (97, 91, 84), (98, 93, 87), (99, 95, 90), (99, 96, 92)]
print "glenn (computed):", demo_hit_update((90, 78, 68), 6, ACCURACY_GAIN[1])

print "\nimproved combat hit chance 2(+3):"
print "serge (observed):", [(90, 78, 68), (97, 91, 84), (99, 96, 92), (99, 99, 96)]
print "serge (computed):", demo_hit_update((90, 78, 68), 3, ACCURACY_GAIN[2])
print "kid (observed):", [(89, 75, 65), (97, 90, 83), (99, 96, 92), (99, 99, 96)]
print "kid (computed):", demo_hit_update((89, 75, 65), 3, ACCURACY_GAIN[2])
print "glenn (observed):", [(90, 78, 68), (97, 91, 84), (99, 96, 92), (99, 99, 96)]
print "glenn (computed):", demo_hit_update((90, 78, 68), 3, ACCURACY_GAIN[2])

print "\nimproved combat hit chance 3(+7):"
print "serge (observed):", [(90, 78, 68), (99, 97, 94), (99, 99, 99)]
print "serge (computed):", demo_hit_update((90, 78, 68), 2, ACCURACY_GAIN[3])
print "kid (observed):", [(89, 75, 65), (99, 97, 94), (99, 99, 99)]
print "kid (computed):", demo_hit_update((89, 75, 65), 2, ACCURACY_GAIN[3])
print "glenn (observed):", [(90, 78, 68), (99, 97, 94), (99, 99, 99)]
print "glenn (computed):", demo_hit_update((90, 78, 68), 2, ACCURACY_GAIN[3])


def create_state(hits, remaining_stamina=7, elemental_power=0, damage_dealt=0, stamina_spent=0):
  """A combat state is just a tuple, for now."""
  return (hits, remaining_stamina, elemental_power, damage_dealt, stamina_spent)


def descendent_states(state, strength):
  """Compute possible next states, and the probability of landing in them."""
  hits, remaining_stamina, elemental_power, damage_dealt, stamina_spent = state
  hit_chance = hits[strength - 1]
  hit_state = create_state(update_hits(hits, ACCURACY_GAIN[strength]),
                           remaining_stamina - strength,
                           elemental_power + strength,
                           damage_dealt + DAMAGE[strength],
                           stamina_spent + strength)
  miss_chance = 100 - hit_chance
  miss_state = create_state(
      hits, remaining_stamina - strength, elemental_power, damage_dealt, stamina_spent + strength)
  return [(hit_chance, hit_state), (miss_chance, miss_state)]

# Functions to evaluate how good a state is:


def utility_damage(state):
  """All we care about is damage done."""
  return state[3]


def utility_damage_efficiency():
  """All we care about is damage done per stamina spent."""
  # This is misguided; a character that swings once and hits will decline
  # to spend further stamina, because it can only hurt their efficiency score.
  # Use utility_sustained_damage instead.
  return lambda s: s[3] / float(max(1, s[4]))

def utility_sustained_damage(guess=0.0):
  # You'll need to iterate, feeding dps back in as the next iteration's guess,
  # until it converges. See sustained_dps().
  HORIZON = 21  # 21 stamina, 3 full combos
  return lambda s: (s[3] + (HORIZON - max(1, s[4])) * guess) / float(HORIZON)

def utility_remaining_stamina(state):
  """All we care about is remaining stamina."""
  return state[1]


def utility_elemental_power(cap=5):
  """All we care about is charging up elemental power."""
  return lambda s: min(cap, s[2])


def utility_steal_chance(state):
  """All we care about is maxing our chance of stealing an item."""
  hits = state[0]
  damage_dealt = state[3]
  return min(100, steal(hits, damage_dealt > 0))


def compose(*args):
  """Compose several utility functions, in priority order."""
  return lambda s: tuple(f(s) for f in args)

# TODO(durandal): consider a weighted combination of utility functions?


@Memoize
def evaluate(state, f):
  """Find the attack strength which, in expectation, leads to the best outcome.

  Along the way, we'll end up computing every reachable state."""
  hits, remaining_stamina, elemental_power, damage_dealt, stamina_spent = state
  results = [(f(state), None)]
  for s in range(1, 1 + min(3, remaining_stamina)):
    descendents = descendent_states(state, s)
    evaluations = [(descendent_chance, evaluate(descendent_state, f)[0])
                   for descendent_chance, descendent_state in descendents]
    if isinstance(evaluations[0][1], tuple):
      ev = tuple_scale(1.0 / 100.0,
                       reduce(tuple_add,
                              (tuple_scale(descendent_chance, evaluation)
                               for descendent_chance, evaluation in evaluations)))
    else:
      ev = sum(evaluation * descendent_chance
               for descendent_chance, evaluation in evaluations) / 100.0
    results.append((ev, s))
  best = max(results)
  # print state, best
  return best


# @Memoize
def display_tree(state, f, depth=0, quiet=False):
  """Display only the branches of the state tree that we'll actually pick."""
  score, strength = evaluate(state, f)
  if not quiet:
    print "%s%s -> %s (%s)" % ('\t' * depth, state, strength, score)
  if strength is not None:
    for descendent in descendent_states(state, strength):
      display_tree(descendent[1], f, depth + 1, quiet)
  return (score, strength)


def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

def sustained_dps(hits, quiet=False):
  eff = 1.0
  state = create_state(hits)
  while True:
    new_eff = evaluate(state, utility_sustained_damage(eff))[0]
    if isclose(eff, new_eff): break
    eff = new_eff
  return display_tree(state, utility_sustained_damage(eff), quiet=quiet)

# Finally, tactical recommendations!

print "\nserge optimizing for damage > elemental charge, leaving 1 stamina free to cast"
display_tree(create_state(serge_base_hits, remaining_stamina=6),
             compose(utility_damage,
                     utility_elemental_power(cap=5)))
print "TL;DR: spam 2 unconditionally"

print "\nserge optimizing for dps"
sustained_dps(serge_base_hits)
print "TL;DR: 223, but abort if the first 2 misses."

print "\nkid optimizing for pilfer charge > steal chance > remaining_stamina > damage, leaving 1 stamina free to cast"
display_tree(create_state(kid_base_hits, remaining_stamina=6),
             compose(utility_elemental_power(cap=3),
                     utility_steal_chance,
                     utility_remaining_stamina,
                     utility_damage))
print "TL;DR: poke 1 until pilfer is charged up"

print "\nkid (already charged) optimizing for steal chance > remaining_stamina > damage, leaving 1 stamina free to cast"
display_tree(create_state(kid_base_hits, remaining_stamina=6),
             compose(utility_steal_chance,
                     utility_remaining_stamina,
                     utility_damage))
print "TL;DR: poke 1 until landing a single hit lands"

print "\nkid optimizing for damage > elemental charge, leaving 1 stamina free to cast"
display_tree(create_state(kid_base_hits, remaining_stamina=6),
             compose(utility_damage,
                     utility_elemental_power(cap=5)))
print "TL;DR: spam 2 unconditionally"

print "\nkid optimizing for dps"
sustained_dps(kid_base_hits)
print "TL;DR: 223, but abort if the first 2 misses"

print "\nglenn optimizing for damage > elemental charge, leaving 1 stamina free to cast"
display_tree(create_state(glenn_base_hits, remaining_stamina=6),
             compose(utility_damage,
                     utility_elemental_power(cap=5)))
print "TL;DR: spam 2 unconditionally"

print "\nglenn optimizing for dps"
sustained_dps(glenn_base_hits)
print "TL;DR: 223, but abort if the first 2 misses"


# print "\nlynx optimizing for damage vs a target with some evasion"
# display_tree(create_state(base_hits(
#     acc=85,
#     equip_acc=gear("silver swallow", ["silver loupe", "dragoon's honor"]),
#     evade=8)), utility_damage)
# print "TL;DR: 2...; if it hits, ...2 3; else, ...1 2 2"

print "\nradius optimizing for dps"
sustained_dps(base_hits(acc=90, equip_acc=gear("silver staff", ["silver loupe"])))
print "TL;DR: 2 (abort if miss) 2...; if both hit, 3; else, 2"

print "\nsearching for 2(hit)2(miss)X breakpoint"
sustained_dps((94, 81, 71))
print "TL;DR: X=2 until (_,82,72) initial, or (_,93,87) at decision time."

print "\nmax hit rate, optimizing for dps"
sustained_dps((99, 99, 99))
print "TL;DR: 33"

print "\nsearching for 223->33 dps breakpoint"
for hit in range(0,100):
  hits = base_hits(equip_acc=gear("silver staff", ["silver loupe"])+hit)
  score, opener = sustained_dps(hits, quiet=True)
  print '%s -> %s (%s)' % (hits, opener, score)
  if opener > 2: break
