from distribution import *
from functools import reduce

STANDARD_ARRAY = tuple(sorted([15, 14, 13, 12, 10, 8], reverse=True))

# Methods for generating a single independent ability score:


def stat_1d20():
  return die(20)


def stat_3d6():
  return dice(3, 6)


def stat_4d6_drop_lowest():
  return cartesian_product((die(6) for _ in range(4))).map(lambda t: sum(sorted(t)[1:]))


# Methods for generating arrays of ability scores:

def stat_array_standard():
  return constant(STANDARD_ARRAY)


def stat_array(stat_generate_f, sort=True):
  stats = [cartesian_product((stat_generate_f(),)) for _ in range(6)]
  if sort:
    def combine_op(a, b): return tuple(sorted(a + b, reverse=True))
  else:
    def combine_op(a, b): return a + b
  return reduce(lambda x, y: x.combine(y, combine_op), stats)


def stat_array_3up3down():
  return cartesian_product([die(6), die(8), die(10)]).map(lambda d: tuple(sorted([
      10 + d[0], 15 - d[0], 10 + d[1], 15 - d[1], 8 + d[2], 17 - d[2]])))


def stat_array_pool(d6s):
  assert len(d6s) == 18
  result = tuple([sum(d6s[0:3]),
                  sum(d6s[3:6]),
                  sum(d6s[6:9]),
                  sum(d6s[9:12]),
                  sum(d6s[12:15]),
                  sum(d6s[15:18])])
  assert sum(result) == sum(d6s)
  return result


def stat_array_24d6_drop_lowest6_pool():
  result = constant(())
  for _ in range(24 - 6):
    result = (result + cartesian_product([die(6)])).map(lambda a: tuple(sorted(a)))
    print("working on expensive distribution 24d6 drop lowest 6:",
          _, len(result._dist), result.max())
    # print result
  for _ in range(6):
    result = (result + cartesian_product([die(6)])
              ).map(lambda a: tuple(sorted(a)[6 - 24:]))
    print("working on expensive distribution 24d6 drop lowest 6:",
          _ + 24 - 6, len(result._dist), result.max())
    # print result
  return result.map(stat_array_pool)

# Methods for evaluating how good a stat (or stat array) is:


def stat_pointbuy_cost(s):
  # How many pointbuy points would it cost to buy this ability score?
  # Standard pointbuy:
  # - gives you an 8 for free
  # - charges 1 point for every increment up to 13
  # - charges 2 points for every increment up to 15
  # - cannot buy past 15
  # Generalized pointbuy additionally:
  # - recovers 1 point for every decrement below 8
  # - charges 3 points for every increment up to 17
  # - charges 4 points for every increment up to 19
  return s - 8 + max(0, s - 13) + max(0, s - 15) + max(0, s - 17)


def array_score(a, stat_score_f):
  return sum(stat_score_f(s) for s in a)


def array_pointbuy_cost(a):
  return array_score(a, stat_pointbuy_cost)


def array_utility(a):
  # More important stats are more valuable.
  return sum((len(a) - v) * (s - 10) for v, s in enumerate(a))


def summarize_nth_best(allocation):
  print("nth best stat:")
  for n in range(len(STANDARD_ARRAY)):
    print("%d: " % n)
    nth_best = allocation.map(lambda a: a[n])
    summarize(nth_best)
  # print "utility:"
  # utility = allocation.map(array_utility)
  # print utility
  # print utility.cum()


def summarize_party_spread(dist):
  dist_min = dist
  dist_max = dist
  party_size = 8
  for _ in range(party_size - 1):
    dist_min = dist_min.combine(dist, min)
    dist_max = dist_max.combine(dist, max)

  print(f"In a party of size {party_size}...")
  print("Weakest member:")
  summarize(dist_min)
  print("Strongest member:")
  summarize(dist_max)
  dist_spread = dist_max - dist_min
  print("Spread between weakest and strongest:")
  summarize(dist_spread)


if __name__ == "__main__":
  # execute only if run as a script

  print("Single ability score (4d6, drop lowest)")
  summarize(stat_4d6_drop_lowest())
  print()

  print("Utility score of the standard array %s: %d" %
        (STANDARD_ARRAY, array_utility(STANDARD_ARRAY)))
  print()

  print("pointbuy-legal arrays:")
  pointbuy_legal = (stat_array(lambda: die(8) + 7)
                    .filter(lambda a: array_pointbuy_cost(a) == 27))
  print(pointbuy_legal)
  print("utility distribution of pointbuy-legal arrays:")
  summarize(pointbuy_legal.map(array_utility))
  print()

  print("highest-utility pointbuy-legal array:")
  print(max((array_utility(x), x) for x, p in pointbuy_legal.items()))

  a_4d6_drop_lowest = stat_array(stat_4d6_drop_lowest)
  for description, allocation in [
      ("standard array", stat_array_standard()),
      # ("1d20", stat_array(stat_1d20)),
      # ("3d6", stat_array(stat_3d6)),
      ("4d6 drop lowest", a_4d6_drop_lowest),
      # ("4d6 drop lowest, reroll if total < 70",
      #  a_4d6_drop_lowest.filter(lambda t: sum(t) >= 70)),
       ("4d6 drop lowest, reroll if total < 70, reroll unless two 15+'s",
        a_4d6_drop_lowest.filter(lambda t: sum(
           t) >= 70).filter(lambda t: t[1] >= 15)),
      # ("4d6 drop lowest, fall back to standard array",
      # a_4d6_drop_lowest.map(lambda a: a if array_utility(a) >=
      # array_utility(STANDARD_ARRAY) else STANDARD_ARRAY))
      # ("4d6 drop lowest, raise best stat to 16, raise all stats to 10, +2 free points", a_4d6_drop_lowest.map(
      # lambda a: tuple([max(16, a[0]) + 2, max(10, a[1]), max(10, a[2]),
      # max(10, a[3]), max(10, a[4]), max(10, a[5])])))
      # ("3 up 3 down: 10 + d6, 15 - same d6, 10 + d8, 15 - same d8, 8 + d10, 17 - same d10",
      #  stat_array_3up3down()),
      # ("24d6 drop lowest 6, allocate in groups of 3",
      # stat_array_24d6_drop_lowest6_pool())
  ]:
    print()
    print(description)
    print("pointbuy cost:")
    pointbuy_cost = allocation.map(array_pointbuy_cost)
    summarize(pointbuy_cost)

    # print("pointbuy cost (cumulative):")
    # print(pointbuy_cost.cum())
    # summarize_nth_best(allocation)

    print("utility:")
    summarize(allocation.map(array_utility))
