from common import assertEqual
from common import submit
import collections
import re


def find_intersections(grid, r, c, tr, tc):
  intersections = [(r, c)]
  for r, row in enumerate(grid):
    for c, col in enumerate(row):
      if col != '#' and len(adjacent_cells(grid, r, c)) > 2:
        intersections.append((r, c))
  intersections.append((tr, tc))
  # print('\n'.join(''.join(str(intersections.index((r, c))) if (r, c) in intersections else x
  #                         for c, x in enumerate(row))
  #                 for r, row in enumerate(grid)))
  return intersections


def build_adjacency_matrix(grid, intersections):
  adjacency_matrix = [dict() for _ in range(len(intersections))]
  intersection_indexes = dict((inter, i) for i, inter in enumerate(intersections))
  for i, inter in enumerate(intersections):
    r, c = inter
    for tr, tc, n in reachable_intersections(grid, r, c, intersection_indexes):
      adjacency_matrix[i][intersection_indexes[(tr, tc)]] = n
  # print('\n'.join(f'{i}: {str(a)}' for i, a in enumerate(adjacency_matrix)))
  return adjacency_matrix


LEGAL_STEPS = {
    '^': [(-1, 0)],
    'v': [(1, 0)],
    '>': [(0, 1)],
    '<': [(0, -1)],
}


def adjacent_cells(grid, r, c):
  directions = LEGAL_STEPS.get(grid[r][c], [(-1, 0), (1, 0), (0, -1), (0, 1)])
  result = []
  for dr, dc in directions:
    nr, nc = r + dr, c + dc
    if nr not in range(len(grid)):
      continue
    if nc not in range(len(grid[nr])):
      continue
    if grid[nr][nc] == '#':
      continue
    result.append((nr, nc))
  return result


def reachable_intersections(grid, r, c, intersection_indexes):
  frontier = []
  frontier.append((r, c, []))
  result = []
  while frontier:
    r, c, path = frontier.pop()
    adjacent = adjacent_cells(grid, r, c)
    if len(path) > 1 and (r, c) in intersection_indexes:
      result.append((r, c, len(path)))
      continue

    adjacent = [a for a in adjacent if len(path) < 1 or a != path[-1]]
    if path and len(adjacent) != 1:
      continue

    for nr, nc in adjacent:
      frontier.append((nr, nc, path + [(r, c)]))

  return result


def longest_path_matrix(adjacency_matrix):
  frontier = []
  frontier.append((0, 1 << 0, 0, 1))
  longest = 0
  paths_found = 0
  target = len(adjacency_matrix)-1
  while frontier:
    i, path_bits, cost, length = frontier.pop()
    if i == target:
      paths_found += 1
      longest = max(longest, cost)
    for j, marginal_cost in adjacency_matrix[i].items():
      if not path_bits & (1 << j):
        frontier.append((j, path_bits | 1 << j, cost + marginal_cost, length + 1))
  return longest


def longest_path_matrix_bidi(adjacency_matrix):
  frontier = []
  frontier.append((0, 1 << 0, 0, 0))
  longest = 0
  paths_found = 0
  target = len(adjacency_matrix)-1

  BIDI_MIDPOINT = target // 2 + 1
  midpoints = collections.defaultdict(list)

  while frontier:
    i, path_bits, cost, length = frontier.pop()
    if i == target:
      paths_found += 1
      longest = max(longest, cost)
    if length == BIDI_MIDPOINT:
      midpoints[i].append((cost, path_bits, length))
      continue
    for j, marginal_cost in adjacency_matrix[i].items():
      if not path_bits & (1 << j):
        frontier.append((j, path_bits | 1 << j, cost + marginal_cost, length + 1))

  # print('len(midpoints):', sum(len(v) for k, v, in midpoints.items()))
  for k, v in midpoints.items():
    v.sort(reverse=True)
  # print('backwards search!')

  frontier.append((target, 1 << target, 0, 1))
  while frontier:
    i, path_bits, cost, length = frontier.pop()
    if length > BIDI_MIDPOINT:
      continue

    for fwd_cost, fwd_path_bits, fwd_length in midpoints[i]:
      if fwd_cost + cost <= longest:
        break
      if fwd_path_bits & path_bits == 1 << i:
        paths_found += 1
        longest = max(longest, fwd_cost + cost)
    for j, marginal_cost in adjacency_matrix[i].items():
      if not path_bits & (1 << j):
        frontier.append((j, path_bits | 1 << j, cost + marginal_cost, length + 1))

  return longest


def longest_path(grid, r, c, tr, tc):
  intersections = find_intersections(grid, r, c, tr, tc)
  adjacency_matrix = build_adjacency_matrix(grid, intersections)
  bidi_safe = not any(grid[r][c] in '^v<>'
                      for r in range(len(grid))
                      for c in range(len(grid[r])))
  if bidi_safe:
    return longest_path_matrix_bidi(adjacency_matrix)
  else:
    return longest_path_matrix(adjacency_matrix)


def day23(input):
  grid = [list(line) for line in input.splitlines()]
  return longest_path(
      grid,
      0, grid[0].index('.'),
      len(grid)-1, grid[-1].index('.'))


test_input = '''\
#.#####################
#.......#########...###
#######.#########.#.###
###.....#.>.>.###.#.###
###v#####.#v#.###.#.###
###.>...#.#.#.....#...#
###v###.#.#.#########.#
###...#.#.#.......#...#
#####.#.#.#######.#.###
#.....#.#.#.......#...#
#.#####.#.#.#########v#
#.#...#...#...###...>.#
#.#.#v#######v###.###v#
#...#.>.#...>.>.#.###.#
#####v#.#.###v#.#.###.#
#.....#...#...#.#.#...#
#.#########.###.#.#.###
#...###...#...#...#.###
###.###.#.###v#####v###
#...#...#.#.>.>.#.>.###
#.###.###.#.###.#.#v###
#.....###...###...#...#
#####################.#
'''
test_output = 94

assertEqual(test_output, day23(test_input))


print('day23 answer:')
submit(day23(open('day23_input.txt', 'r').read()),
       expected=2190)
print()

# part2 complication
test_output = 154


def ignore_slopes(input):
  return re.sub('[<>^v]', '.', input)


assertEqual(test_output, day23(ignore_slopes(test_input)))

print('day23, part2 answer:')
submit(day23(ignore_slopes(open('day23_input.txt', 'r').read())),
       expected=6258)
print()
