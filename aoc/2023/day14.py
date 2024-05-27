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

# part2 complication


def day14(input):
  return score(tilt_cycles(parse(input), 1000000000))


def tilt_cycles(grid, n):
  seen = []
  next_report = 1
  for i in range(n):
    grid = tilt_cycle(grid)
    copy = [r[:] for r in grid]  # needed since tilt() mutates grid
    for old_i, old_grid in enumerate(seen):
      if copy == old_grid:  # loop found!
        print(f'we saw this grid before back at i={old_i}, again at i={i}')
        loop_len = i - old_i
        print(f'loop length = {loop_len}')
        num_loops = (n - i) // loop_len
        print(f'num loops skipped = {num_loops}')
        n -= (num_loops + 1) * loop_len
        print(f'... and then step forward to i={n-1}')
        return seen[n-1]
    seen.append(copy)
    if i >= next_report:
      print(f'spin {i}/{n} (looking for repeats)')
      next_report *= 2
  return grid


assertEqual([1, 2], [1, 2])
assertEqual([[1], [2]], [[1], [2]])


def tilt_cycle(grid):
  for _ in range(4):
    grid = rotate(tilt(grid))
  return grid


def rotate(grid):
  return list(list(r) for r in zip(*grid[::-1]))


assertEqual([[3, 1], [4, 2]], rotate([[1, 2], [3, 4]]))

test_output = 64
assertEqual(test_output, day14(test_input))

print('day14, part2 answer:')
submit(day14(open('day14_input.txt', 'r').read()),
       expected=99291)
print()
