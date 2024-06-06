from common import assertEqual
from common import submit
import collections
import random
import copy
import itertools


def parse_input(input):
  g = collections.defaultdict(list)
  for line in input.splitlines():
    tokens = line.split(': ')
    src = tokens[0]
    for dst in tokens[1].split(' '):
      g[src].append(dst)
      g[dst].append(src)
  return g


def num_edges(g):
  return sum(len(dsts) for src, dsts in g.items())


def choose_nth_edge(g, n):
  for src, dsts in g.items():
    l = len(dsts)
    if l > n:
      return (src, dsts[n])
    else:
      n -= l


def node_weight(n):
  if isinstance(n, tuple):
    return n[1]
  return 1


def contraction_algorithm(g):
  ne = num_edges(g)  # compute this once and then update it as we add/remove edges
  supernodes_created = 0
  while len(g) > 2:
    e = choose_nth_edge(g, random.randrange(ne))
    n1, n2 = e
    supernode = (supernodes_created, node_weight(n1) + node_weight(n2))
    supernodes_created += 1

    n1_dsts = g[n1]
    n2_dsts = g[n2]
    del g[n2]
    del g[n1]
    ne -= len(n1_dsts)
    ne -= len(n2_dsts)

    g[supernode] = [n for n in n1_dsts if n != n2] + [n for n in n2_dsts if n != n1]
    ne += len(g[supernode])
    for dst in g[supernode]:
      g[dst] = [supernode if n in (n1, n2) else n for n in g[dst]]

  return g


def num_cuts(g):
  assertEqual(2, len(g))
  edges = [len(dsts) for src, dsts in g.items()]
  assertEqual(edges[0], edges[1])
  return edges[0]


def day25(input):
  graph = parse_input(input)
  print('num nodes:', len(graph))
  print('num edges:', num_edges(graph))

  num_attempts_expected = len(graph) * (len(graph)-1)
  print(f'seeking a 3-cut, worst case 1/e chance of failure after {num_attempts_expected} attempts')
  for num_attempts in itertools.count(1):
    partition = contraction_algorithm(copy.deepcopy(graph))
    print(f'attempt #{num_attempts} found a {num_cuts(partition)}-cut')
    if num_cuts(partition) > 3:
      continue
    print(f'found a 3-cut after {num_attempts} attempts')
    supernodes = list(partition.keys())
    return (supernodes[0][1]) * (supernodes[1][1])


test_input = '''\
jqt: rhn xhk nvd
rsh: frs pzl lsr
xhk: hfx
cmg: qnr nvd lhk bvb
rhn: xhk bvb hfx
bvb: xhk hfx
pzl: lsr hfx nvd
qnr: nvd
ntq: jqt hfx bvb xhk
nvd: lhk
lsr: lhk
rzs: qnr cmg lsr rsh
frs: qnr lhk lsr
'''
test_output = 54

assertEqual(test_output, day25(test_input))


print('day25 answer:')
submit(day25(open('day25_input.txt', 'r').read()),
       expected=596376)
print()
