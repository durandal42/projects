import utils

@utils.Memoize
def dune(distance_remaining, previous_step=None, step_before_that=None):
  if distance_remaining == 0: return 1
  if distance_remaining < 0: return 0
  paths = 0
  for step_size in [1,2]:
    if (previous_step != step_size or step_before_that != step_size):
      paths += dune(distance_remaining - step_size, step_size, previous_step)
  return paths

for n in range(100):
  print n, dune(n)
