import cfg
import via_tree
import itertools
import fractions


symbols, root = cfg.parse_grammar_file('zendo_python_rules.txt')

def all_theories():
  next_report = fractions.Fraction(1)
  for mass, theory in via_tree.stream_strings(
    lambda x: cfg.random_cfg_string(symbols, root, x),
    10):
    # print 'generated theory:', theory
    yield mass, theory
    if mass < next_report:
      next_report = mass / 2
      print mass


SMALL = 's'
MEDIUM = 'm'
LARGE = 'l'

RED = 'r'
GREEN = 'g'
YELLOW = 'y'
BLUE = 'b'

UPRIGHT = 'u'
FLAT = 'f'

GROUNDED = 'g'
UNGROUNDED = 'u'

class Piece(object):
  def __init__(self, size=None, color=None, location=GROUNDED, orientation=UPRIGHT):
    self.size = size
    self.color = color
    self.location = location
    self.orientation = orientation

def all(pieces, predicate):
  for p in pieces:
    if not predicate(p): return False
  return True

def exists(pieces, predicate):
  for p in pieces:
    if predicate(p): return True
  return False

def count(ps):
  return len(ps)

def pip_count(ps):
  return sum(map(pips, ps))

def pips(p):
  return {SMALL:1, MEDIUM:2, LARGE:3}[p.size]

def distinct_attribute_values_represented(attribute):
  return lambda ps: len(set(map(lambda x: x.__dict__[attribute], ps)))

def attribute_is(attribute, value):
  return lambda p: p.__dict__[attribute] == value

def even(n):
  return n % 2 == 0

def odd(n):
  return n % 2 != 0

def exactly(n):
  return lambda x: x == n

def greater_than(n):
  return lambda x: x > n

def less_than(n):
  return lambda x: x < n

discarded_theories = 0
discarded_mass = 0
def apply_evidence(theory_stream, pieces, result):
  for mass, theory in theory_stream:
#    print 'testing theory:', theory
    if result == eval(theory):
      yield mass, theory
    else:
      global discarded_theories
      global discarded_mass
      discarded_theories += 1
      discarded_mass += mass
#      print 'theory invalidated:', mass, theory

def solve(evidence):
  theory_stream = all_theories()
  for pieces, result in evidence:
    theory_stream = apply_evidence(theory_stream, pieces, result)
  for mass, theory in itertools.islice(theory_stream, 1):
    print mass, theory
  print 'discarded theories:', discarded_theories
  print 'discarded mass:', (0.0 + discarded_mass)


'''
print 'all pieces are the same color'
solve([
  ([Piece(SMALL, RED)], True),
  ([Piece(MEDIUM, BLUE), Piece(LARGE, YELLOW)], False),
  ([Piece(SMALL, RED), Piece(LARGE, RED)], True),
  ([Piece(SMALL, RED), Piece(SMALL, GREEN)], False),
  ([Piece(SMALL, YELLOW), Piece(SMALL, YELLOW)], True),
  ([Piece(SMALL, GREEN), Piece(MEDIUM, RED), Piece(LARGE, BLUE)], False),
  ])
'''

'''
print 'all pieces are the same size'
solve([
  ([Piece(SMALL, BLUE), Piece(SMALL, RED)], True),
  ([Piece(MEDIUM, BLUE), Piece(SMALL, RED)], False),
  ([Piece(SMALL, YELLOW)], True),
  ([Piece(MEDIUM, RED), Piece(MEDIUM, RED)], True),
  ([Piece(SMALL, YELLOW), Piece(MEDIUM, YELLOW), Piece(LARGE, YELLOW)], False),
  ])
'''
'''
print 'all four colors are present'
solve([
  ([Piece(SMALL, YELLOW), Piece(MEDIUM, GREEN), Piece(LARGE, BLUE), Piece(MEDIUM, RED)], True),
  ([], False),
  ([Piece(LARGE, YELLOW), Piece(MEDIUM, BLUE)], False),
  ([Piece(LARGE, YELLOW), Piece(MEDIUM, GREEN), Piece(LARGE, BLUE), Piece(MEDIUM, RED)], True),
  ([Piece(MEDIUM, GREEN), Piece(MEDIUM, RED)], False),
  ([Piece(LARGE, YELLOW), Piece(MEDIUM, GREEN), Piece(LARGE, YELLOW), Piece(MEDIUM, GREEN)], False),
  ([Piece(LARGE, YELLOW), Piece(MEDIUM, GREEN), Piece(LARGE, BLUE), Piece(MEDIUM, GREEN)], False),
  ])
'''
'''
print 'no greens'
solve([
  ([], True),
  ([Piece(SMALL, GREEN)], False),
  ([Piece(SMALL, RED), Piece(MEDIUM, YELLOW)], True),
  ([Piece(LARGE, BLUE)], True),
  ])
'''
'''
print 'has a medium yellow'
solve([
  ([Piece(SMALL, RED), Piece(MEDIUM, YELLOW)], True),
  ([Piece(LARGE, GREEN)], False),
  ([Piece(MEDIUM, YELLOW), Piece(MEDIUM, RED), Piece(LARGE, GREEN)], True),
  ([Piece(MEDIUM, RED)], False),
  ([Piece(SMALL, YELLOW)], False),
  ([Piece(MEDIUM, RED), Piece(LARGE, YELLOW)], False),
  ])
'''
'''
print 'all pieces are flat'
solve([
  ([Piece(SMALL, RED, GROUNDED, UPRIGHT)], False),
  ([Piece(LARGE, GREEN, GROUNDED, FLAT)], True),
  ])
'''
'''
print 'has at least 2 upright pieces'
solve([
  ([Piece(SMALL, RED, GROUNDED, UPRIGHT)], False),
  ([Piece(LARGE, GREEN, GROUNDED, FLAT),
    Piece(SMALL, YELLOW, UNGROUNDED, UPRIGHT),
    Piece(MEDIUM, RED, GROUNDED, UPRIGHT)], True),
  ([Piece(MEDIUM, RED, GROUNDED, UPRIGHT)], False),
  ([Piece(MEDIUM, RED, UNGROUNDED, UPRIGHT)], False),
  ([Piece(MEDIUM, RED, UNGROUNDED, FLAT)], False),
  ([Piece(LARGE, RED, UNGROUNDED, FLAT)], False),
  ([Piece(SMALL, GREEN, UNGROUNDED, UPRIGHT),
    Piece(MEDIUM, RED, GROUNDED, UPRIGHT)], True),
  ([Piece(MEDIUM, GREEN, GROUNDED, UPRIGHT)], False),
  ([], False),
  ([Piece(SMALL, GREEN, UNGROUNDED, FLAT),
    Piece(MEDIUM, RED, GROUNDED, UPRIGHT)], False),
  ])
'''

print 'has exactly one red and exactly one blue NOT ACTUALLY EASY'
solve([
  ([Piece(SMALL, RED), Piece(MEDIUM, BLUE)], True),
  ([Piece(LARGE, GREEN), Piece(SMALL, YELLOW)], False),
  ([Piece(LARGE, RED)], False),
  ([Piece(MEDIUM, BLUE)], False),
  ([Piece(MEDIUM, RED), Piece(LARGE, BLUE)], True),
  ([Piece(MEDIUM, RED), Piece(LARGE, RED)], False),
  ([], False),
  ([Piece(SMALL, RED), Piece(MEDIUM, GREEN)], False),
  ([Piece(SMALL, YELLOW), Piece(MEDIUM, BLUE)], False),
  ([Piece(SMALL, RED), Piece(MEDIUM, BLUE), Piece(SMALL, RED), Piece(MEDIUM, BLUE)], False),
  ([Piece(SMALL, RED), Piece(MEDIUM, BLUE), Piece(SMALL, RED), Piece(MEDIUM, BLUE)], False),
  ([Piece(SMALL, RED), Piece(MEDIUM, RED), Piece(SMALL, RED), Piece(MEDIUM, BLUE)], False),
  ([Piece(SMALL, RED), Piece(MEDIUM, BLUE), Piece(SMALL, BLUE), Piece(MEDIUM, BLUE)], False),
# unsolved
  ])

'''
print 'either all warm (red and yellow) or all cool (blue and green)'
solve([
  ([Piece(SMALL, RED)], True),
  ([Piece(LARGE, BLUE), Piece(MEDIUM, YELLOW)], False),
  ([Piece(SMALL, RED), Piece(SMALL, YELLOW)], True),
  ([Piece(SMALL, YELLOW), Piece(SMALL, GREEN)], False),
  ([Piece(SMALL, RED), Piece(LARGE, BLUE)], False),
  ([Piece(MEDIUM, GREEN)], True),
  ([Piece(LARGE, GREEN), Piece(LARGE, GREEN), Piece(MEDIUM, YELLOW)], False),
  ([Piece(LARGE, BLUE)], True),
  ])
'''
