import collections
import itertools

def derive_from_pair(left, right):
  for cl, cr in itertools.izip(left, right):
    if cl != cr: return (cl, cr)
  return None

assert derive_from_pair('a', 'b') == ('a', 'b')
assert derive_from_pair('abcd', 'abce') == ('d', 'e')
assert derive_from_pair('', 'b') == None
assert derive_from_pair('b', 'b') == None

def derive_from_list(words):
  for left, right in zip(words[:-1], words[1:]):
    r = derive_from_pair(left, right)
    if r: yield r

assert set(derive_from_list(['', 'a', 'abcd', 'abce', 'b'])) == set([('d','e'), ('a', 'b')])

def build_graph(edges):
  g = collections.defaultdict(set)
  for a,b in edges:
    g[a].add(b)
    g[b]  # create empty set of children of b
  return g

assert build_graph([(0,1), (1,2), (2,3), (3,1), (3,4)]) == {0:set([1]), 1:set([2]), 2:set([3]), 3:set([1,4]), 4:set([])}

# destructively topological-sort an adjacency-list graph
def topo_sort(graph):
  # count number of incoming edges for each node:
  incoming_count = collections.defaultdict(int)
  for source, outgoing in graph.iteritems():
    for dest in outgoing:
      incoming_count[dest] += 1
  # identify nodes with no incoming edges:
  no_incoming = [n for n in graph.keys() if incoming_count[n] == 0]
  while graph:
    if not no_incoming:
      # every remaining node has at least one incoming edge; there's a cycle
      return  # can't proceed; caller will have seen everything we produced so far
    if len(no_incoming) > 1:
      # multiple remaining nodes have no incoming edges; there is not a unique total order
      pass  # can proceed, but answer won't be unique
    root = no_incoming.pop()
    # decrement incoming counts for all nodes pointed to by root
    for dest in graph[root]:
      incoming_count[dest] -= 1
      if incoming_count[dest] == 0: no_incoming.append(dest)
    # remove root from the graph
    del graph[root]
    yield root

assert list(topo_sort({0:set([1]), 1:set([2]), 2:set([3]), 3:set([1,4]), 4:set([])})) == [0]
assert list(topo_sort({0:set([1]), 1:set([2]), 2:set([3]), 3:set([4]), 4:set([])})) == [0, 1, 2, 3, 4]
assert list(topo_sort({0:set([1,2,3,4]), 1:set([2,3,4]), 2:set([3,4]), 3:set([4]), 4:set([])})) == [0, 1, 2, 3, 4]

import sys
words = [word.strip().lower() for word in sys.stdin.readlines()]
for letter in topo_sort(build_graph(derive_from_list(words))):
  print letter
