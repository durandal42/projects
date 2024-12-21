from common import assertEqual
from common import submit


def interpret_disk_map(m):
  id = 0
  result = []
  for i, x in enumerate(m.strip()):
    if i % 2 == 0:
      result += [i//2] * int(x)
    else:
      result += ["."] * int(x)
  return result


def interpret_blocks(b):
  return [x if x == "." else int(x) for x in b]


def compact(blocks):
  i, j = 0, len(blocks)-1
  while i < j:
    while blocks[i] != "." and i < j:
      i += 1
    while blocks[j] == "." and i < j:
      j -= 1
    if i < j:
      blocks[i], blocks[j] = blocks[j], blocks[i]
  return blocks


def checksum(blocks):
  return sum(i * x for i, x in enumerate(blocks) if x != ".")


def day09(input):
  blocks = interpret_disk_map(input)
  blocks = compact(blocks)
  return checksum(blocks)


test_input = '''\
2333133121414131402
'''
test_output = 1928

assertEqual(interpret_blocks("00...111...2...333.44.5555.6666.777.888899"),
            interpret_disk_map(test_input))

assertEqual(interpret_blocks("022111222......"), compact(interpret_blocks("0..111....22222")))

assertEqual(test_output, day09(test_input))


print('day09 answer:')
submit(day09(open('day09_input.txt', 'r').read()),
       expected=6330095022244)
print()
