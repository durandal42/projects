from common import assertEqual
from common import submit


def day04(input):
  target = "XMAS"
  grid = input.splitlines()

  matches = 0
  for r in range(len(grid)):
    for c in range(len(grid[r])):
      for dr in [-1, 0, 1]:
        if r + (len(target)-1) * dr not in range(len(grid)):
          continue
        for dc in [-1, 0, 1]:
          if c + (len(target)-1) * dc not in range(len(grid[r])):
            continue
          if all(grid[r + i * dr][c + i * dc] == target[i]
                 for i in range(len(target))):
            matches += 1

  return matches


test_input = '''\
MMMSXXMASM
MSAMXMSMSA
AMXSXMAAMM
MSAMASMSMX
XMASAMXAMM
XXAMMXXAMA
SMSMSASXSS
SAXAMASAAA
MAMMMXMMMM
MXMXAXMASX
'''
test_output = 18

assertEqual(test_output, day04(test_input))


print('day04 answer:')
submit(day04(open('day04_input.txt', 'r').read()),
       expected=None)
print()
