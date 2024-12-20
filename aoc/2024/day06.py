from common import assertEqual
from common import submit


def day06(input):
  grid = input.splitlines()

  gr, gc = None, None
  for r, row in enumerate(grid):
    if "^" in row:
      gr, gc = r, row.index("^")
      break
  assert gr
  assert gc

  seen = set()
  seen.add((gr, gc))

  dr, dc = -1, 0
  while True:
    if (gr+dr) not in range(len(grid)) or (gc+dc) not in range(len(grid[gr])):
      break
    if grid[gr+dr][gc+dc] == "#":
      dr, dc = dc, -dr
      continue
    gr += dr
    gc += dc
    seen.add((gr, gc))

  return len(seen)


test_input = '''\
....#.....
.........#
..........
..#.......
.......#..
..........
.#..^.....
........#.
#.........
......#...
'''
test_output = 41

assertEqual(test_output, day06(test_input))


print('day06 answer:')
submit(day06(open('day06_input.txt', 'r').read()),
       expected=5153)
print()
