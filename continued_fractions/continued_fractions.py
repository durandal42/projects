import math
import fractions
import itertools

# "continue" is a keyword
def continued_fraction(x):
  assert x >= 0
  while True:
    if isinstance(x, fractions.Fraction):
      i = math.floor(x)
      f = x - i
    else:
      f, i = math.modf(x)
    yield int(i)
    if f == 0:
      break
    x = 1 / f

# https://mathworld.wolfram.com/PiContinuedFraction.html
assert (list(itertools.islice(continued_fraction(math.pi), 10)) ==
        [3,7,15,1,292,1,1,1,2,1,3,1,14][:10])

def approximations_from_continued_fraction(terms):
  terms_head = []
  for i in terms:
    terms_head.append(i)
    x = None
    for t in terms_head[::-1]:
      if x is None:
        x = fractions.Fraction(t)
      else:
        x = t + 1 / x
    yield x

def approximations(x):
  return approximations_from_continued_fraction(continued_fraction(x))


assert (list(itertools.islice(approximations(math.pi), 2)) ==
        [3, fractions.Fraction(22, 7)])

def best_approximation(x, max_denominator):
  best_so_far = None
  for a in approximations(x):
    print(a)
    if a.denominator > max_denominator:
      break
    best_so_far = a
  print()
  return best_so_far

for x in [
    math.pi,
    math.e,
    (1 + 5 ** 0.5) / 2, # golden ratio
    fractions.Fraction(199,400),
  ]:
  print(x)
  best_approximation(x, 10000)
  print()


