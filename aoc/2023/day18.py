from common import assertEqual
from common import submit
from common import fill
import re
import collections


def parse_instructions(input):
  result = []
  for line in input.splitlines():
    m = re.match("(\\w) (\\d+) \\(#(\\w+)\\)", line)
    result.append((m.group(1), int(m.group(2)), m.group(3)))
  return result


assertEqual([('R', 6, '70c710')], parse_instructions('R 6 (#70c710)'))

DIRECTIONS = {
    'U': (-1, 0),
    'D': (1, 0),
    'L': (0, -1),
    'R': (0, 1),
}


def dig(instructions):
  h_lines, v_lines = collections.defaultdict(list), collections.defaultdict(list)
  r, c = 0, 0
  for inst in instructions:
    direction, distance, color = inst
    dr, dc = DIRECTIONS[direction]
    dr *= distance
    dc *= distance
    if dr:
      v_lines[c].append(range(min(r, r+dr), max(r, r+dr)+1))
    if dc:
      h_lines[r].append(range(min(c, c+dc), max(c, c+dc)+1))
    r += dr
    c += dc
  return collections.deque(sorted(h_lines.items())), collections.deque(sorted(v_lines.items()))


def bounding_box(h_lines, v_lines):
  min_r = min(r for r, spans in h_lines)
  min_c = min(c for c, spans in v_lines)
  max_r = max(r for r, spans in h_lines)
  max_c = max(c for c, spans in v_lines)
  return (min_r, min_c, max_r+1, max_c+1)


def pretty_print_grid(grid):
  return '\n'.join(''.join(row) for row in grid)


def day18(input, fix=False):
  instructions = parse_instructions(input)
  if fix:
    instructions = [fix_instruction(inst) for inst in instructions]
  # print(instructions)

  h_lines, v_lines = dig(instructions)
  # print(f'h_lines: {h_lines}')
  # print(f'v_lines: {v_lines}')
  bb = bounding_box(h_lines, v_lines)
  # print(bb)

  total = 0
  no_h_lines_on_prev_row = True
  r = bb[0]-1  # manual for loop so we can skip ahead
  while r < bb[2]:
    r += 1
    h_lines_on_this_row = h_lines.popleft()[1] if h_lines and h_lines[0][0] == r else []
    if not h_lines_on_this_row:
      if no_h_lines_on_prev_row:
        # print(f'no h lines on row {r}, should contribute the same as previous row')
        # how *many* rows in a row have no h lines?
        next_row_with_h_lines = h_lines[0][0]
        total += total_this_row * (next_row_with_h_lines - r)
        r = next_row_with_h_lines - 1
        continue
      else:
        no_h_lines_on_prev_row = True
    else:
      no_h_lines_on_prev_row = False
    # print(f'scanning row {r}')
    inside = False
    total_this_row = 0
    v_lines_this_row = collections.deque(v_lines)
    prev_v_line_direction = 0
    no_v_lines_on_prev_col = True
    c = bb[1]-1  # manual for loop so we can skip ahead
    while c < bb[3]:
      c += 1
      # print(f'looking at col {c}')
      v_lines_on_this_col = v_lines_this_row.popleft()[1] if v_lines_this_row and v_lines_this_row[0][0] == c else []
      if not v_lines_on_this_col:
        if no_v_lines_on_prev_col:
          # how *many* cols in a row have no v lines?
          # TODO: this is the hot spot, binary search or merge lists or something
          # print(v_lines_this_row)
          next_col_with_v_lines = v_lines_this_row[0][0]
          total_this_row += total_this_col * (next_col_with_v_lines - c)
          c = next_col_with_v_lines - 1
          continue
        else:
          no_v_lines_on_prev_col = True
      else:
        no_v_lines_on_prev_col = False

      total_this_col = 0
      # print(v_lines_on_this_col)
      on_a_v_line = any(r in v_line for v_line in v_lines_on_this_col)
      on_a_h_line = any(c in h_line for h_line in h_lines_on_this_row)
      # print(f'on_a_v_line: {on_a_v_line}')
      # print(f'on_a_h_line: {on_a_h_line}')
      if on_a_v_line and not on_a_h_line:
        # easy case, crossing a vertical line
        inside = not inside
      if on_a_h_line and not on_a_v_line:
        # nothing to do, but sanity check our corner-handling
        assert prev_v_line_direction
      if on_a_v_line and on_a_h_line:
        # print("found a corner!")
        # on a corner!
        on_bot_of_v_line = not any(r+1 in v_line for v_line in v_lines_on_this_col)
        on_top_of_v_line = not any(r-1 in v_line for v_line in v_lines_on_this_col)
        # print(f'on_top_of_v_line: {on_top_of_v_line}')
        # print(f'on_bot_of_v_line: {on_bot_of_v_line}')
        assert on_bot_of_v_line != on_top_of_v_line
        if not prev_v_line_direction:
          prev_v_line_direction = -1 if on_bot_of_v_line else 1
        else:
          if (prev_v_line_direction < 0) == on_top_of_v_line:
            inside = not inside
            # print('toggled inside due to pair of opposed corners')
          prev_v_line_direction = 0
        # print(f'prev_line_direction: {prev_v_line_direction}')
      if (on_a_h_line or on_a_v_line):
        total_this_col += 1
      elif inside:
        total_this_col += 1
      total_this_row += total_this_col
    # print(f'interior_total on row {r}: {interior_total_this_row}')
    total += total_this_row

  return total


test_input = '''\
R 6 (#70c710)
D 5 (#0dc571)
L 2 (#5713f0)
D 2 (#d2c081)
R 2 (#59c680)
D 2 (#411b91)
L 5 (#8ceee2)
U 2 (#caa173)
L 1 (#1b58a2)
U 2 (#caa171)
R 2 (#7807d2)
U 3 (#a77fa3)
L 2 (#015232)
U 2 (#7a21e3)
'''
test_output = 62

assertEqual(test_output, day18(test_input))


print('day18 answer:')
submit(day18(open('day18_input.txt', 'r').read()),
       expected=48400)
print()

# part2 complication
test_output = 952408144115


def fix_instruction(inst):
  return ('RDLU'[int(inst[2][-1])], int(inst[2][:-1], 16), None)


assertEqual(('R', 461937, None),
            fix_instruction((None, None, '70c710')))

assertEqual(test_output, day18(test_input, fix=True))

print('day18, part2 answer:')
submit(day18(open('day18_input.txt', 'r').read(), fix=True),
       expected=72811019847283)
print()
