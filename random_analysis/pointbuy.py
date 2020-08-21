from distribution import *

STANDARD_ARRAY = tuple(sorted([15, 14, 13, 12, 10, 8], reverse=True))

# Methods for generating a single independent ability score:


def stat_4d6_drop_lowest():
  return mktuple((die(6) for _ in range(4))).map(lambda t: sum(sorted(t)[1:]))

print "\nSingle ability score (4d6, drop lowest)", stat_4d6_drop_lowest()


# Methods for generating arrays of ability scores:


def stat_array(stat_generate_f):
  stats = [mktuple((stat_generate_f(),)) for _ in range(6)]
  return reduce(lambda x, y: x.combine(y, lambda a, b: tuple(sorted(a + b, reverse=True))), stats)


def array_4d6_drop_lowest():
  return stat_array(stat_4d6_drop_lowest)


# Methods for evaluating how good a stat (or stat array) is:
def stat_pointbuy_cost(s):
  # How many pointbuy points would it cost to buy this ability score?
  # Standard pointbuy:
  # - gives you an 8 for free
  # - charges 1 point for every increment up to 13
  # - charges 2 points for every increment up to 15
  # - cannot buy past 15
  # Generalized pointbuy lets you:
  # - recover 1 point by decrementing a score below 8
  # - continue spending 2 for increments past 15
  #   (an argument could be made that this should cost even more, being impossible by default)
  return s - 8 + max(0, s - 13)


def array_score(a, stat_score_f):
  return sum(stat_score_f(s) for s in a)


def array_pointbuy_cost(a):
  return array_score(a, stat_pointbuy_cost)


def array_utility(a):
  # For each stat, computes its bonus, and then values bonuses higher for
  # your more important stats.
  return sum((len(a) - v) * (s / 2 - 5) for v, s in enumerate(a))

print "Utility score of the standard array:\t", STANDARD_ARRAY, array_utility(STANDARD_ARRAY)


def summarize_nth_best(allocation):
  print "nth best stat:"
  for n in range(len(STANDARD_ARRAY)):
    print "%d: " % n
    nth_best = allocation.map(lambda a: a[n])
    summarize(nth_best)
  # print "utility:"
  # utility = allocation.map(array_utility)
  # print utility
  # print utility.cum()


a_4d6_drop_lowest = array_4d6_drop_lowest()
for description, allocation in [
    ("4d6 drop lowest", a_4d6_drop_lowest),
    # ("4d6 drop lowest, reroll if total < 70",
    #  a_4d6_drop_lowest.filter(lambda t: sum(t) >= 70)),
    # ("4d6 drop lowest, reroll if total < 70, reroll unless two 15+'s",
    #  a_4d6_drop_lowest.filter(lambda t: sum(
    #     t) >= 70).filter(lambda t: t[1] >= 15)),
    ("4d6 drop lowest, fall back to standard array",
     a_4d6_drop_lowest.map(lambda a: a if array_utility(a) >= array_utility(STANDARD_ARRAY) else STANDARD_ARRAY))
]:
  print
  print description
  print "pointbuy cost:"
  pointbuy_cost = allocation.map(array_pointbuy_cost)
  summarize(pointbuy_cost)
  # summarize_nth_best(allocation)
