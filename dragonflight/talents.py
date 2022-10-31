import collections
import talent_data

def get_talents_by_name(talents):
  talents_by_name = {}
  for t in talents:
    talents_by_name[t.name] = t
  return talents_by_name

TALENTS = talent_data.get_talents("Paladin")

print("Loaded %d talents:" % len(TALENTS), TALENTS)
# print(get_talents_by_name(TALENTS))

def singularize_talent_name(name, i, max_points):
  return name + " (%d of %d)" % (i+1, max_points)

def singularize_talent_tree(talents):
  talents_by_name = get_talents_by_name(TALENTS)
  parents = collections.defaultdict(list)
  children = collections.defaultdict(list)
  for t1 in talents:
    for t2_name in t1.parents:
      parents[t1.name].append(t2_name)
      children[t2_name].append(t1.name)

  parent_corrections = {}
  talent_names_to_remove = set()
  talents_to_add = []
  for t in talents:
    if t.points > 1:
      talent_names_to_remove.add(t.name)
      parent_corrections[t.name] = singularize_talent_name(t.name, t.points-1, t.points)
      for i in range(t.points):
        name = singularize_talent_name(t.name, i, t.points)
        if i == 0:
          parents = t.parents
        else: 
          parents = [singularize_talent_name(t.name, i-1, t.points)]
        talents_to_add.append(talent_data.Talent(name=name, points=1, row=t.row+i/10, col=t.col, parents=parents))

  talents += talents_to_add

  new_talents = []
  for t in talents:
    if t.name in talent_names_to_remove: continue
    new_parents = []
    for p in t.parents:
      if p in parent_corrections:
        new_parents.append(parent_corrections[p])
      else:
        new_parents.append(p)
    new_talents.append(talent_data.Talent(name=t.name, points=t.points, row=t.row, col=t.col, parents=new_parents))

  return new_talents

TALENTS = singularize_talent_tree(TALENTS)

def data_validate_talents(talents):
  talents_by_name = get_talents_by_name(talents)
  for t1 in talents:
    if t1.points > 1:
      print("Didn't singularize talent:", t1)
      return False
    for t2_name in t1.parents:
      t2 = talents_by_name[t2_name]
      if not data_validate_dependency(t1, t2): return False
  return True

# Determine whether a dependency of t1 on t2 is valid.
def data_validate_dependency(t1, t2):
  if t1.row <= t2.row:
    print("Talent depends on another talent at the same or higher row:", t1, t2)
    return False
  return True

assert data_validate_talents(TALENTS)


LOADOUT = [
  "Lay on Hands",
  "Blessing of Freedom",
  "Hammer of Wrath",
  "Auras of the Resolute",
  "Auras of Swift Vengeance",
  "Divine Steed",
  "Fist of Justice (1 of 2)",
  "Fist of Justice (2 of 2)",
  "Cavalier",
  "Greater Judgment",
]

FREE_TALENTS = [
  "Lay on Hands",
  "Auras of the Resolute",
]

def validate_talent_loadout(talents, free_talents, loadout):
  if len(loadout) != len(set(loadout)):
    # TODO(dsloan): handle taking the same talent twice more cleanly
    return False
  talents_by_name = get_talents_by_name(talents)
  loadout = set(loadout)
  points_spent_by_tier = collections.defaultdict(int)

  for t1_name in loadout:
    t1 = talents_by_name[t1_name]

    # check that dependencies are satisfied:
    dependency_satisfied = False
    for t2_name in t1.parents:
      t2 = talents_by_name[t2_name]
      if t2_name in loadout:
        dependency_satisfied = True
    if len(t1.parents) > 0 and not dependency_satisfied:
      # print("Talent selected without fully selecting at least one dependency:", t1_name)
      return False

    if t1_name in free_talents:
      tier = 0
    else:
      tier = max(1, (t1.row + 2)//3)
    points_spent_by_tier[tier] += 1
    # TODO(dsloan): some points are free, depending on specialization

  # print(points_spent_by_tier)
  if points_spent_by_tier[2] > 0 and points_spent_by_tier[1] < 8:
    # print("Must spend 8 points on tier1 talents to unlock tier2 talents.")
    return False
  if points_spent_by_tier[3] > 0 and points_spent_by_tier[1]+points_spent_by_tier[2] < 20:
    # print("Must spend 20 points on tier1+tier2 talents to unlock tier3 talents.")
    return False

  # TODO(dsloan): check that total number of talent points spent is within budget

  return True

assert validate_talent_loadout(TALENTS, FREE_TALENTS, LOADOUT)

def choices(talents, free_talents, partial_loadout):
  partial_loadout = tuple(partial_loadout)
  return [t.name for t in talents
          if validate_talent_loadout(talents, free_talents, partial_loadout + (t.name,))]

print(choices(TALENTS, FREE_TALENTS, LOADOUT))

def valid_builds(talents, free_talents, points_to_spend, partial_loadout=None):
  assert points_to_spend >= 0

  if partial_loadout == None: partial_loadout = free_talents

  partial_loadouts = [tuple(sorted(partial_loadout))]

  while points_to_spend > 0:
    print("With %d points remaining, %d valid builds so far..." % (points_to_spend, len(partial_loadouts)))
    loadout_frontier = set()
    for partial_loadout in partial_loadouts:
      for t in choices(talents, free_talents, partial_loadout):
        loadout_frontier.add(tuple(sorted(partial_loadout + (t,))))
    points_to_spend -= 1
    partial_loadouts = loadout_frontier

  return list(loadout_frontier)

def exercise_valid_builds():
  vbs = valid_builds(TALENTS, FREE_TALENTS, 26)
  print("Found %d valid builds." % len(vbs))
  # for vb in vbs:
  #   print("\t", sorted_build(vb, get_talents_by_name(TALENTS)))

def sorted_build(b, talents_by_name):
  return sorted(b, key=lambda t: (talents_by_name[t].row, talents_by_name[t].col))

exercise_valid_builds()