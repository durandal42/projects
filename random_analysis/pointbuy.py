from distribution import *

STANDARD_ARRAY = tuple(sorted([15, 14, 13, 12, 10, 8]))


def stat_4d6_drop_lowest():
  return mktuple((die(6) for _ in range(4))).map(lambda t: sum(sorted(t)[1:]))

print "\nSingle ability score (4d6, drop lowest)", stat_4d6_drop_lowest()


def stat_array_4d6_drop_lowest():
  stats = [mktuple((stat_4d6_drop_lowest(),)) for _ in range(6)]
#  return stats[0].combine(stats[1], lambda x,y: tuple(sorted(x+y)))
  return reduce(lambda x, y: x.combine(y, lambda a, b: tuple(sorted(a + b))), stats)


def stat_pointbuy_cost(s):
  return s - 8 + max(0, s - 13)


def array_pointbuy_cost(a):
  return sum(stat_pointbuy_cost(s) for s in a)


def array_utility(a):
  return sum(v * (s / 2 - 5) for v, s in zip(range(len(a)), a))

print "Utility score of the standard array:\t", STANDARD_ARRAY, array_utility(STANDARD_ARRAY)
print "\nstat array pointbuy cost (4d6 drop lowest):"
standard_allocation = stat_array_4d6_drop_lowest()
for allocation in [
    standard_allocation,
    standard_allocation.filter(lambda t: sum(t) >= 70),
    # standard_allocation.filter(lambda t: sum(
    #     t) >= 70).filter(lambda t: t[-2] >= 15),
]:
  print "pointbuy cost:"
  pointbuy_cost = allocation.map(array_pointbuy_cost)
  summarize(pointbuy_cost)
  # print pointbuy_cost.cum()
  print "nth best stat:"
  for n in range(1, 1 + len(STANDARD_ARRAY)):
    print "%d: " % n
    nth_best = allocation.map(lambda a: a[-n])
    summarize(nth_best)
  # print "utility:"
  # utility = allocation.map(array_utility)
  # print utility
  # print utility.cum()
