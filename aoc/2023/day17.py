from common import assertEqual
from common import submit
import heapq


def day17(input, min_streak=0, max_streak=3):
  grid = input.splitlines()
  # print('\n'.join(grid))
  num_rows = len(grid)
  num_cols = len(grid[0])
  print(f'{num_rows}x{num_cols} = {num_rows * num_cols}')

  q = []
  seen = set()
  start = (0, 0, 0, 0, 0, 0)
  heapq.heappush(q, start)
  while q:
    least_heat = heapq.heappop(q)
    if least_heat[1:] in seen:
      continue
    seen.add(least_heat[1:])
    heat_so_far, r, c, streak_dr, streak_dc, streak_len = least_heat
    if r == len(grid) - 1 and c == len(grid[r]) - 1 and streak_len >= min_streak:
      print(f'found a solution; len(q) = {len(q)}, len(seen) = {len(seen)}')
      return heat_so_far

    for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
      if dr == -streak_dr and dc == -streak_dc:
        continue  # can't u-turn
      if dr == streak_dr and dc == streak_dc:
        if streak_len >= max_streak:
          continue  # can't go >max spaces in a row in the same direction
      elif (streak_dr or streak_dc) and streak_len < min_streak:
        continue  # must go at least min spaces in a row in the same direction

      new_r = r+dr
      if new_r not in range(num_rows):
        continue
      new_c = c+dc
      if new_c not in range(num_cols):
        continue
      next = (heat_so_far + int(grid[new_r][new_c]), new_r, new_c, dr, dc,
              streak_len + 1 if dr == streak_dr and dc == streak_dc else 1)
      if next[1:] in seen:
        continue
      heapq.heappush(q, next)


test_input = '''\
2413432311323
3215453535623
3255245654254
3446585845452
4546657867536
1438598798454
4457876987766
3637877979653
4654967986887
4564679986453
1224686865563
2546548887735
4322674655533
'''
test_output = 102

assertEqual(test_output, day17(test_input))


print('day17 answer:')
submit(day17(open('day17_input.txt', 'r').read()),
       expected=814)
print()

# part2 complication
assertEqual(71, day17('''\
111111111111
999999999991
999999999991
999999999991
999999999991
''', min_streak=4, max_streak=10))

test_output = 94

assertEqual(test_output, day17(test_input, min_streak=4, max_streak=10))

print('day17, part2 answer:')
submit(day17(open('day17_input.txt', 'r').read(), min_streak=4, max_streak=10),
       expected=974)
print()
