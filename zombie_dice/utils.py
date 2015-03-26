import collections

class Memoize:
  def __init__(self, f, display=False):
    self.f = f
    self.memo = {}
    self.display = display
  def __call__(self, *args):
    if not args in self.memo:
      self.memo[args] = self.f(*args)
      if self.display:
        print 'memoized%s = %s' % (args, self.memo[args])
    return self.memo[args]

# Given a list of frequency dictionaries, compute their product.
# Optionally, apply a supplied reduce function to the resulting events sequences.
def cross_counted(args, f=lambda x: x):
  product = reduce(lambda left, right: {l + (r,): lc * rc
                                        for l, lc in left.iteritems()
                                        for r, rc in right.iteritems()},
                   args, {():1})
  result = collections.Counter()
  for event, count in product.iteritems():
    result[f(event)] += count
  return result

assert (cross_counted([{'a':2, 'b':3},
                       {'c':5, 'd':7, 'e':11}]) ==
        {('a', 'c'): 10,
         ('a', 'd'): 14,
         ('a', 'e'): 22,
         ('b', 'c'): 15,
         ('b', 'd'): 21,
         ('b', 'e'): 33,
         })

assert (cross_counted([{'a':2, 'b':3},
                       {'c':5, 'd':7, 'e':11}],
                      lambda x: x[0]) ==
        {'a': 10 + 14 + 22,
         'b': 15 + 21 + 33,})