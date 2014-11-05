import itertools
import fractions

def bitstream(penalty=1):
  yield ('', fractions.Fraction(1) / (penalty * 2))
  for suffix, mass in bitstream(penalty * 2):
    for prefix in ['0','1']:
      yield (prefix + suffix, mass / 2)

def stream_until(mass_threshold, f=lambda x: x):
  valid_mass = 0
  invalid_mass = 0
  for bitstring, mass in bitstream():
    hypothesis = f(bitstring)
    if hypothesis is None:
      invalid_mass += mass
    else:
      valid_mass += mass
      # print '"%s"\t%s\t%s' % (hypothesis, mass, valid_mass)
      yield mass, bitstring, float(valid_mass / (1 - invalid_mass)), hypothesis
      if valid_mass / (1 - invalid_mass) >= mass_threshold:
        break

#stream_until(0.99)
