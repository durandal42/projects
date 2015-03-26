import collections

import collections
import functools

class memoized(object):
  '''Decorator. Caches a function's return value each time it is called.
  If called later with the same arguments, the cached value is returned
  (not reevaluated).
  '''
  def __init__(self, func):
    self.func = func
    self.cache = {}
  def __call__(self, *args):
    if not isinstance(args, collections.Hashable):
      # uncacheable. a list, for instance.
      # better to not cache than blow up.
      return self.func(*args)
    if args in self.cache:
      return self.cache[args]
    else:
      value = self.func(*args)
      self.cache[args] = value
      return value
  def __repr__(self):
    '''Return the function's docstring.'''
    return self.func.__doc__
  def __get__(self, obj, objtype):
    '''Support instance methods.'''
    return functools.partial(self.__call__, obj)


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