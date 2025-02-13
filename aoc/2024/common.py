def assertEqual(expected, actual):
  assert expected == actual, f"expected: {expected}\nactual: {actual}"


assertEqual(0, 0)
try:
  assertEqual(1, 0)
  assert False
except AssertionError:
  pass


def submit(answer, expected=None):
  if expected is not None:
    assertEqual(expected, answer)
  print(answer)


def sign(x):
  if x < 0:
    return -1
  if x > 0:
    return 1
  return 0
