from common import assertEqual
from common import submit


def day13(input):
  return sum(score(pattern.splitlines()) for pattern in input.split('\n\n'))


def score(pattern):
  h_mirror = find_mirror(pattern)
  v_mirror = find_mirror(transpose(pattern))
  return (v_mirror or 0) + (h_mirror or 0) * 100


def transpose(pattern):
  return [''.join(str(pattern[r][c])
                  for r in range(len(pattern)))
          for c in range(len(pattern[0]))]


assertEqual(['012'], transpose(['0', '1', '2']))
assertEqual(['12', '34'], transpose(transpose(['12', '34'])))


def find_mirror(pattern):
  # print(f'looking for mirror in:\n{"\n".join("".join(p) for p in pattern)}')
  for r in range(1, len(pattern)):
    mirror = True
    for above, below in zip(reversed(pattern[0:r]), pattern[r:]):
      if above != below:
        mirror = False
        break
    if mirror:
      return r


test_input = '''#.##..##.
..#.##.#.
##......#
##......#
..#.##.#.
..##..##.
#.#.##.#.

#...##..#
#....#..#
..##..###
#####.##.
#####.##.
..##..###
#....#..#
'''
test_output = 405

assertEqual(test_output, day13(test_input))

print('day13 answer:')
submit(day13(open('day13_input.txt', 'r').read()),
       expected=35521)
print()
