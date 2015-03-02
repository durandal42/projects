import collections
import copy

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
    
def prune_graph(graph, scores, threshold):
  graph = copy.deepcopy(graph)
  to_remove = [n for n in graph if scores[n] < threshold]
  for n in to_remove:
    for neighbor in graph[n]:
      graph[neighbor].remove(n)
    del graph[n]
  return graph
  
def component_nodes(node, graph):
  seen = set()
  frontier = [node]
  while frontier:
    current = frontier.pop()
    seen.add(current)
    frontier += [neighbor for neighbor in graph[current] if neighbor not in seen]
  return seen

def split_components(graph):
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

def solution(K, C, D):
  target_scores = target_sorted_list(D, K)
  print 'target attractiveness scores:', target_scores

  graph = make_graph(C)
  print 'graph:', graph

  graph = prune_graph(graph, D, target_scores[-1])
  print 'pruned:', graph

  components = split_components(graph)
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
        components += split_components(prune_graph(graph, C, t))
        print 'repruned and added to components queue.'
        repruned = True
        break
    if repruned: continue

    if len(scores) <= K and scores == target_scores[:K]:
      print 'eligible component found with size:', len(scores)
      best = max(best, len(scores))
      continue

    print 'don\'t know what to do with component, scores:', component, scores

  return best

SAMPLE_C = [1, 3, 0, 3, 2, 4, 4]  # graph edges
SAMPLE_D = [6, 2, 7, 5, 6, 5, 2]  # attractiveness scores

print solution(2, SAMPLE_C, SAMPLE_D)
