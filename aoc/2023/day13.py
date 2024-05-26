from common import assertEqual
from common import submit


def day13(input, error_target=0):
  return sum(score(pattern.splitlines(), error_target) for pattern in input.split('\n\n'))


def score(pattern, error_target):
  h_mirror = find_mirror(pattern, error_target)
  v_mirror = find_mirror(transpose(pattern), error_target)
  return (v_mirror or 0) + (h_mirror or 0) * 100


def transpose(pattern):
  return [''.join(str(pattern[r][c])
                  for r in range(len(pattern)))
          for c in range(len(pattern[0]))]


assertEqual(['012'], transpose(['0', '1', '2']))
assertEqual(['12', '34'], transpose(transpose(['12', '34'])))


def mismatches(left, right):
  assert len(left) == len(right)
  result = 0
  for l, r in zip(left, right):
    if l != r:
      result += 1
  return result


def find_mirror(pattern, error_target):
  # print(f'looking for mirror in:\n{"\n".join("".join(p) for p in pattern)}')
  for r in range(1, len(pattern)):
    mirror = True
    mm = 0
    for above, below in zip(reversed(pattern[0:r]), pattern[r:]):
      mm += mismatches(above, below)
      if mm > error_target:
        mirror = False
        break
    if mirror and mm == error_target:
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

# part2 complication


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
test_output = 400

assertEqual(test_output, day13(test_input, error_target=1))

print('day13, part2 answer:')
submit(day13(open('day13_input.txt', 'r').read(), error_target=1),
       expected=None)
print()
