"""
write a function that takes k and returns the kth smallest possible value for 2^x*3^y*5^z if x y and z are non-negative int variables

so, the kth number whose prime factors consist only of {2,3,5}
"""

import itertools

def is_eligible(x):
  for d in [2,3,5]:
    while x % d == 0:
      x /= d
  return x == 1

def all_eligible_naive():
  return (i for i in itertools.count(1) if is_eligible(i))

def make_tuple(p2, p3, p5):
  return (pow(2, p2) * pow(3, p3) * pow(5, p5), p2, p3, p5)

import heapq
def all_eligible_frontier():
  seen = set()
  frontier = []
  initial = make_tuple(0,0,0)
  seen.add(initial)
  heapq.heappush(frontier, initial)
  while frontier:
    next = heapq.heappop(frontier)
    n, p2, p3, p5 = next
    yield n
    for new in [make_tuple(p2+1, p3, p5),
                make_tuple(p2, p3+1, p5),
                make_tuple(p2, p3, p5+1)]:
      if new not in seen:
        heapq.heappush(frontier, new)
        seen.add(new)

def kth_smallest_eligible(k):
  return next(itertools.islice(all_eligible_frontier(), k, None))

for k in range(1, 512):
  # k = pow(2, p)
  kth = kth_smallest_eligible(k)
  print k, kth
