import math
import memoize

def tuple_add(x, y):
  return tuple(map(sum, zip(x, y)))

def num_pairs(n):
  return n * (n-1) / 2

@memoize.memoized
def num_connected_with_edges(nodes, remaining_edges, connected_components=None):
  if connected_components is None: connected_components = ((1,0),) * nodes

  if remaining_edges == 0:
    if len(connected_components) > 1:
      return 0
    else:
      return 1

  sum = 0
  for i, cci in enumerate(connected_components):
    for j, ccj in enumerate(connected_components):
      if i < j:
        continue
      if i == j:
        num_new_edges = num_pairs(cci[0]) - cci[1]
        if num_new_edges > 0:
          new_cc = list(connected_components)
          new_cc[i] = tuple_add(new_cc[i], (0,1))
          sum += num_new_edges * num_connected_with_edges(nodes,
                                                          remaining_edges - 1,
                                                          tuple(sorted(new_cc)))
      else:
        num_new_edges = cci[0] * ccj[0]
        new_cc = [cck for k, cck in enumerate(connected_components)
                                    if k != i and k !=j]
        new_cc.append(tuple_add(
            tuple_add(cci, ccj),
            (0,1)))
        sum += num_new_edges * num_connected_with_edges(nodes,
                                                        remaining_edges - 1,
                                                        tuple(sorted(new_cc)))

  return sum

def num_connected(n):
  sum = 0
  for v in range(max(0, n-1), num_pairs(n)+1):
    result = num_connected_with_edges(n, v) / math.factorial(v)
    print 'num_connected_with_edges(%s, %s):\t%s' % (n, v, result)
    sum += result
  return sum

TEST_DATA = [1, 1, 1, 4, 38, 728, 26704,
             1866256,
             251548592,
             66296291072,
             34496488594816,
             35641657548953344,
             73354596206766622208,
             301272202649664088951808,
             2471648811030443735290891264,
             40527680937730480234609755344896]
print "testing num_connected against https://oeis.org/A001187 ..."
import time
for n, expected in enumerate(TEST_DATA):
  start_time = time.clock()
  result = num_connected(n)
  stop_time = time.clock()
  print 'num_connected(%s):\t%s\t(%ss elapsed)' % (n, result, stop_time - start_time)
  assert result == expected
print "all tests passed."

'''
import itertools
for n in itertools.count(0):
  result = num_connected(n)
'''
