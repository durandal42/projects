def assertEqual(expected, actual):
  assert expected == actual, f"expected: {expected}\nactual: {actual}"

assertEqual(0, 0)
try:
  assertEqual(1, 0)
  assert False
except AssertionError:
  pass
