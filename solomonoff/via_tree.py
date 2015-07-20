import cfg
import fractions
import heapq
import operator

class InsufficientEntropyError(Exception): pass
class EntropyOutOfRangeError(Exception): pass

_path = iter([])
def set_path(path):
  global _path, _bonus
  _path = iter(path)

def randrange_from_fixed_path(n):
  assert n >= 0
  if n == 1: return 0
  try:
    result, limit = _path.next()
  except StopIteration:
    raise InsufficientEntropyError(n)  # signal upward what branching factor this path needs next
  assert limit == n
  if result >= n:
    raise EntropyOutOfRangeError(fractions.Fraction(result, n))
  return result

def stream_strings(f, nines=3):
  mass_threshold = 1.0 - (0.1 ** nines)
  if nines == 0: mass_threshold = 1.0
  format_string = '{:1.%df}' % (nines + 1)
  valid_mass = 0
  paths = [(1, [])]
  while paths and valid_mass < mass_threshold:
    inverse_mass, path = heapq.heappop(paths)
    set_path(path)
    try:
      string = f(randrange_from_fixed_path)
      mass = fractions.Fraction(1, inverse_mass)
      valid_mass += mass  # this path was valid
      yield mass,  string
#      print '%d remaining paths\t%s mass\t%s target' % (
#        len(paths), format_string.format(float(valid_mass)), mass_threshold)

      for choice in _path:
        # this should never happen, because our valid prefix path shouldn't have added itself back with children
        print path
        assert False
    except InsufficientEntropyError as e:
      # the path so far ran out of choices, and the next missing choice's branching factor is stored in e
      limit = e.args[0]
      for i in range(limit):
        heapq.heappush(paths, (inverse_mass * limit, path + [(i, limit)]))
    except EntropyOutOfRangeError:
      print path
      assert False  # this should never happen, because we built this path to match the requested choices exactly
      pass

import sys

if __name__ == '__main__':
  symbols, root = cfg.parse_grammar_file(sys.argv[1])
  for item in stream_strings(
    lambda x: cfg.random_cfg_string(symbols, root, x),
    #emit_simple,
    int(sys.argv[2])):
    print 'mass, outcome:', item
    pass
