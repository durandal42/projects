from common import assertEqual
from common import submit
import collections


def day16(input):
  grid = input.splitlines()

  # beware of \'s in inline input!
  assert min(len(r) for r in grid) == max(len(r) for r in grid)

  print('\n'.join(''.join(r) for r in grid))
  return illuminate(grid)


def illuminate(grid):
  illuminated_grid = [[' '] * len(grid[0]) for _ in range(len(grid))]
  seen = set()
  illuminated = set()
  frontier = collections.deque()
  frontier.append((0, 0, 0, 1))
  while frontier:
    next = frontier.pop()
    if next in seen:  # previously seen
      continue
    seen.add(next)

    r, c, dr, dc = next
    if r < 0 or r >= len(grid) or c < 0 or c >= len(grid[r]):  # out of bounds
      continue
    illuminated.add((r, c))
    tile = grid[r][c]
    illuminated_grid[r][c] = 'X'

    if tile == '.' or (tile == '|' and dr) or (tile == '-' and dc):
      # pass through
      frontier.append((r+dr, c+dc, dr, dc))
      continue
    elif tile == '\\':
      dr, dc = dc, dr  # reflect \
      frontier.append((r+dr, c+dc, dr, dc))
    elif tile == '/':
      dr, dc = -dc, -dr  # reflect /
      frontier.append((r+dr, c+dc, dr, dc))
    elif tile == '|':
      assert (dc and not dr)
      dr, dc = -1, 0  # split ^
      frontier.append((r+dr, c+dc, dr, dc))
      dr, dc = 1, 0  # split v
      frontier.append((r+dr, c+dc, dr, dc))
    elif tile == '-':
      assert (dr and not dc)
      dr, dc = 0, -1  # split <
      frontier.append((r+dr, c+dc, dr, dc))
      dr, dc = 0, 1  # split >
      frontier.append((r+dr, c+dc, dr, dc))
    else:
      assert False

  print('\n'.join(''.join(r) for r in illuminated_grid))
  print('-' * len(grid[0]))

  return len(illuminated)


# beware of \'s in inline input!
test_input = '''.|...\\....
|.-.\\.....
.....|-...
........|.
..........
.........\\
..../.\\\\..
.-.-/..|..
.|....-|.\\
..//.|....
'''
test_output = 46

assertEqual(test_output, day16(test_input))


print('day16 answer:')
submit(day16(open('day16_input.txt', 'r').read()),
       expected=7996)
print()
