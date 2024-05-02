from common import assertEqual
from common import submit


def enumerate_deltas():
  for dx in [-1, 0, 1]:
    for dy in [-1, 0, 1]:
      yield dx, dy


def is_symbol(c):
  return not c.isdigit() and c != '.'


def day3(input):
  result = 0
  lines = input.splitlines()
  for r, row in enumerate(lines):
    adjacent_symbol = None
    current_number = ''
    for c, col in enumerate(row):
      if col.isdigit():
        current_number += col
        for dx, dy in enumerate_deltas():
          if (r + dx in range(0, len(lines)) and
              c + dy in range(0, len(lines[r])) and
                  is_symbol(lines[r + dx][c + dy])):
            adjacent_symbol = lines[r + dx][c + dy]

      if not col.isdigit() or c == len(lines[r]) - 1:
        if current_number and adjacent_symbol:
          print(f'found part number {current_number} adjacent to symbol {adjacent_symbol}')
          result += int(current_number)
        adjacent_symbol = None
        current_number = ''

  return result


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

assertEqual(test_output, day3(test_input))


print('day3 answer:')
submit(day3(open('day3_input.txt', 'r').read()),
       expected=560670)
print()
