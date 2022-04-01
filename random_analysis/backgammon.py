import distribution

def print_normalized(ds):
  max_p = max(map(lambda d: d.max()[1], ds))
  for d in ds:
    print(d.__str__(max_p))

dice = distribution.product([
  distribution.die(6) for x in range(4)
])
    
print_normalized([
  dice,
  dice.map(lambda p: tuple(sorted(p))),
])

a = sum([
  distribution.die(6) for x in range(10)
]).map(lambda s: s % 2 + 1)
b = distribution.die(2)
print(a)
print(b)
print(a == b)
print(a.equivalent(b))

print(distribution.die(6) == distribution.die(8))

print(distribution.die(6) + 1)
