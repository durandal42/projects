HEADER = ["Class", "Armor", "Tier", "Shields", "Bow/Xbow/Gun", "Wands",
          "Swords(2h)", "Axes(2h)", "Maces(2h)", "Polearms", "Fist",
          "Axes(1h)", "Staves", "Daggers", "Swords(1h)", "Maces(1h)"],

DATA = [
    ["Paladin", "Plate", "Conqueror", True, False, False, True,
     True, True, True, False, True, False, False, True, True],
    ["Mage", "Cloth", "Vanquisher", False, False, True, False,
        False, False, False, False, False, True, True, True, False],
    ["Priest",  "Cloth", "Conqueror", False, False, True, False,
        False, False, False, False, False, True, True, False, True],
    ["Death Knight", "Plate", "Vanquisher", False, False, False,
        True, True, True, True, False, True, False, False, True, True],
    ["Hunter", "Mail", "Protector", False, True, False, True,
        True, False, True, True, True, True, True, True, False],
    ["Druid", "Leather", "Vanquisher", False, False, False, False,
        False, True, True, True, False, True, True, False, True],
    ["Warlock", "Cloth", "Conqueror", False, False, True, False,
        False, False, False, False, False, True, True, True, False],
    ["Monk", "Leather", "Protector", False, False, False, False,
        False, False, True, True, True, True, False, True, True],
    ["Shaman", "Mail", "Protector", True, False, False, False,
        True, True, False, True, True, True, True, False, True],
    ["Rogue", "Leather", "Vanquisher", False, True, False, False,
        False, False, False, True, True, False, True, True, True],
    ["Warrior", "Plate", "Protector", True, True, False, True,
        True, True, True, True, True, True, True, True, True],
    ["Demon Hunter", "Leather", "Conqueror", False, False, False,
        False, False, False, False, True, True, False, True, True, False],
]

TEAM_SIZE = 4

# data.sort()


def make_teams(lineup):
  return zip(*[lineup[i::TEAM_SIZE] for i in range(TEAM_SIZE)])


def score(matchup):
  return 0 - sum(conflicts(team) for team in matchup)


def contention(i, needs):
  assert len(needs) == TEAM_SIZE
  counted_needs = collections.Counter(needs)
  result = 0
  for need, count in counted_needs.iteritems():
    if not need:
      continue  # it's okay for multiple team members *not* to need loot
    result += count - 1
  return result


def conflicts(team):
  return sum(contention(i, needs) for i, needs in enumerate(zip(*team)))

import itertools


def possible_matchups(data):
  options = []
  for batch in range(len(data) / TEAM_SIZE):
    options.append(1)
    for i in range(TEAM_SIZE - 1):
      options.append(len(data) - len(options))
    # TODO(durandal): solve teammate-ordering problem; this is inefficient for
    # TEAM_SIZE > 2

  for decisions in itertools.product(*[range(o) for o in options]):
    unused_indices = range(len(data))
    indices = []
    for d in decisions:
      indices.append(unused_indices.pop(d))
    assert len(unused_indices) == 0
    assert len(indices) == len(data)
    yield make_teams([data[i] for i in indices])


def summarize(matchup):
  return sorted([tuple(c[0] for c in sorted(p)) for p in matchup])


def find_best_matchups(data):
  best = None
  for matchup in possible_matchups(data):
    scored = (score(matchup), summarize(matchup))
    if (not best or scored[0] > best[0][0]):
      best = [scored]
      print "new best:", scored
    elif (scored[0] == best[0][0]):
      best.append(scored)
      print "tied for best:", scored
  return [scored[1] for scored in best]

import collections


def buddies(data):
  best_matchups = find_best_matchups(DATA)
  counters = dict((d[0], collections.Counter()) for d in data)
  for matchup in best_matchups:
    for team in matchup:
      for c1, c2 in itertools.combinations(team, 2):
        counters[c1][c2] += 1
        counters[c2][c1] += 1
  return counters

for c, common_buddy in buddies(DATA).iteritems():
  print "%s:\n\t%s" % (c, common_buddy)
