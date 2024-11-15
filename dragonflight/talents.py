import talent_data
import talent_serialization
import whtrees
import numpy
import sys
import os
import pickle
import functools
import collections

def get_talents_by_name(talents):
  talents_by_name = {}
  for t in talents:
    talents_by_name[t.name] = t
    for name in t.name.split(" / "):
      talents_by_name[name] = t
  return talents_by_name


SingularTalent = collections.namedtuple(
    "SingularTalent", "name i parents tier")


def singularize_talent_name(name, i, max_points):
  return name + " (%d of %d)" % (i+1, max_points)


def singularize_talent_tree(talents):
  talents_by_name = get_talents_by_name(talents)
  parents = collections.defaultdict(list)
  children = collections.defaultdict(list)
  for t1 in talents:
    for t2_name in t1.parents:
      parents[t1.name].append(t2_name)
      children[t2_name].append(t1.name)

  parent_corrections = {}
  new_talents = []
  for t in talents:
    if t.points > 1:
      parent_corrections[t.name] = singularize_talent_name(
          t.name, t.points-1, t.points)
      for i in range(t.points):
        name = singularize_talent_name(t.name, i, t.points)
        if i == 0:
          parents = t.parents
        else:
          parents = [singularize_talent_name(t.name, i-1, t.points)]
        new_talents.append(SingularTalent(
            name=name, i=len(new_talents),
            parents=parents, 
            tier={0:1, 8:2, 20:3}[t.required_points]))
    else:
      new_talents.append(SingularTalent(
          name=t.name, i=len(new_talents),
          parents=t.parents,
          tier={0:1, 8:2, 20:3}[t.required_points]))

  corrected_parent_talents = []
  for t in new_talents:
    new_parents = []
    for p in t.parents:
      if p in parent_corrections:
        new_parents.append(parent_corrections[p])
      else:
        new_parents.append(p)
    corrected_parent_talents.append(t._replace(parents=new_parents))

  return corrected_parent_talents


def intify_talent_tree_parents(talents):
  talent_indices_by_name = {}
  for t in talents:
    talent_indices_by_name[t.name] = t.i
  for t in talents:
    new_parents = []
    for p in t.parents:
      new_parents.append(talent_indices_by_name[p])
    t.parents.clear()
    for p in new_parents:
      t.parents.append(p)


def data_validate_talents(talents):
  for i, t1 in enumerate(talents):
    assert t1.i == i
    for t2i in t1.parents:
      t2 = talents[t2i]
      if not data_validate_dependency(t1, t2):
        return False
  return True

# Determine whether a dependency of t1 on t2 is valid.


def data_validate_dependency(t1, t2):
  # if t1.row <= t2.row:
  #   print("Talent depends on another talent at the same or higher row:", t1, t2)
  #   return False
  if t1.i <= t2.i:
    print("Talent depends on a higher-indexed talent:", t1, t2)
    return False
  return True


def indices_to_bits(indices):
  result = 0
  for ti in indices:
    result |= (1 << ti)
  return result


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


def validate_talent_loadout(talents, free_talents_bits, loadout_bits,
                            new_talent_index=None):
  # print("Validating talent loadout:",
  #       loadout_bits_to_tuple(talents, loadout_bits))
  if new_talent_index is None:
    if not validate_point_thresholds(talents, free_talents_bits, loadout_bits):
      return False
  if not validate_dependencies(
          talents, free_talents_bits, loadout_bits, new_talent_index):
    return False
  return True


def count_spent_points(talents, free_talents_bits, loadout_bits):
  points_spent_by_tier = collections.defaultdict(int)

  for t1_i in set_bit_indices(loadout_bits):
    if (1 << t1_i) & free_talents_bits > 0:
      tier = 0
    else:
      tier = talents[t1_i].tier
    points_spent_by_tier[tier] += 1

  return points_spent_by_tier


def validate_point_thresholds(talents, free_talents_bits, loadout_bits):
  points_spent_by_tier = count_spent_points(
      talents, free_talents_bits, loadout_bits)
  # print(points_spent_by_tier)
  if points_spent_by_tier[2] > 0 and points_spent_by_tier[1] < 8:
    # print("Must spend 8 points on tier1 talents to unlock tier2 talents.")
    return False
  if (points_spent_by_tier[3] > 0 and
          points_spent_by_tier[1]+points_spent_by_tier[2] < 20):
    # print("Must spend 20 points on tier1+tier2 talents to unlock tier3 talents.")
    return False

  # TODO(dsloan): check that number of talent points spent is within budget
  return True


def validate_dependencies(
        talents, free_talents_bits, loadout_bits, new_talent_index=None):
  if new_talent_index is not None:
    return validate_dependency(talents[new_talent_index], loadout_bits)
  else:
    for t1_i in set_bit_indices(loadout_bits):
      if not validate_dependency(talents[t1_i], loadout_bits):
        return False
    return True


def validate_dependency(t1, loadout_bits):
  if not t1.parents:
    return True
  for t2_i in t1.parents:
    if (1 << t2_i) & loadout_bits:
      return True
  # print("Talent selected without fully selecting at least one dependency: %s" % (t1.name))
  return False


def choices(
        talents, free_talents_bits, partial_loadout_bits,
        enforce_choice_ordering=False):
  # print("Generating options for partial loadout:", bin(partial_loadout_bits), loadout_bits_to_tuple(talents, partial_loadout_bits))
  points_spent_by_tier = count_spent_points(
      talents, free_talents_bits, partial_loadout_bits)
  tier_permitted = {
      1: True,
      2: points_spent_by_tier[1] >= 8,
      3: points_spent_by_tier[1]+points_spent_by_tier[2] >= 20,
  }
  highest_index_spent_point = (
      partial_loadout_bits & ~free_talents_bits).bit_length()
  # print("Bit length of current loadout:", partial_loadout_bits.bit_length())
  return [i for i in range(len(talents))
          if True
          and (1 << i) & partial_loadout_bits == 0
          and (not enforce_choice_ordering or i >= highest_index_spent_point)
          and tier_permitted[talents[i].tier]
          and validate_talent_loadout(
      talents, free_talents_bits, partial_loadout_bits | (1 << i),
      new_talent_index=i)
  ]


def valid_builds(talents, free_talents_bits, points_to_spend):
  assert points_to_spend >= 0

  partial_loadouts_bits = [free_talents_bits]

  while points_to_spend > 0:
    print("With %d points remaining, %d valid builds so far..." %
          (points_to_spend, len(partial_loadouts_bits)))
    # print("valid builds:", [bin(plb) for plb in partial_loadouts_bits])
    # if points_to_spend < 15: return list(loadout_frontier)
    loadout_frontier = set()
    for partial_loadout_bits in partial_loadouts_bits:
      for t in choices(
              talents, free_talents_bits, partial_loadout_bits,
              enforce_choice_ordering=True):
        loadout_frontier.add(partial_loadout_bits | (1 << t))
    points_to_spend -= 1
    partial_loadouts_bits = loadout_frontier

  return list(loadout_frontier)


def filter_builds(builds, required_talent_bits):
  return builds[builds & required_talent_bits == required_talent_bits]
  # return list(filter(lambda b: b & required_talent_bits == required_talent_bits,
  #                    builds))


def format_talent_index(talents, i):
  return "[%s] %s" % ('{:2d}'.format(i), talents[i].name)

import numpy

def count_talent_appearances(talents, builds):
  return list(map(lambda t: numpy.count_nonzero(builds & (1<<t)),
                  talents))

def show_common_talents(builds, talents):
  print("In %d valid builds..." % len(builds))
  all_talents = range(len(talents))
  talent_appearances = count_talent_appearances(all_talents, builds)

  required_talents = list(
      filter(lambda t: talent_appearances[t] == len(builds), all_talents))
  unreachable_talents = list(
      filter(lambda t: talent_appearances[t] == 0, all_talents))
  selectable_talents = sorted(filter(
      lambda tc: tc[1] > 0 and tc[1] < len(builds),
      zip(all_talents, talent_appearances)),
      key=lambda tc: -tc[1])

  return (
      selectable_talents,
      indices_to_bits(required_talents),
      indices_to_bits(unreachable_talents),
  )


def interactive_filter(all_builds, talents, initial_filter=0):
  builds = filter_builds(all_builds, initial_filter)
  # TODO(dsloan): undo button / remove talent
  selectable, required, unreachable = [], 0, 0
  while True:
    now_selectable, now_required, now_unreachable = show_common_talents(
        builds, talents)

    print("Required talent(s):")
    print("\n".join("%s\t%s" % ((1<<i)&required and " " or "*",
                                format_talent_index(talents, i))
                    for i in range(len(talents))
                    if (1<<i) & now_required))
    required = now_required

    if unreachable is not None and unreachable != now_unreachable:
      print("Newly unreachable talent(s):")
      print("\n".join("\t%s" % format_talent_index(talents, i)
                      for i in set_bit_indices(now_unreachable & ~unreachable)))
    unreachable = now_unreachable

    if not now_selectable:
      print("No further talents can be spent.")
    else:
      print("Selectable talents, sorted by appearance rate:")
      print("\n".join("\t%s:\t%s" % ('{:10d}'.format(c),
                                     format_talent_index(talents, ti))
                      for ti, c in now_selectable))
    selectable = now_selectable

    print("Pick talent(s) to include (or prefix with - to remove)(hit enter to break and print export string): ")
    user_input = sys.stdin.readline().strip()
    if user_input == "": return now_required
    exclude = False
    if user_input[0] == '-':
      exclude = True
      user_input = user_input[1:]

    talent_indices = [
        int(s.strip())
        for s in user_input.split(',')]
    talent_bits = indices_to_bits(talent_indices)

    if exclude:
      builds = filter_builds(all_builds, now_required & ~talent_bits)
      selectable, required, unreachable = [], 0, 0
    else:
      builds = filter_builds(builds, talent_bits)

    if not builds:
      print("No valid builds remain.")
      return

def export_string(talents, spec_name, loadout_bits):
  talent_names = [t.name for t in talents if (1<<t.i) & loadout_bits]
  tree_id = whtrees.TREE_IDS_BY_NAME[spec_name]
  return talent_serialization.generate_blizzard_import_string(
    talent_serialization.serialize_talent_names(talent_names, tree_id), tree_id)

def session(arg):
  if arg in whtrees.TREE_IDS_BY_NAME:
    tree_name = arg
    initial_talent_names = []
  else:
    sts, spec_id = talent_serialization.parse_blizzard_import_string(arg)
    tree_name = whtrees.TREE_NAMES_BY_ID[spec_id]
    initial_talent_names = talent_serialization.get_selected_talent_names(sts, spec_id)

  talents = talent_data.get_talents(tree_name)
  print("Loaded %d talents:" % len(talents))
  print("\n".join("\t" + t.name for t in talents))

  talents = singularize_talent_tree(talents)
  print("Singularized talents into %d distinct nodes." % len(talents))
  print("\n".join("\t" + t.name for t in talents))

  intify_talent_tree_parents(talents)
  print("Intified talent tree parents:")
  print("\n".join("\t[%d] %s: %s" % (i, t.name, t.parents)
                  for (i, t) in enumerate(talents)))

  assert data_validate_talents(talents)

  print("Import string has %d talents selected." % len(initial_talent_names))
  print(initial_talent_names)
  talents_by_name = get_talents_by_name(talents)
  initial_talent_indices = [talents_by_name[name].i for name in initial_talent_names
                            if name in talents_by_name]
  print("Import string has %d talents selected in this tree." % len(initial_talent_indices))
  initial_talent_loadout = indices_to_bits(initial_talent_indices)

  points_to_spend = 25

  builds_pickle_file = ('pickled_builds/%s-%d.pickle'
                        % (tree_name.lower().replace(" ", ""), points_to_spend))

  if os.path.exists(builds_pickle_file):
    print("Loading pickled builds...")
    builds = pickle.load(open(builds_pickle_file, "rb"))
  else:
    builds = valid_builds(talents,
                          free_talents_bits=0,  # TODO(dsloan): get this from the tree
                          points_to_spend=points_to_spend)
    print("Pickling builds...")
    pickle.dump(builds, open(builds_pickle_file, "wb"))
  print("Found %d valid builds." % len(builds))

  build = interactive_filter(numpy.array(builds), talents, initial_talent_loadout)

  print("Export string:")
  print("\t", export_string(talents, tree_name, build))


def main():
  if len(sys.argv) == 2:
    session(sys.argv[1])
  else:
    session("Paladin-Holy")


if __name__ == '__main__':
  import cProfile
  import pstats
  pr = cProfile.Profile()
  pr.enable()

  main()

  pr.disable()
  stats = pstats.Stats(pr)
  stats.sort_stats('tottime').print_stats(20)
