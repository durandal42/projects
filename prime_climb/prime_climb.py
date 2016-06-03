import itertools
ROLLS = [r for r in itertools.product(range(1,11), range(1, 11))]
print ROLLS

OPS = [c for c in itertools.product(" _", "+*-/", "+*-/")]
print OPS

def update(steps):
  new_steps = [0.0 for i in range(len(steps))]
  for i, _ in enumerate(steps):
    if i == 101: continue
    results = []
    for r1, r2 in ROLLS:
      best_result = None
      for operations in OPS:
        operands = [r1, r2]
        location = i
        for op in operations:
          if op == ' ': continue
          if op == '_': operands.reverse()
          if op == '+':
            location += operands.pop()
          if op == '-':
            location -= operands.pop()
          if op == '*':
            location *= operands.pop()
          if op == '/':
            if location % operands[-1] != 0:
              location = None  # invalid location
              break
            location /= operands.pop()
          if location < 0 or location > 101:
            location = None  # invalid location
            break
          if location == 101:
            break
        if location is None: continue
        result = (steps[location], location)
#        print '\t\ti: %d, roll: %s, ops: %s, result(steps, location): %s' % (i, (r1, r2), operations, result)
        if best_result is None or result < best_result:
          best_result = result
#      print '\ti: %d, roll: %s, best result: %s' % (i, (r1, r2), best_result)
      results.append(best_result[0])
    new_steps[i] = 1 + sum(results) / len(results)
#    print 'i: %d, expected steps to goal: %d, best results: %s' % (i, new_steps[i], results)
  return new_steps

def solve(steps):
  iterations = 0
  while True:
    print steps
    new_steps = update(steps)
    iterations += 1
    if new_steps == steps:
      break
    steps = new_steps
  print steps
  for i, s in enumerate(steps):
    print "%d\t%s" % (i, s)
  print "(took %d iterations to stabilize)" % iterations

INITIAL = [101-x for x in range(102)]

solve(INITIAL)
