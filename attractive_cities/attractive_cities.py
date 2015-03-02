import collections
import copy
import heapq


def make_graph(C):
  G = collections.defaultdict(list)
  for i in range(len(C)):
    if C[i] != i:
      G[i] += [C[i]]
      G[C[i]] += [i]
  return G

def target_sorted_list(D, K):
  D_sorted = sorted(D, reverse=True)
  for i in range(K-1, len(D)):
    if D_sorted[i] < D_sorted[K-1]:
      return D_sorted[:i]
    
def remove_node(node, graph):
  for neighbor in graph[node]:
    graph[neighbor].remove(node)
  del graph[node]

def prune_graph(graph, scores, threshold):
  to_remove = [n for n in graph if scores[n] < threshold]
  for n in to_remove:
    remove_node(n, graph)
  
def component_nodes(node, graph):
  seen = set()
  frontier = [node]
  while frontier:
    current = frontier.pop()
    seen.add(current)
    frontier += [neighbor for neighbor in graph[current] if neighbor not in seen]
  return seen

def get_components(graph):
  graph = copy.deepcopy(graph)
  result = []
  while graph:
    current_component = {}
    seed = graph.keys()[0]
    nodes = component_nodes(seed, graph)
    for node in nodes:
      current_component[node] = graph[node]
      del graph[node]
    result.append(current_component)
  return result

def leaf_heap(G, D):
  leaves = [(D[n], n) for n in G if len(G[n]) == 1]
  heapq.heapify(leaves)
  return leaves

def remove_leaf(G, D):
  leaves = leaf_heap(G, D)
  minleaf = heapq.heappop(leaves)[1]
  remove_node(minleaf, G)

def solution(K, C, D):
  target_scores = target_sorted_list(D, K)
  print 'target attractiveness scores:', target_scores

  graph = make_graph(C)
  print 'graph:', graph

  prune_graph(graph, D, target_scores[-1])
  print 'pruned:', graph

  components = get_components(graph)
  print 'components:', components

  best = 0
  while components:
    component = components.pop()
    print 'component:', component
    nodes = component.keys()
    scores = sorted([D[n] for n in nodes], reverse=True)

    repruned = False
    for t,a in zip(target_scores, scores):
      if t > a:
        prune_graph(graph, D, t)
        components += get_components(graph)
        print 'target/actual score mismatch; repruned and added to components queue.'
        repruned = True
        break
    if repruned: continue

    leaves = leaf_heap(graph, D)
    while len(scores) > K or scores != target_scores[:len(scores)]:
      worst_leaf_score, worst_leaf = heapq.heappop(leaves)
      if worst_leaf_score == scores.pop():
        remove_node(worst_leaf, component)
        print 'discarding unattractive leaf:', worst_leaf
        continue
      else:
        prune_graph(graph, D, worst_leaf_score)
        components += get_components(graph)
        print 'worst leaf was not worst node; repruned and added to components queue.'
        repruned = True
        break
    if repruned: continue

    print 'eligible component found with size %d: %s' % (len(scores), component)
    best = max(best, len(scores))
    continue

  return best

SAMPLE_C = [1, 3, 0, 3, 2, 4, 4]  # graph edges
SAMPLE_D = [6, 2, 7, 5, 6, 5, 2]  # attractiveness scores

print solution(2, SAMPLE_C, SAMPLE_D)
print solution(5, SAMPLE_C, SAMPLE_D)
