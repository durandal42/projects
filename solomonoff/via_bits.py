import fractions
import cfg

class InsufficientEntropyError(Exception): pass
class EntropyOutOfRangeError(Exception): pass

_bits = iter([])
_bonus = fractions.Fraction(1)
def set_entropy_pool(bits):
  global _bits, _bonus
  _bits = iter(bits)
  _bonus = fractions.Fraction(1)

def randrange_from_fixed_entropy_pool(n):
  global _bonus
  assert n >= 0
  result, stop = 0,1
  while stop < n:
    try:
      bit = int(_bits.next())
    except StopIteration:
      raise InsufficientEntropyError('foo')
    assert bit in [0,1]
    #print '(consuming bit: %d)' % bit,
    stop *= 2
    result *= 2
    result += bit
  _bonus *= fractions.Fraction(stop, n)
  if result >= n:
    #print ' = %d, which is >= %d' % (result, n)
    raise EntropyOutOfRangeError('')
  return result

def stream_strings(f, nines=3):
  mass_threshold = 1.0 - (0.1 ** nines)
  format_string = '{:1.%df}' % (nines + 1)
  valid_mass = 0
  invalid_mass = fractions.Fraction()
  prefixes = ['']
  while prefixes and valid_mass / (1 - invalid_mass) < mass_threshold:
    new_prefixes = []
    for bitstring in prefixes:
      # probability mass of this bitstring; all children combined also have the same mass
      mass = fractions.Fraction(1, 2 ** (2 * len(bitstring) + 1))
      set_entropy_pool(bitstring)
      try:
        string = f(randrange_from_fixed_entropy_pool)
        valid_mass += mass * _bonus  # this bitstring was valid
        invalid_mass += mass * _bonus # all bitstrings with this as a prefix are invalid
#        print 'valid bitstring %s contains %s mass (including %sx bonus multiplier)' % (bitstring, mass * _bonus, _bonus)
#        print 'children of valid string contain %s invalid mass' % mass, invalid_mass
        yield mass,  string
  
        for bit in _bits:
          # bits left over; some prefix of this bitstring was a valid rule, but this one is not
          # don't yield a result, don't add to new_prefixes
          # this should never happen, because our valid prefix shouldn't have added itself to new_prefixes
          print bitstring
          assert False
      except InsufficientEntropyError:
        # this bitstring is the prefix of at least one valid bitstring, but is not valid itself
        invalid_mass += mass * _bonus # this bitstring was invalid
        new_prefixes.append(bitstring)  # try all children, reserve judgment on validity
#        print 'prefix; %s invalid mass (but will consider children)' % mass, invalid_mass
      except EntropyOutOfRangeError:
        # this bitstring was invalid, but its mass was distributed across its siblings as a bonus
        # its children will also be invalid
        #invalid_mass += mass
#        print 'entropy out of range for bitstring %s; %s invalid mass (bitstring and children)' % (bitstring, mass), invalid_mass
        pass
    prefixes = [prefix + bit for prefix in new_prefixes for bit in ['0','1']]
    print '%d remaining prefixes\t%s ratio\t%s target' % (
      len(prefixes), format_string.format(float(valid_mass / (1 - invalid_mass))), mass_threshold)

import sys

symbols, root = cfg.parse_grammar_file(sys.argv[1])
for item in stream_strings(
  lambda x: cfg.random_cfg_string(symbols, root, x),
  #emit_simple,
  int(sys.argv[2])):
  print 'mass, outcome:', item

