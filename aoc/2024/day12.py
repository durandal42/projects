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


test_input = '''\
AAAA
BBCD
BBCC
EEEC
'''
test_output = 140

assertEqual(test_output, day12(test_input))
assertEqual(772, day12('''\
OOOOO
OXOXO
OOOOO
OXOXO
OOOOO
'''))
assertEqual(1930, day12('''\
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
'''))


print('day12 answer:')
submit(day12(open('day12_input.txt', 'r').read()),
       expected=1488414)
print()
