from common import assertEqual
from common import submit
import collections


def day16(input):
  grid = input.splitlines()

  # beware of \'s in inline input!
  assert min(len(r) for r in grid) == max(len(r) for r in grid)

  print('\n'.join(''.join(r) for r in grid))
  return illuminate(grid)


def illuminate(grid, r=0, c=0, dr=0, dc=1):
  seen = set()
  illuminated = set()
  frontier = collections.deque()
  frontier.append((r, c, dr, dc))
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

# part2 complication
test_output = 51


def day16(input):
  grid = input.splitlines()

  entry_points = []
  for r in range(len(grid)):
    entry_points.append((r, 0, 0, 1))
    entry_points.append((r, len(grid[r])-1, 0, -1))
  for c in range(len(grid[0])):
    entry_points.append((0, c, 1, 0))
    entry_points.append((len(grid)-1, c, -1, 0))

  return max(illuminate(grid, r, c, dr, dc) for r, c, dr, dc in entry_points)


print('day16, part2 answer:')
submit(day16(open('day16_input.txt', 'r').read()),
       expected=8239)
print()
