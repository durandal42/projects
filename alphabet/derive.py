import collections
import itertools

def derive_from_pair(left, right):
  for cl, cr in itertools.izip(left, right):
    if cl != cr: return (cl, cr)
  return None

def derive_from_list(words):
  previous = None
  for word in words:
    if previous:
      r = derive_from_pair(previous, word)
      if r: yield r
    previous = word

def build_graph(edges):
  g = collections.defaultdict(set)
  for a,b in edges:
    g[a].add(b)
    g[b]
  return g

def topo_sort(graph):
  incoming_count = collections.defaultdict(int)
  for source, outgoing in graph.iteritems():
    for dest in outgoing:
      incoming_count[dest] += 1
  no_incoming = [n for n in graph.keys() if incoming_count[n] == 0]
  while graph:
    if not no_incoming: print 'cycle!', graph
    if len(no_incoming) > 1: print 'ambiguous!', no_incoming
    root = no_incoming.pop()
    for dest in graph[root]:
      incoming_count[dest] -= 1
      if incoming_count[dest] == 0: no_incoming.append(dest)
    del graph[root]
    yield root

import sys
words = [word.strip().lower() for word in sys.stdin.readlines()]
for letter in topo_sort(build_graph(derive_from_list(words))):
  print letter
