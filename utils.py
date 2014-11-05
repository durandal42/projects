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

import collections
def count(word):
  result = {}
  for letter in word:
    result[letter] = result.get(letter, 0) + 1
  return result
