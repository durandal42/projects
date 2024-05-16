from common import assertEqual
from common import submit
import collections


def enumerate_deltas():
  for dx in [-1, 0, 1]:
    for dy in [-1, 0, 1]:
      if dx or dy:
        yield dx, dy


def is_symbol(c):
  return not c.isdigit() and c != '.'


def find_part_numbers(input):
  lines = input.splitlines()
  lines = (['.' * len(lines[0])] +
           [f'.{line}.' for line in lines] +
           ['.' * len(lines[0])])
  for r, row in enumerate(lines):
    adjacent_symbols = set()
    current_number = ''
    for c, col in enumerate(row):
      if col.isdigit():
        current_number += col
        for dr, dc in enumerate_deltas():
          if is_symbol(lines[r + dr][c + dc]):
            adjacent_symbols.add((r + dr, c + dc, lines[r + dr][c + dc]))

      if not col.isdigit() or c == len(lines[r]) - 1:
        if current_number and adjacent_symbols:
          # print(f'found part number {current_number} adjacent to symbols
          # {adjacent_symbols}')
          yield int(current_number), adjacent_symbols
        adjacent_symbols = set()
        current_number = ''


def day03(input):
  return sum(n for n, _ in find_part_numbers(input))


test_input = '''467..114..
...*......
..35..633.
......#...
617*......
.....+.58.
..592.....
......755.
...$.*....
.664.598..
'''
test_output = 4361

assertEqual(test_output, day03(test_input))


print('day03 answer:')
submit(day03(open('day03_input.txt', 'r').read()),
       expected=560670)
print()


# part 2 complication
test_output = 467835


def find_gears(part_numbers):
  symbols_to_adjacent_part_numbers = collections.defaultdict(list)
  for n, symbols in part_numbers:
    for s in symbols:
      symbols_to_adjacent_part_numbers[s].append(n)
  for s, part_numbers in symbols_to_adjacent_part_numbers.items():
    if s[2] == '*' and len(part_numbers) == 2:
      yield s, part_numbers


def day03(input):
  return sum(pn[0] * pn[1] for s, pn in find_gears(find_part_numbers(input)))


assertEqual(test_output, day03(test_input))


print('day03 part2 answer:')
submit(day03(open('day03_input.txt', 'r').read()),
       expected=91622824)
print()
