from common import assertEqual
from common import submit
import collections


def union(d, a, b):
  # print(f'union({a}, {b})')
  fa = find(d, a)
  fb = find(d, b)
  if fa != fb:
    d[fb] = fa
  # print("[\n" + "\n".join("\t" + str(x) for x in d.items()) + "]")
  # print("[\n" + "\n".join("\t" + str(x) for x in classes(d).items()) + "]")


def find(d, x):
  # print(f'find({x})')
  if x not in d:  # never seen before; create new class
    d[x] = x
    return x
  if d[x] == x:  # points to self -> this is a root -> return self
    return x
  root = find(d, d[x])  # recursive call
  d[x] = root  # path compression
  return root


def classes(d):
  result = collections.defaultdict(list)
  for x in d:
    result[find(d, x)].append(x)
  return result


def parse_input(input):
  return {
      (r, c): x
      for r, row in enumerate(input.splitlines())
      for c, x in enumerate(row)
  }


def day12(input):
  # print(input)
  plots = parse_input(input)
  # print(plots)

  uf = {}
  for loc, plant in plots.items():
    find(uf, loc)
    r, c = loc
    for loc2 in [(r+1, c), (r, c+1)]:
      if plots.get(loc2) == plant:
        union(uf, loc, loc2)

  return sum(cost(region, plots) for region in classes(uf).items())


def cost(region, plots):
  c, locs = region
  plant = plots[c]
  area = len(locs)
  perimeter = 0
  for loc in locs:
    r, c = loc
    for loc2 in [(r+1, c), (r, c+1), (r-1, c), (r, c-1)]:
      if plots.get(loc2) != plant:
        perimeter += 1
  # print(f"{plant}\t{area}\t{perimeter}\t{locs}")
  return area * perimeter


test_input_1 = '''\
AAAA
BBCD
BBCC
EEEC
'''

assertEqual(140, day12(test_input_1))

test_input_2 = '''\
OOOOO
OXOXO
OOOOO
OXOXO
OOOOO
'''
assertEqual(772, day12(test_input_2))

test_input_3 = '''\
RRRRIICCFF
RRRRIICCCF
VVRRRCCFFF
VVRCCCJFFF
VVVVCJJCFE
VVIVCCJJEE
VVIIICJJEE
MIIIIIJJEE
MIIISIJEEE
MMMISSJEEE
'''
assertEqual(1930, day12(test_input_3))


print('day12 answer:')
submit(day12(open('day12_input.txt', 'r').read()),
       expected=1488414)
print()


# part 2 complication

def cost(region, plots):
  c, locs = region
  plant = plots[c]
  area = len(locs)

  segments = {}
  for loc in locs:
    r, c = loc
    for dr, dc in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
      loc2 = r+dr, c+dc
      if plots.get(loc2) != plant:
        segments[(r + dr/2, c + dc / 2)] = (dr, dc)

  num_fences = len(segments)

  for loc, d in segments.items():
    r, c = loc
    dr, dc = -d[1], d[0]  # rotated 90 degrees
    neighbor_loc = r+dr, c+dc
    if segments.get(neighbor_loc) == d:
      num_fences -= 1

  # print(f"{plant}\t{area}\t{num_fences}\t{locs}")
  return area * num_fences


assertEqual(80, day12(test_input_1))
assertEqual(436, day12(test_input_2))
assertEqual(1206, day12(test_input_3))

test_input_4 = '''\
EEEEE
EXXXX
EEEEE
EXXXX
EEEEE
'''
assertEqual(236, day12(test_input_4))

test_input_5 = '''\
AAAAAA
AAABBA
AAABBA
ABBAAA
ABBAAA
AAAAAA
'''
assertEqual(368, day12(test_input_5))

print('day12, part2 answer:')
submit(day12(open('day12_input.txt', 'r').read()),
       expected=911750)
print()
