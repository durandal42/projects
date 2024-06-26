import fractions
import collections
import operator
import math
import functools


class Distribution:

  def __init__(self, dist=None):
    if dist is None:
      self._dist = collections.defaultdict(fractions.Fraction)
    else:
      self._dist = dist

  def __repr__(self):
    if not self._dist:
      return "Distribution()"
    return "Distribution(\n\t%s\n)" % (",\n\t".join(
        "%s:\t%s" % item for item in self._dist.items()))

  HISTOGRAM_WIDTH = 50

  def __str__(self, max_p=None):
    if not self._dist:
      return "Distribution()"
    if max_p is None:
      max_p = max(self._dist.values())
    return "Distribution(\n\t%s\n)" % ("\n\t".join(
        "%s:\t%0.4f - [%s]" % (x, px, "*" *
                               int(Distribution.HISTOGRAM_WIDTH * px / max_p))
        for x, px in sorted(self._dist.items())))

  def __len__(self):
    return len(self._dist)

  def weight(self):
    return float(sum(v.denominator for k, v in self._dist.items()))

  def equivalent(left, right):
    if isinstance(left, Distribution):
      left = left._dist
    if isinstance(right, Distribution):
      right = right._dist
    if isinstance(left, dict) and isinstance(right, dict):
      keys = set(left.keys()) | set(right.keys())
      for x in keys:
        if not left.get(x, 0) == right.get(x, 0):
          return False
      return True
    return False

  def combine(self, other, operator):
    result = collections.defaultdict(fractions.Fraction)
    if isinstance(other, self.__class__):
      # print(f'combining distributions of sizes {len(self)} * {len(other)},
      # with max weight {max(self.weight(), other.weight())}...')
      for x, px in self._dist.items():
        for y, py in other._dist.items():
          result[operator(x, y)] += px * py
    else:
      # print(f'combining distribution of size {len(self)} with a constant...')
      for x, px in self._dist.items():
        result[operator(x, other)] += px
    return self.__class__(result)

  def map(self, operator):
    # print "mapping:", self, operator
    result = collections.defaultdict(fractions.Fraction)
    for x, px in self._dist.items():
      mapped = operator(x)
      # print 'mapped:', mapped
      if isinstance(mapped, self.__class__):
        for y, py in mapped._dist.items():
          result[y] += px * py
      else:
        result[mapped] += px
    # print 'map complete:', result
    return self.__class__(result)

  def ev(self):
    try:
      return sum(x * px for x, px in self._dist.items())
    except TypeError:
      return functools.reduce(
          lambda t1, t2: tuple(map(sum, zip(t1, t2))),
          (tuple(x * px for x in t) for t, px in self._dist.items()))

  def stddev(self):
    mean = self.ev()
    return math.sqrt(sum(px * (x - mean)**2 for x, px in self._dist.items()))

  def cum(self):
    cp = 0
    result = {}
    for x, px in sorted(self._dist.items()):
      cp += px
      result[x] = cp
    return self.__class__(result)

  def atmost(self, v):
    c = self.cum()
    if v in c._dist:
      return c._dist[v]
    else:
      assert False  # TODO: find next-highest element

  def atleast(self, v):
    c = self.cum()
    if v in c._dist:
      return 1 - c._dist[v] + self._dist[v]
    else:
      return False

  def choice(self, p):
    cp = 0
    for x, px in sorted(self._dist.items()):
      cp += px
      if cp > p:
        return x
    assert False

  def filter(self, predicate):
    cp = 0
    result = {}
    for x, px in self._dist.items():
      if predicate(x):
        cp += px
        result[x] = px
    for x, px in result.items():
      result[x] = px / cp
    return self.__class__(result)

  def __add__(self, other):
    return self.combine(other, operator.__add__)

  def __radd__(self, other):
    return self + other

  def __sub__(self, other):
    return self.combine(other, operator.__sub__)

  def __rsub__(self, other):
    return self.combine(other, lambda x, y: y - x)

  def __mul__(self, other):
    return self.combine(other, operator.__mul__)

  def __rmul__(self, other):
    return self + other

  def __eq__(self, other):
    return self.combine(other, operator.__eq__)

  def __lt__(self, other):
    return self.combine(other, operator.__lt__)

  def __le__(self, other):
    return self.combine(other, operator.__le__)

  def __gt__(self, other):
    return self.combine(other, operator.__gt__)

  def __ge__(self, other):
    return self.combine(other, operator.__ge__)

  def __nonzero__(self):
    for x, px in self._dist.items():
      if not x:
        return False
    return True

  def items(self):
    return self._dist.items()

  def max(self):
    p, x = max((p, x) for x, p in self.items())
    return (x, p)


def constant(x):
  return Distribution({x: 1})


def cartesian_product(dists):
  return sum((d.map(lambda x: (x,)) for d in dists), ())


def pow(d, n, operator=operator.__add__):
  result = constant(0)
  while n > 0:
    # print(f'remaining power: {n}, d.size: {len(d._dist)}, result.size:
    # {len(result._dist)}')
    if n % 2 == 0:
      d = d.combine(d, operator)
      n //= 2
    else:
      result = result.combine(d, operator)
      n -= 1
  return result


def die(size):
  return Distribution(dict((i + 1, fractions.Fraction(1, size))
                           for i in range(size)))


def dice(num, size):
  # print(f"dice({num},{size})")
  # return sum(die(size) for _ in range(num))
  return pow(die(size), num)


def ifthenelse(condition, iftrue, iffalse):
  return condition.map(lambda x: x and iftrue or iffalse)


def ifthen(condition, iftrue):
  return ifthenelse(condition, iftrue, 0)


def switch_f(x, condition_result_list):
  for condition, result in condition_result_list:
    if condition(x):
      return result
  return 0


def switch(input, condition_result_list):
  return input.map(lambda x: switch_f(x, condition_result_list))


# basic combinations
assert Distribution.equivalent(die(6), dict(
    (i, fractions.Fraction(1, 6)) for i in range(1, 7)))
assert Distribution.equivalent(
    die(6) + 3, dict((i + 3, fractions.Fraction(1, 6)) for i in range(1, 7)))
assert Distribution.equivalent(die(6) + 3, 3 + die(6))
assert Distribution.equivalent(dice(2, 6), die(6) + die(6))
assert Distribution.equivalent(dice(2, 2), {2: fractions.Fraction(
    1, 4), 3: fractions.Fraction(2, 4), 4: fractions.Fraction(1, 4)})
assert Distribution.equivalent(die(2) - die(2), die(2) + die(2) - 3)
assert Distribution.equivalent(1 - die(2), die(2) - 2)
assert Distribution.equivalent(die(2) * die(2), {1: fractions.Fraction(
    1, 4), 2: fractions.Fraction(2, 4), 4: fractions.Fraction(1, 4)})

# expected value
assert 6.5 == die(12).ev()
assert 7 == dice(2, 6).ev()
assert 19.5 == (die(8) + 4 + dice(2, 6) + 4).ev()


# boolean magic
assert Distribution.equivalent(
    die(6) == 3,
    {
        True: fractions.Fraction(1, 6),
        False: fractions.Fraction(5, 6)
    })


def summarize(d, exact=False):
  ev = d.ev()
  if not exact:
    ev = float(ev)
  print(d, "mean:", ev, "stddev:", d.stddev())


# atleast/atmost:
assert die(6).atleast(4) == fractions.Fraction(1, 2)
assert die(6).atmost(4) == fractions.Fraction(2, 3)


def plausibility(d, v, exact=True):
  atl = d.atleast(v)
  atm = d.atmost(v)
  exa = d._dist[v]
  if not exact:
    atl, atm, exa = float(atl), float(atm), float(exa)
  print(f'odds of at least {v}: {atl}')
  print(f'odds of at most {v}: {atm}')
  print(f'odds of exactly {v}: {exa}')
