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

# part 2 complication

test_output = 2858


def interpret_disk_map(m):
  id = 0
  files = {}
  free = []
  j = 0
  for i, x in enumerate(m.strip()):
    x = int(x)
    if i % 2 == 0:
      files[i//2] = ((j, x))
    else:
      free.append((j, x))
    j += x
  return files, free


def compact(files, free):
  for id in reversed(files.keys()):
    start, length = files[id]
    for free_index, free_loc in enumerate(free):
      free_start, free_length = free_loc
      if free_start > start:
        break
      if free_length < length:
        continue
      # free block found!

      # insert into free block, possibly leaving more free space at the end
      new_loc = (free_start, length)
      files[id] = new_loc

      free_start += length
      free_length -= length
      if free_length == 0:
        del free[free_index]
      else:
        free[free_index] = (free_start, free_length)

      # turn old location into free space, possibly coalescing with nearby free blocks
      free.append((start, length))
      free = coalesce(free)
      break

  return files, free


def coalesce(free):
  free.sort()
  result = []
  for start, length in free:
    if result and result[-1][0] + result[-1][1] == start:
      result[-1] = (result[-1][0], result[-1][1] + length)
    else:
      result.append((start, length))
  return result


def checksum(files):
  result = 0
  for id, loc in files.items():
    start, length = loc
    for i in range(length):
      result += (start+i) * id
  return result


def day09(input):
  files, free = interpret_disk_map(input)
  files, free = compact(files, free)
  return checksum(files)


test_output = 2858

assertEqual(test_output, day09(test_input))


print('day09, part 2 answer:')
submit(day09(open('day09_input.txt', 'r').read()),
       expected=None)
print()
