from common import assertEqual
from common import submit


def day14(input):
  return score(tilt(parse(input)))


def parse(input):
  return [list(line) for line in input.splitlines()]


def tilt(grid):
  for r, row in enumerate(grid):
    if r == 0:
      continue
    for c, x in enumerate(row):
      if x != 'O':
        continue
      min_r = r
      for r2 in range(r - 1, -1, -1):
        if grid[r2][c] == '.':
          min_r = r2
        else:
          break
      if r2 < r:
        grid[min_r][c], grid[r][c] = grid[r][c], grid[min_r][c]  # swap
  return grid


def score(grid):
  result = 0
  for r, row in enumerate(grid):
    for x in row:
      if x == 'O':
        result += len(grid) - r
  return result


test_input = '''O....#....
O.OO#....#
.....##...
OO.#O....O
.O.....O#.
O.#..O.#.#
..O..#O..O
.......O..
#....###..
#OO..#....
'''
tilted = parse('''OOOO.#.O..
OO..#....#
OO..O##..O
O..#.OO...
........#.
..#....#.#
..O..#.O.O
..O.......
#....###..
#....#....
''')
assertEqual(tilted, tilt(parse(test_input)))
test_output = 136

assertEqual(test_output, day14(test_input))


print('day14 answer:')
submit(day14(open('day14_input.txt', 'r').read()),
       expected=108826)
print()
