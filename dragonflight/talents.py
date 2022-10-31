import collections
import functools
import pickle
import os
import sys

import talent_data

def get_talents_by_name(talents):
  talents_by_name = {}
  for t in talents:
    talents_by_name[t.name] = t
  return talents_by_name

TALENTS = talent_data.get_talents("Paladin")

print("Loaded %d talents:" % len(TALENTS))
print("\n".join("\t" + t.name for t in TALENTS))

SingularTalent = collections.namedtuple("SingularTalent", "name parents row col tier")

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
  new_talents = []
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
        new_talents.append(SingularTalent(name=name, parents=parents, row=t.row+i/10, col=t.col, tier=max(1, (t.row + 2)//3)))
    else:
      new_talents.append(SingularTalent(name=t.name, parents=t.parents, row=t.row, col=t.col, tier=max(1, (t.row + 2)//3)))

  talents = new_talents

  new_talents = []
  for t in talents:
    if t.name in talent_names_to_remove: continue
    new_parents = []
    for p in t.parents:
      if p in parent_corrections:
        new_parents.append(parent_corrections[p])
      else:
        new_parents.append(p)
    new_talents.append(t._replace(parents=new_parents))

  return sorted(new_talents, key=lambda t: (t.row, t.col))
  

TALENTS = singularize_talent_tree(TALENTS)
print("Singularized talents into %d distinct nodes." % len(TALENTS))
print("\n".join("\t" + t.name for t in TALENTS))

def get_talent_indices_by_name(talents):
  result = {}
  for t in talents:
    result[t.name] = len(result)
  return result

TALENT_INDICES_BY_NAME = get_talent_indices_by_name(TALENTS)


def data_validate_talents(talents):
  talents_by_name = get_talents_by_name(talents)
  for t1 in talents:
    for t2_name in t1.parents:
      t2 = talents_by_name[t2_name]
      if not data_validate_dependency(t1, t2): return False
  return True

# Determine whether a dependency of t1 on t2 is valid.
def data_validate_dependency(t1, t2):
  if t1.row <= t2.row:
    print("Talent depends on another talent at the same or higher row:", t1, t2)
    return False
  if TALENT_INDICES_BY_NAME[t1.name] <= TALENT_INDICES_BY_NAME[t2.name]:
    print("Talent depends on another talent which appears later in the talent list:", t1, t2)
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

def intify_talent_tree_parents(talents):
  talent_indices_by_name = get_talent_indices_by_name(TALENTS)
  for t in talents:
    new_parents = []
    for p in t.parents:
      new_parents.append(talent_indices_by_name[p])
    t.parents.clear()
    for p in new_parents:
      t.parents.append(p)

intify_talent_tree_parents(TALENTS)
print("Intified talent tree, with parents:")
print("\n".join("\t[%d] %s: %s" % (i, t.name, t.parents) for (i,t) in enumerate(TALENTS)))

def loadout_tuple_to_bits(talent_indices_by_name, loadout_tuple):
  result = 0
  for t_name in loadout_tuple:
    result |= (1 << talent_indices_by_name[t_name])
  return result

# cribbed from https://stackoverflow.com/questions/8898807/pythonic-way-to-iterate-over-bits-of-integer
# and https://stackoverflow.com/questions/40608220/pythonic-way-to-count-the-number-of-trailing-zeros-in-base-2
def set_bit_indices(n):
  while n:
    b = n & (~n+1)
    yield b.bit_length() - 1
    n ^= b

def loadout_bits_to_tuple(talents, loadout_bits):
  result = []
  for i in set_bit_indices(loadout_bits):
    result.append(talents[i].name)
  return tuple(result)

def roundtrip_loadout_through_bits(loadout_list):
  print("Testing roundtrip bitstring conversion...")
  loadout_tuple = tuple(loadout_list)
  print("\tOriginal loadout tuple:", loadout_tuple)
  loadout_bits = loadout_tuple_to_bits(get_talent_indices_by_name(TALENTS), loadout_tuple)
  print("\tBitstring of test loadout:", bin(loadout_bits))
  print("\tSet indices in bitset:", list(set_bit_indices(loadout_bits)))
  loadout_tuple_again = loadout_bits_to_tuple(TALENTS, loadout_bits)
  print("\tTest loadout back from the shadowland of bits:", loadout_tuple_again)
  assert loadout_tuple_again == loadout_tuple

roundtrip_loadout_through_bits(LOADOUT)

LOADOUT_BITS = loadout_tuple_to_bits(get_talent_indices_by_name(TALENTS), LOADOUT)
FREE_TALENTS_BITS = loadout_tuple_to_bits(get_talent_indices_by_name(TALENTS), FREE_TALENTS)

def validate_talent_loadout(talents, free_talents_bits, loadout_bits, new_talent_index=None):
  # print("Validating talent loadout:", loadout_bits_to_tuple(talents, loadout_bits))
  if new_talent_index is None and not validate_point_thresholds(talents, free_talents_bits, loadout_bits): return False
  if not validate_dependencies(talents, free_talents_bits, loadout_bits, new_talent_index): return False
  return True

def count_spent_points(talents, free_talents_bits, loadout_bits):
  points_spent_by_tier = collections.defaultdict(int)

  for t1_i in set_bit_indices(loadout_bits):
    if (1<<t1_i) & free_talents_bits > 0:
      tier = 0
    else:
      tier = talents[t1_i].tier
    points_spent_by_tier[tier] += 1

  return points_spent_by_tier

def validate_point_thresholds(talents, free_talents_bits, loadout_bits):
  points_spent_by_tier = count_spent_points(talents, free_talents_bits, loadout_bits)
  # print(points_spent_by_tier)
  if points_spent_by_tier[2] > 0 and points_spent_by_tier[1] < 8:
    # print("Must spend 8 points on tier1 talents to unlock tier2 talents.")
    return False
  if points_spent_by_tier[3] > 0 and points_spent_by_tier[1]+points_spent_by_tier[2] < 20:
    # print("Must spend 20 points on tier1+tier2 talents to unlock tier3 talents.")
    return False
  # TODO(dsloan): check that total number of talent points spent is within budget
  return True

def validate_dependencies(talents, free_talents_bits, loadout_bits, new_talent_index=None):
  if new_talent_index is not None:
    return validate_dependency(talents[new_talent_index], loadout_bits)
  else:
    for t1_i in set_bit_indices(loadout_bits):
      if not validate_dependency(talents[t1_i], loadout_bits):
        return False
    return True

def validate_dependency(t1, loadout_bits):
  if not t1.parents: return True
  for t2_i in t1.parents:
    if (1<<t2_i) & loadout_bits:
      return True
  # print("Talent selected without fully selecting at least one dependency: %s" % (t1.name))
  return False

assert validate_talent_loadout(TALENTS, FREE_TALENTS_BITS, LOADOUT_BITS)

def choices(talents, free_talents_bits, partial_loadout_bits, enforce_choice_ordering=False):
  # print("Generating options for partial loadout:", bin(partial_loadout_bits), loadout_bits_to_tuple(talents, partial_loadout_bits))
  points_spent_by_tier = count_spent_points(talents, free_talents_bits, partial_loadout_bits)
  tier_permitted = {
    1: True,
    2: points_spent_by_tier[1] >= 8,
    3: points_spent_by_tier[1]+points_spent_by_tier[2] >= 20,
  }
  spent_points_bits = partial_loadout_bits & ~free_talents_bits
  # print("Bit length of current loadout:", partial_loadout_bits.bit_length())
  return [i for i in range(len(talents))
          if True 
             and (1<<i) & partial_loadout_bits == 0
             and (not enforce_choice_ordering or i >= spent_points_bits.bit_length())
             and tier_permitted[talents[i].tier]
             and validate_talent_loadout(talents, free_talents_bits, partial_loadout_bits | (1<<i), new_talent_index=i)]

print(list(map(lambda i: TALENTS[i].name, choices(TALENTS, FREE_TALENTS_BITS, LOADOUT_BITS))))

def valid_builds(talents, free_talents_bits, points_to_spend, partial_loadout_bits=0):
  assert points_to_spend >= 0

  if partial_loadout_bits == 0:
    print("no partial loadout provided; giving you only the free talents:", bin(free_talents_bits))
    partial_loadout_bits = free_talents_bits

  partial_loadouts_bits = [partial_loadout_bits]

  while points_to_spend > 0:
    print("With %d points remaining, %d valid builds so far..." % (points_to_spend, len(partial_loadouts_bits)))
    # print("valid builds:", [bin(plb) for plb in partial_loadouts_bits])
    # if points_to_spend < 15: return list(loadout_frontier)
    loadout_frontier = set()
    for partial_loadout_bits in partial_loadouts_bits:
      for t in choices(talents, free_talents_bits, partial_loadout_bits, enforce_choice_ordering=True):
        loadout_frontier.add(partial_loadout_bits | (1<<t))
    points_to_spend -= 1
    partial_loadouts_bits = loadout_frontier

  return list(loadout_frontier)

def exercise_valid_builds(points_to_spend):
  vbs = valid_builds(TALENTS, FREE_TALENTS_BITS, points_to_spend)
  # for vb in vbs:
  #   print("\t", sorted_build(loadout_bits_to_tuple(TALENTS, vb), get_talents_by_name(TALENTS)))
  return vbs

def sorted_build(b, talents_by_name):
  return sorted(b, key=lambda t: (talents_by_name[t].row, talents_by_name[t].col))

def filter_builds(builds, required_talent_bits):
  return list(filter(lambda b: b & required_talent_bits == required_talent_bits,
                     builds))

def format_talent_index(i):
  return "[%s] %s" % ('{:2d}'.format(i), TALENTS[i].name)
  
def index_list_to_bits(indices):
  bits = 0
  for i in indices:
    bits |= 1 << i
  return bits

def show_common_talents(builds):
  print("In %d valid builds..." % len(builds))
  all_talents = range(len(TALENTS))
  talent_appearances = [0] * len(TALENTS)

  for ti in all_talents:
    t_bit = 1 << ti
    for b in builds:
      if b & t_bit > 0:
        talent_appearances[ti] += 1
  #  for b in builds:
  #    for ti in set_bit_indices(b):
  #      talent_appearances[ti] += 1
  
  required_talents = list(filter(lambda t: talent_appearances[t] == len(builds), all_talents))
  unreachable_talents = list(filter(lambda t: talent_appearances[t] == 0, all_talents))
  selectable_talents = list(filter(lambda t: talent_appearances[t] > 0 and talent_appearances[t] < len(builds), all_talents))

  selectable_talents.sort(key=lambda ti: talent_appearances[ti], reverse=True)
  #  print("Unreachable talents:")
  #  print("\n".join("\t%s" % format_talent_index(i) for i in unreachable_talents))
  #  print("Required talents:")
  #  print("\n".join("\t%s" % format_talent_index(i) for i in required_talents))
  print("Selectable talents, sorted by appearance rate:")
  print("\n".join("\t%s:\t%s" % ('{:5d}'.format(talent_appearances[i]),format_talent_index(i))
                  for i in selectable_talents))
  return (
    index_list_to_bits(selectable_talents),
    index_list_to_bits(required_talents),
    index_list_to_bits(unreachable_talents),
  )

def interactive_filter(builds):
  selectable, required, unreachable = None, None, None
  while len(builds) > 1:
    now_selectable, now_required, now_unreachable = show_common_talents(builds)
    return
    if selectable is not None and selectable != now_selectable:
      pass
    if required is not None and required != now_required:
      print("Newly required talent(s):")
      print("\n".join("\t%s" % format_talent_index(i)
                      for i in set_bit_indices(now_required & ~required)))
    if unreachable is not None and unreachable != now_unreachable:
      print("Newly unreachable talent(s):")
      print("\n".join("\t%s" % format_talent_index(i)
                      for i in set_bit_indices(now_unreachable & ~unreachable)))
    selectable, required, unreachable = now_selectable, now_required, now_unreachable
    print("Pick mandatory talent(s): ")
    mandatory_talents_indices = [int(s.strip()) for s in sys.stdin.readline().strip().split(',')]
    builds = filter_builds(builds, index_list_to_bits(mandatory_talents_indices))
  if not builds:
    print("No valid builds remain.")
  else:
    print("One remaining build:", bin(builds[0]))
  
def main():
  points_to_spend = 26
  
  builds_pickle_file = 'pickled_builds/paladin-protection-generic-%d.pickle' % points_to_spend
  if os.path.exists(builds_pickle_file):
    print("Loading pickled builds...")
    builds = pickle.load(open(builds_pickle_file, "rb"))
  else:
    builds = exercise_valid_builds(points_to_spend)
    print("Pickling builds...")
    pickle.dump(builds, open(builds_pickle_file, "wb"))
  print("Found %d valid builds." % len(builds))

  interactive_filter(builds)

if __name__ == '__main__':
  import cProfile
  cProfile.run('main()')
