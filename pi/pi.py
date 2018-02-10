'''
Probability of two random numbers being coprime == 6/pi^2
'''

import fractions
import math
import itertools

# We'll pick 'random' numbers uniformly from 1-max.
# ... and then we'll consider all possible pairs within that space at once.
coprime_pairs = 0
for max in itertools.count(2):
  # Instead of computing the whole max*max square again each time, remember
  # how many coprime pairs we found in the previous (max-1)*(max-1) square.
  new_coprime_pairs = sum(1 for a in range(max) if fractions.gcd(a,max)==1)
  # For every new (a,max) coprime pair we find, (max,b) is also coprime.
  # (max,max) is never coprime.
  coprime_pairs += 2 * new_coprime_pairs
  # The number of possible pairs is always just max^2
  print "i: %d,\tpi: %f" % (max, math.sqrt(6.0 * max**2 / coprime_pairs))
